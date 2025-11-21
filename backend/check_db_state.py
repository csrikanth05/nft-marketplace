from app.database import SessionLocal
from app.models.models import User, NFT, Listing, Auction, Bid

def check_db():
    db = SessionLocal()
    try:
        print("\n=== DATABASE STATE CHECK ===")
        
        # Users
        users = db.query(User).all()
        print(f"\nUsers ({len(users)}):")
        for u in users:
            print(f" - {u.address}")

        # NFTs
        nfts = db.query(NFT).all()
        print(f"\nNFTs ({len(nfts)}):")
        for n in nfts:
            print(f" - Token {n.token_id} | Owner: {n.owner_address} | Listed: {n.is_listed}")

        # Listings
        listings = db.query(Listing).all()
        print(f"\nListings ({len(listings)}):")
        for l in listings:
            print(f" - ID {l.listing_id} | NFT {l.nft_id} | Active: {l.active} | Sold: {l.sold}")

        # Auctions
        auctions = db.query(Auction).all()
        print(f"\nAuctions ({len(auctions)}):")
        for a in auctions:
            print(f" - ID {a.auction_id} | NFT {a.nft_id} | Active: {a.active} | Highest Bid: {a.highest_bid_eth} ETH")

        # Bids
        bids = db.query(Bid).all()
        print(f"\nBids ({len(bids)}):")
        for b in bids:
            print(f" - Auction {b.auction_id} | Bidder: {b.bidder_address} | Amount: {b.amount_eth} ETH")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_db()
