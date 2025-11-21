import asyncio
import time
from app.services.indexer_service import indexer_service
from app.database import SessionLocal
from app.models.models import NFT, Listing, Auction, User

def test_indexer():
    print("="*60)
    print("TESTING BLOCKCHAIN INDEXER")
    print("="*60)
    
    # 1. Run the sync manually for a few seconds
    print("Running indexer sync...")
    
    # Create a new event loop for testing
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Run sync once (we modify the service slightly for test or just run it for a bit)
    # Since sync_events is an infinite loop, we can't await it directly in a test without timeout
    # Instead, we'll call the process methods directly for the latest blocks
    
    try:
        db = SessionLocal()
        current_block = indexer_service.w3.eth.block_number
        print(f"Current block: {current_block}")
        
        # Process all events from block 0 to current
        print("Processing NFT events...")
        loop.run_until_complete(indexer_service.process_nft_events(db, 0, current_block))
        
        print("Processing Marketplace events...")
        loop.run_until_complete(indexer_service.process_marketplace_events(db, 0, current_block))
        
        print("Processing Auction events...")
        loop.run_until_complete(indexer_service.process_auction_events(db, 0, current_block))
        
        # Verify Data
        print("\nVerifying Indexed Data:")
        
        # Check Users
        users = db.query(User).all()
        print(f"Users found: {len(users)}")
        for user in users:
            print(f" - {user.address}")
            
        # Check NFTs
        nfts = db.query(NFT).all()
        print(f"NFTs found: {len(nfts)}")
        for nft in nfts:
            print(f" - Token {nft.token_id} (Owner: {nft.owner_address})")
            
        # Check Listings
        listings = db.query(Listing).all()
        print(f"Listings found: {len(listings)}")
        for listing in listings:
            print(f" - Listing {listing.listing_id} (Active: {listing.active})")
            
        # Check Auctions
        auctions = db.query(Auction).all()
        print(f"Auctions found: {len(auctions)}")
        for auction in auctions:
            print(f" - Auction {auction.auction_id} (Active: {auction.active})")
            
        db.close()
        print("\n✅ Indexer Test Completed Successfully")
        
    except Exception as e:
        print(f"\n❌ Indexer Test Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_indexer()
