from web3 import Web3
from .web3_service import web3_service
from ..config import settings
from typing import List, Dict, Any


class AuctionService:
    def __init__(self):
        self.contract = web3_service.auction_contract
        self.w3 = web3_service.w3
    
    def create_auction(
        self,
        nft_contract_address: str,
        token_id: int,
        start_time: int,
        end_time: int,
        reserve_price_eth: float,
        from_address: str,
        private_key: str
    ) -> Dict[str, Any]:
        """Create a new auction"""
        print(f"\n=== CREATE AUCTION DEBUG ===")
        print(f"Initial start_time: {start_time}")
        print(f"Initial end_time: {end_time}")
        
        reserve_price_wei = self.w3.to_wei(reserve_price_eth, 'ether')
        
        # Check if auction contract is approved to transfer this NFT
        # We use the NFT contract from web3_service (assuming it's the platform's NFT)
        # If supporting external NFTs, we'd need to load that contract ABI dynamically
        nft_contract = web3_service.nft_contract
        auction_contract_address = settings.AUCTION_CONTRACT_ADDRESS
        
        # Check current approval
        approved_address = nft_contract.functions.getApproved(token_id).call()
        is_approved_for_all = nft_contract.functions.isApprovedForAll(
            Web3.to_checksum_address(from_address),
            Web3.to_checksum_address(auction_contract_address)
        ).call()
        
        if approved_address != auction_contract_address and not is_approved_for_all:
            # Need to approve
            print(f"Approving Auction contract for token {token_id}...")
            approve_txn = nft_contract.functions.approve(
                Web3.to_checksum_address(auction_contract_address),
                token_id
            ).build_transaction({
                'from': Web3.to_checksum_address(from_address)
            })
            
            # Send approval transaction
            approve_hash = web3_service.send_transaction(approve_txn, private_key)
            
            # Wait for approval to be mined
            self.w3.eth.wait_for_transaction_receipt(approve_hash)
            print(f"Approval confirmed: {approve_hash}")
        
        # ALWAYS recalculate start_time right before creating auction
        # This accounts for time passing during approval OR just network delay
        current_block = self.w3.eth.get_block('latest')
        current_time = current_block['timestamp']
        print(f"Current blockchain time: {current_time}")
        
        # If start_time is now in the past or doesn't have enough buffer, adjust it
        # We need a LARGE buffer to account for Ganache's auto-mining behavior
        min_required_start = current_time + 120  # Increased to 120 seconds
        print(f"Minimum required start_time: {min_required_start}")
        
        if start_time < min_required_start:
            duration = end_time - start_time
            start_time = min_required_start
            end_time = start_time + duration
            print(f"⚠️  ADJUSTED start_time to {start_time}, end_time to {end_time}")
        else:
            print(f"✓ start_time {start_time} is valid (>= {min_required_start})")
        
        print(f"Final start_time being sent to contract: {start_time}")
        print(f"Final end_time being sent to contract: {end_time}")
        print(f"=== END DEBUG ===\n")

        # Build the transaction with the adjusted times
        transaction = self.contract.functions.createAuction(
            Web3.to_checksum_address(nft_contract_address),
            token_id,
            start_time,
            end_time,
            reserve_price_wei
        ).build_transaction({
            'from': Web3.to_checksum_address(from_address)
        })
        
        # Log the transaction data to verify the values
        print(f"Transaction data check - start_time in tx: {start_time}, end_time in tx: {end_time}")
        
        # Get blockchain time right before sending
        pre_send_block = self.w3.eth.get_block('latest')
        pre_send_time = pre_send_block['timestamp']
        print(f"Blockchain time RIGHT before sending tx: {pre_send_time}")
        print(f"Time difference: start_time - current_time = {start_time - pre_send_time} seconds")
        
        tx_hash = web3_service.send_transaction(transaction, private_key)
        
        # Get blockchain time after transaction is mined
        post_send_block = self.w3.eth.get_block('latest')
        post_send_time = post_send_block['timestamp']
        print(f"Blockchain time AFTER tx mined: {post_send_time}")
        print(f"Time advanced during mining: {post_send_time - pre_send_time} seconds")
        
        # Get auction ID from event
        receipt = self.w3.eth.get_transaction_receipt(tx_hash)
        auction_created_event = self.contract.events.AuctionCreated().process_receipt(receipt)
        auction_id = auction_created_event[0]['args']['auctionId'] if auction_created_event else None
        
        return {
            "transaction_hash": tx_hash,
            "auction_id": auction_id,
            "token_id": token_id,
            "reserve_price_eth": reserve_price_eth
        }
    
    def place_bid(
        self,
        auction_id: int,
        bid_amount_eth: float,
        from_address: str,
        private_key: str
    ) -> str:
        """Place a bid on an auction"""
        bid_amount_wei = self.w3.to_wei(bid_amount_eth, 'ether')
        
        transaction = self.contract.functions.placeBid(auction_id).build_transaction({
            'from': Web3.to_checksum_address(from_address),
            'value': bid_amount_wei
        })
        
        return web3_service.send_transaction(transaction, private_key)
    
    def end_auction(
        self,
        auction_id: int,
        from_address: str,
        private_key: str
    ) -> str:
        """End an auction"""
        transaction = self.contract.functions.endAuction(auction_id).build_transaction({
            'from': Web3.to_checksum_address(from_address)
        })
        
        return web3_service.send_transaction(transaction, private_key)
    
    def cancel_auction(
        self,
        auction_id: int,
        from_address: str,
        private_key: str
    ) -> str:
        """Cancel an auction (only if no bids)"""
        transaction = self.contract.functions.cancelAuction(auction_id).build_transaction({
            'from': Web3.to_checksum_address(from_address)
        })
        
        return web3_service.send_transaction(transaction, private_key)
    
    def withdraw_bid(
        self,
        auction_id: int,
        from_address: str,
        private_key: str
    ) -> str:
        """Withdraw refunded bid"""
        transaction = self.contract.functions.withdraw(auction_id).build_transaction({
            'from': Web3.to_checksum_address(from_address)
        })
        
        return web3_service.send_transaction(transaction, private_key)
    
    def get_auction(self, auction_id: int) -> Dict[str, Any]:
        """Get auction details"""
        auction = self.contract.functions.getAuction(auction_id).call()
        
        return {
            "auction_id": auction_id,
            "seller": auction[0],
            "nft_contract": auction[1],
            "token_id": auction[2],
            "start_time": auction[3],
            "end_time": auction[4],
            "reserve_price_wei": auction[5],
            "reserve_price_eth": self.w3.from_wei(auction[5], 'ether'),
            "highest_bidder": auction[6],
            "highest_bid_wei": auction[7],
            "highest_bid_eth": self.w3.from_wei(auction[7], 'ether'),
            "active": auction[8],
            "ended": auction[9]
        }
    
    def get_pending_return(self, auction_id: int, bidder_address: str) -> float:
        """Get pending return amount for a bidder"""
        amount_wei = self.contract.functions.pendingReturns(
            auction_id,
            Web3.to_checksum_address(bidder_address)
        ).call()
        return self.w3.from_wei(amount_wei, 'ether')
    
    def get_current_auction_id(self) -> int:
        """Get the current auction ID counter"""
        return self.contract.functions.getCurrentAuctionId().call()
    
    def get_all_active_auctions(self) -> List[Dict[str, Any]]:
        """Get all active auctions (only for NFTs that exist in database)"""
        from ..database import SessionLocal
        from ..models.models import NFT
        
        current_id = self.get_current_auction_id()
        active_auctions = []
        
        # Get DB session to check NFT existence
        db = SessionLocal()
        
        try:
            for auction_id in range(1, current_id + 1):
                try:
                    auction = self.get_auction(auction_id)
                    if auction['active'] and not auction['ended']:
                        # Check if NFT exists in database
                        nft_exists = db.query(NFT).filter(
                            NFT.contract_address == auction['nft_contract'],
                            NFT.token_id == auction['token_id']
                        ).first()
                        
                        # Only include auction if NFT exists in DB
                        if nft_exists:
                            active_auctions.append(auction)
                except:
                    continue
        finally:
            db.close()
        
        return active_auctions


# Global instance
auction_service = AuctionService()
