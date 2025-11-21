import asyncio
import time
from web3 import Web3
from sqlalchemy.orm import Session
from ..database import SessionLocal, engine, Base
from ..models.models import User, NFT, Listing, Auction, Bid, EventProcessed
from .web3_service import web3_service
from ..config import settings

class IndexerService:
    def __init__(self):
        self.w3 = web3_service.w3
        self.nft_contract = web3_service.nft_contract
        self.marketplace_contract = web3_service.marketplace_contract
        self.auction_contract = web3_service.auction_contract
        
        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)

    def get_db(self):
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def get_last_processed_block(self, db: Session, contract_name: str) -> int:
        record = db.query(EventProcessed).filter(EventProcessed.contract_name == contract_name).first()
        if record:
            return record.last_processed_block
        return 0

    def update_last_processed_block(self, db: Session, contract_name: str, block_number: int):
        record = db.query(EventProcessed).filter(EventProcessed.contract_name == contract_name).first()
        if not record:
            record = EventProcessed(contract_name=contract_name, last_processed_block=block_number)
            db.add(record)
        else:
            record.last_processed_block = block_number
        db.commit()

    def get_or_create_user(self, db: Session, address: str) -> User:
        user = db.query(User).filter(User.address == address).first()
        if not user:
            user = User(address=address)
            db.add(user)
            db.commit()
            db.refresh(user)
        return user

    async def process_nft_events(self, db: Session, from_block: int, to_block: int):
        # NFTMinted Event
        events = self.nft_contract.events.NFTMinted().get_logs(fromBlock=from_block, toBlock=to_block)
        for event in events:
            args = event['args']
            token_id = args['tokenId']
            to_address = args['creator'] # Event param is named 'creator'
            token_uri = args['tokenURI']
            
            self.get_or_create_user(db, to_address)
            
            # Check if NFT exists
            nft = db.query(NFT).filter(NFT.token_id == token_id, NFT.contract_address == settings.NFT_CONTRACT_ADDRESS).first()
            if not nft:
                nft = NFT(
                    token_id=token_id,
                    contract_address=settings.NFT_CONTRACT_ADDRESS,
                    owner_address=to_address,
                    creator_address=to_address, # Initial creator is the minter
                    token_uri=token_uri
                )
                db.add(nft)
            db.commit()
            print(f"Indexed NFTMinted: Token {token_id} to {to_address}")

        # Transfer Event
        events = self.nft_contract.events.Transfer().get_logs(fromBlock=from_block, toBlock=to_block)
        for event in events:
            args = event['args']
            token_id = args['tokenId']
            from_address = args['from']
            to_address = args['to']
            
            self.get_or_create_user(db, to_address)
            
            nft = db.query(NFT).filter(NFT.token_id == token_id, NFT.contract_address == settings.NFT_CONTRACT_ADDRESS).first()
            if nft:
                nft.owner_address = to_address
                db.commit()
                print(f"Indexed Transfer: Token {token_id} from {from_address} to {to_address}")

    async def process_marketplace_events(self, db: Session, from_block: int, to_block: int):
        # NFTListed
        events = self.marketplace_contract.events.NFTListed().get_logs(fromBlock=from_block, toBlock=to_block)
        for event in events:
            args = event['args']
            listing_id = args['listingId']
            seller = args['seller']
            nft_contract = args['nftContract']
            token_id = args['tokenId']
            price = args['price']
            
            self.get_or_create_user(db, seller)
            
            nft = db.query(NFT).filter(NFT.token_id == token_id, NFT.contract_address == nft_contract).first()
            if nft:
                listing = Listing(
                    listing_id=listing_id,
                    nft_id=nft.id,
                    seller_address=seller,
                    price_wei=str(price),
                    price_eth=float(self.w3.from_wei(price, 'ether')),
                    active=True
                )
                db.add(listing)
                nft.is_listed = True
                db.commit()
                print(f"Indexed NFTListed: Listing {listing_id} for Token {token_id}")

        # NFTSold
        events = self.marketplace_contract.events.NFTSold().get_logs(fromBlock=from_block, toBlock=to_block)
        for event in events:
            args = event['args']
            listing_id = args['listingId']
            buyer = args['buyer']
            
            self.get_or_create_user(db, buyer)
            
            listing = db.query(Listing).filter(Listing.listing_id == listing_id).first()
            if listing:
                listing.active = False
                listing.sold = True
                
                if listing.nft:
                    listing.nft.is_listed = False
                    listing.nft.owner_address = buyer
                
                db.commit()
                print(f"Indexed NFTSold: Listing {listing_id} by {buyer}")

        # ListingCancelled
        events = self.marketplace_contract.events.ListingCancelled().get_logs(fromBlock=from_block, toBlock=to_block)
        for event in events:
            args = event['args']
            listing_id = args['listingId']
            
            listing = db.query(Listing).filter(Listing.listing_id == listing_id).first()
            if listing:
                listing.active = False
                listing.cancelled = True
                if listing.nft:
                    listing.nft.is_listed = False
                db.commit()
                print(f"Indexed ListingCancelled: Listing {listing_id}")

    async def process_auction_events(self, db: Session, from_block: int, to_block: int):
        # AuctionCreated
        events = self.auction_contract.events.AuctionCreated().get_logs(fromBlock=from_block, toBlock=to_block)
        for event in events:
            args = event['args']
            auction_id = args['auctionId']
            seller = args['seller']
            nft_contract = args['nftContract']
            token_id = args['tokenId']
            start_time = args['startTime']
            end_time = args['endTime']
            reserve_price = args['reservePrice']
            
            self.get_or_create_user(db, seller)
            
            nft = db.query(NFT).filter(NFT.token_id == token_id, NFT.contract_address == nft_contract).first()
            if nft:
                auction = Auction(
                    auction_id=auction_id,
                    nft_id=nft.id,
                    seller_address=seller,
                    start_time=start_time,
                    end_time=end_time,
                    reserve_price_wei=str(reserve_price),
                    reserve_price_eth=float(self.w3.from_wei(reserve_price, 'ether')),
                    active=True
                )
                db.add(auction)
                nft.is_listed = True # Using is_listed for auction as well
                db.commit()
                print(f"Indexed AuctionCreated: Auction {auction_id} for Token {token_id}")

        # BidPlaced
        events = self.auction_contract.events.BidPlaced().get_logs(fromBlock=from_block, toBlock=to_block)
        for event in events:
            args = event['args']
            auction_id = args['auctionId']
            bidder = args['bidder']
            amount = args['amount']
            
            self.get_or_create_user(db, bidder)
            
            auction = db.query(Auction).filter(Auction.auction_id == auction_id).first()
            if auction:
                auction.highest_bid_wei = str(amount)
                auction.highest_bid_eth = float(self.w3.from_wei(amount, 'ether'))
                auction.highest_bidder_address = bidder
                
                bid = Bid(
                    auction_id=auction.id,
                    bidder_address=bidder,
                    amount_wei=str(amount),
                    amount_eth=float(self.w3.from_wei(amount, 'ether')),
                    timestamp=int(time.time()) # Approximate timestamp
                )
                db.add(bid)
                db.commit()
                print(f"Indexed BidPlaced: Auction {auction_id} by {bidder} amount {amount}")

        # AuctionEnded
        events = self.auction_contract.events.AuctionEnded().get_logs(fromBlock=from_block, toBlock=to_block)
        for event in events:
            args = event['args']
            auction_id = args['auctionId']
            winner = args['winner']
            amount = args['amount']
            
            if winner != "0x0000000000000000000000000000000000000000":
                self.get_or_create_user(db, winner)
            
            auction = db.query(Auction).filter(Auction.auction_id == auction_id).first()
            if auction:
                auction.active = False
                auction.ended = True
                
                if auction.nft:
                    auction.nft.is_listed = False
                    if winner != "0x0000000000000000000000000000000000000000":
                        auction.nft.owner_address = winner
                
                db.commit()
                print(f"Indexed AuctionEnded: Auction {auction_id} Winner {winner}")

        # AuctionCancelled
        events = self.auction_contract.events.AuctionCancelled().get_logs(fromBlock=from_block, toBlock=to_block)
        for event in events:
            args = event['args']
            auction_id = args['auctionId']
            
            auction = db.query(Auction).filter(Auction.auction_id == auction_id).first()
            if auction:
                auction.active = False
                auction.cancelled = True
                if auction.nft:
                    auction.nft.is_listed = False
                db.commit()
                print(f"Indexed AuctionCancelled: Auction {auction_id}")

    async def sync_events(self):
        """Main polling loop"""
        print("Starting Indexer Service...")
        while True:
            try:
                current_block = self.w3.eth.block_number
                db = SessionLocal()
                
                # Sync NFT Events
                last_nft_block = self.get_last_processed_block(db, "NFTContract")
                if last_nft_block < current_block:
                    await self.process_nft_events(db, last_nft_block + 1, current_block)
                    self.update_last_processed_block(db, "NFTContract", current_block)
                
                # Sync Marketplace Events
                last_market_block = self.get_last_processed_block(db, "Marketplace")
                if last_market_block < current_block:
                    await self.process_marketplace_events(db, last_market_block + 1, current_block)
                    self.update_last_processed_block(db, "Marketplace", current_block)
                
                # Sync Auction Events
                last_auction_block = self.get_last_processed_block(db, "Auction")
                if last_auction_block < current_block:
                    await self.process_auction_events(db, last_auction_block + 1, current_block)
                    self.update_last_processed_block(db, "Auction", current_block)
                
                db.close()
                
            except Exception as e:
                print(f"Error in indexer loop: {e}")
            
            await asyncio.sleep(5) # Poll every 5 seconds

indexer_service = IndexerService()
