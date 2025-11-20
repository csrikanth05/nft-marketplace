import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
HEALTH_URL = "http://localhost:8000/health"

# Contract addresses from deployment
NFT_CONTRACT = "0x7D89BCf357cD820A6A88D1ac9266e47f704734Ba"
MARKETPLACE_CONTRACT = "0xBF4e7AeB704F2249b48ACec5037A6a43525B13a6"
AUCTION_CONTRACT = "0xAA9390E163Ff8Dd7Ddc5913065A47115c35eF712"

# Ganache account details (UPDATE THESE!)
ACCOUNT_1_ADDRESS = "0x379f3Fe5316cf87c988B8C0C47D8A4f4049d5add"
ACCOUNT_1_PRIVATE_KEY = "0x30ecae152f29aaef2e4a71ef692e984a9633865a342b96888333ba3edf2dfac7"

ACCOUNT_2_ADDRESS = "0x9eC4ae245fcEF074f8a52bBf9E56FE4fb3d75BE5"
ACCOUNT_2_PRIVATE_KEY = "0x3a8b1aec539d28b028ec8b2e1459bdb1e4778d28708fa19ed2d19cae156ec0b3"

# Test results
test_results = []


def log_test(test_name, passed, message=""):
    """Log test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    result = f"{status} - {test_name}"
    if message:
        result += f": {message}"
    print(result)
    test_results.append({"test": test_name, "passed": passed, "message": message})


def test_health_check():
    """Test 1: Health Check"""
    print("\n" + "="*60)
    print("Test 1: Health Check")
    print("="*60)
    
    try:
        response = requests.get(HEALTH_URL)
        data = response.json()
        
        passed = response.status_code == 200 and data.get("status") == "healthy"
        log_test("Health Check", passed, f"Status: {data.get('status')}")
        return passed
    except Exception as e:
        log_test("Health Check", False, str(e))
        return False


def test_mint_nft():
    """Test 2: Mint NFT"""
    print("\n" + "="*60)
    print("Test 2: Mint NFT")
    print("="*60)
    
    try:
        payload = {
            "to_address": ACCOUNT_1_ADDRESS,
            "token_uri": "ipfs://QmTestHash123",
            "royalty_receiver": ACCOUNT_1_ADDRESS,
            "royalty_fee": 500,
            "from_address": ACCOUNT_1_ADDRESS,
            "private_key": ACCOUNT_1_PRIVATE_KEY
        }
        
        response = requests.post(f"{BASE_URL}/nft/mint", json=payload)
        data = response.json()
        
        if response.status_code == 200:
            token_id = data.get("token_id")
            tx_hash = data.get("transaction_hash")
            log_test("Mint NFT", True, f"Token ID: {token_id}, TX: {tx_hash[:10]}...")
            return token_id
        else:
            log_test("Mint NFT", False, data.get("detail", "Unknown error"))
            return None
    except Exception as e:
        log_test("Mint NFT", False, str(e))
        return None


def test_get_nft_details(token_id):
    """Test 3: Get NFT Details"""
    print("\n" + "="*60)
    print(f"Test 3: Get NFT Details (Token {token_id})")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/nft/{token_id}")
        data = response.json()
        
        if response.status_code == 200:
            owner = data.get("owner")
            creator = data.get("creator")
            passed = owner == ACCOUNT_1_ADDRESS and creator == ACCOUNT_1_ADDRESS
            log_test("Get NFT Details", passed, f"Owner: {owner[:10]}..., Creator: {creator[:10]}...")
            return passed
        else:
            log_test("Get NFT Details", False, data.get("detail", "Unknown error"))
            return False
    except Exception as e:
        log_test("Get NFT Details", False, str(e))
        return False


def test_get_nfts_by_owner():
    """Test 4: Get NFTs by Owner"""
    print("\n" + "="*60)
    print("Test 4: Get NFTs by Owner")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/nft/owner/{ACCOUNT_1_ADDRESS}")
        data = response.json()
        
        if response.status_code == 200:
            token_count = len(data)
            log_test("Get NFTs by Owner", True, f"Found {token_count} token(s)")
            return True
        else:
            log_test("Get NFTs by Owner", False, str(data))
            return False
    except Exception as e:
        log_test("Get NFTs by Owner", False, str(e))
        return False


def test_get_total_supply():
    """Test 5: Get Total Supply"""
    print("\n" + "="*60)
    print("Test 5: Get Total Supply")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/nft/stats/total-supply")
        data = response.json()
        
        if response.status_code == 200:
            total = data.get("total_supply")
            log_test("Get Total Supply", True, f"Total supply: {total}")
            return True
        else:
            log_test("Get Total Supply", False, str(data))
            return False
    except Exception as e:
        log_test("Get Total Supply", False, str(e))
        return False


def test_list_nft(token_id):
    """Test 6: List NFT on Marketplace"""
    print("\n" + "="*60)
    print(f"Test 6: List NFT {token_id} on Marketplace")
    print("="*60)
    print("⚠️  NOTE: You must approve the marketplace contract first!")
    print("   Run in Truffle console:")
    print(f"   await nft.approve('{MARKETPLACE_CONTRACT}', {token_id}, {{from: '{ACCOUNT_1_ADDRESS}'}})")
    input("   Press Enter after approving...")
    
    try:
        payload = {
            "nft_contract_address": NFT_CONTRACT,
            "token_id": token_id,
            "price_eth": 1.5,
            "from_address": ACCOUNT_1_ADDRESS,
            "private_key": ACCOUNT_1_PRIVATE_KEY
        }
        
        response = requests.post(f"{BASE_URL}/marketplace/list", json=payload)
        data = response.json()
        
        if response.status_code == 200:
            listing_id = data.get("listing_id")
            log_test("List NFT on Marketplace", True, f"Listing ID: {listing_id}")
            return listing_id
        else:
            log_test("List NFT on Marketplace", False, data.get("detail", "Unknown error"))
            return None
    except Exception as e:
        log_test("List NFT on Marketplace", False, str(e))
        return None


def test_get_listing(listing_id):
    """Test 7: Get Listing Details"""
    print("\n" + "="*60)
    print(f"Test 7: Get Listing {listing_id} Details")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/marketplace/listing/{listing_id}")
        data = response.json()
        
        if response.status_code == 200:
            active = data.get("active")
            price = data.get("price_eth")
            log_test("Get Listing Details", True, f"Active: {active}, Price: {price} ETH")
            return True
        else:
            log_test("Get Listing Details", False, data.get("detail", "Unknown error"))
            return False
    except Exception as e:
        log_test("Get Listing Details", False, str(e))
        return False


def test_get_all_listings():
    """Test 8: Get All Active Listings"""
    print("\n" + "="*60)
    print("Test 8: Get All Active Listings")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/marketplace/listings")
        data = response.json()
        
        if response.status_code == 200:
            count = len(data)
            log_test("Get All Active Listings", True, f"Found {count} active listing(s)")
            return True
        else:
            log_test("Get All Active Listings", False, str(data))
            return False
    except Exception as e:
        log_test("Get All Active Listings", False, str(e))
        return False


def test_get_platform_fee():
    """Test 9: Get Platform Fee"""
    print("\n" + "="*60)
    print("Test 9: Get Platform Fee")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/marketplace/stats/platform-fee")
        data = response.json()
        
        if response.status_code == 200:
            fee_percent = data.get("platform_fee_percent")
            log_test("Get Platform Fee", True, f"Platform fee: {fee_percent}%")
            return True
        else:
            log_test("Get Platform Fee", False, str(data))
            return False
    except Exception as e:
        log_test("Get Platform Fee", False, str(e))
        return False


def print_summary():
    """Print test summary"""
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    total = len(test_results)
    passed = sum(1 for r in test_results if r["passed"])
    failed = total - passed
    
    print(f"\nTotal Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Success Rate: {(passed/total*100):.1f}%")
    
    if failed > 0:
        print("\nFailed Tests:")
        for result in test_results:
            if not result["passed"]:
                print(f"  - {result['test']}: {result['message']}")


def main():
    """Run all tests"""
    print("="*60)
    print("NFT MARKETPLACE API - AUTOMATED TESTS")
    print("="*60)
    print(f"\nBase URL: {BASE_URL}")
    print(f"NFT Contract: {NFT_CONTRACT}")
    print(f"Marketplace Contract: {MARKETPLACE_CONTRACT}")
    print(f"Auction Contract: {AUCTION_CONTRACT}")
    print(f"\nAccount 1: {ACCOUNT_1_ADDRESS}")
    
    # Check if private keys are set
    if "YOUR_GANACHE" in ACCOUNT_1_PRIVATE_KEY:
        print("\n❌ ERROR: Please update ACCOUNT_1_PRIVATE_KEY in the script!")
        print("Get it from Ganache GUI → Click key icon next to account")
        return
    
    # Run tests
    test_health_check()
    
    token_id = test_mint_nft()
    if token_id:
        test_get_nft_details(token_id)
        test_get_nfts_by_owner()
        test_get_total_supply()
        
        listing_id = test_list_nft(token_id)
        if listing_id:
            test_get_listing(listing_id)
            test_get_all_listings()
            test_get_platform_fee()
    
    # Print summary
    print_summary()


if __name__ == "__main__":
    main()
