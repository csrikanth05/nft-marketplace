import requests
import json

BASE_URL = "http://localhost:8000/api/v1/db"

def test_database_api():
    print("="*60)
    print("TESTING DATABASE API ENDPOINTS")
    print("="*60)
    
    try:
        # Test 1: Get all NFTs
        print("\n1. Testing GET /nfts")
        response = requests.get(f"{BASE_URL}/nfts")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        nfts = response.json()
        print(f"   ✓ Found {len(nfts)} NFTs")
        if nfts:
            print(f"   Sample: Token {nfts[0]['token_id']} owned by {nfts[0]['owner_address']}")
        
        # Test 2: Get NFT by token ID
        if nfts:
            token_id = nfts[0]['token_id']
            print(f"\n2. Testing GET /nfts/{token_id}")
            response = requests.get(f"{BASE_URL}/nfts/{token_id}")
            assert response.status_code == 200
            nft = response.json()
            print(f"   ✓ NFT {token_id}: Owner={nft['owner_address']}, Listed={nft['is_listed']}")
        
        # Test 3: Get NFTs by owner
        if nfts:
            owner = nfts[0]['owner_address']
            print(f"\n3. Testing GET /users/{owner}/nfts")
            response = requests.get(f"{BASE_URL}/users/{owner}/nfts")
            assert response.status_code == 200
            owner_nfts = response.json()
            print(f"   ✓ User owns {len(owner_nfts)} NFTs")
        
        # Test 4: Get all active listings
        print("\n4. Testing GET /listings (active only)")
        response = requests.get(f"{BASE_URL}/listings?active_only=true")
        assert response.status_code == 200
        listings = response.json()
        print(f"   ✓ Found {len(listings)} active listings")
        
        # Test 5: Get all listings (including inactive)
        print("\n5. Testing GET /listings (all)")
        response = requests.get(f"{BASE_URL}/listings?active_only=false")
        assert response.status_code == 200
        all_listings = response.json()
        print(f"   ✓ Found {len(all_listings)} total listings")
        
        # Test 6: Get listing by ID
        if all_listings:
            listing_id = all_listings[0]['listing_id']
            print(f"\n6. Testing GET /listings/{listing_id}")
            response = requests.get(f"{BASE_URL}/listings/{listing_id}")
            assert response.status_code == 200
            listing = response.json()
            print(f"   ✓ Listing {listing_id}: Price={listing['price_eth']} ETH, Active={listing['active']}")
        
        # Test 7: Get all active auctions
        print("\n7. Testing GET /auctions (active only)")
        response = requests.get(f"{BASE_URL}/auctions?active_only=true")
        assert response.status_code == 200
        auctions = response.json()
        print(f"   ✓ Found {len(auctions)} active auctions")
        
        # Test 8: Get auction by ID with bids
        if auctions:
            auction_id = auctions[0]['auction_id']
            print(f"\n8. Testing GET /auctions/{auction_id}")
            response = requests.get(f"{BASE_URL}/auctions/{auction_id}")
            assert response.status_code == 200
            auction = response.json()
            print(f"   ✓ Auction {auction_id}: Reserve={auction['reserve_price_eth']} ETH, Bids={len(auction['bids'])}")
            if auction['bids']:
                print(f"   Highest bid: {auction['highest_bid_eth']} ETH")
        
        # Test 9: Get user profile
        if nfts:
            user_address = nfts[0]['owner_address']
            print(f"\n9. Testing GET /users/{user_address}")
            response = requests.get(f"{BASE_URL}/users/{user_address}")
            assert response.status_code == 200
            profile = response.json()
            stats = profile['stats']
            print(f"   ✓ User Profile:")
            print(f"     - NFTs owned: {stats['nfts_owned']}")
            print(f"     - Active listings: {stats['active_listings']}")
            print(f"     - Active auctions: {stats['active_auctions']}")
            print(f"     - Total bids: {stats['total_bids']}")
        
        # Test 10: Get all users
        print("\n10. Testing GET /users")
        response = requests.get(f"{BASE_URL}/users")
        assert response.status_code == 200
        users = response.json()
        print(f"   ✓ Found {len(users)} users")
        
        # Test 11: Pagination
        print("\n11. Testing pagination (limit=1)")
        response = requests.get(f"{BASE_URL}/nfts?limit=1")
        assert response.status_code == 200
        limited_nfts = response.json()
        assert len(limited_nfts) <= 1
        print(f"   ✓ Pagination working: returned {len(limited_nfts)} NFT(s)")
        
        # Test 12: 404 for non-existent NFT
        print("\n12. Testing 404 for non-existent NFT")
        response = requests.get(f"{BASE_URL}/nfts/99999")
        assert response.status_code == 404
        print(f"   ✓ Correctly returns 404 for non-existent NFT")
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED")
        print("="*60)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("\nMake sure the backend server is running on http://localhost:8000")
    print("Press Enter to start tests...")
    input()
    test_database_api()
