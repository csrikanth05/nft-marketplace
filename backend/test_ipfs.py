import requests
import io
import json

BASE_URL = "http://localhost:8000/api/v1/ipfs"

# Create a simple test image (1x1 pixel PNG)
TEST_IMAGE_DATA = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'

def test_ipfs_api():
    print("="*60)
    print("TESTING IPFS API ENDPOINTS")
    print("="*60)
    
    try:
        # Test 1: Upload image
        print("\n1. Testing POST /upload-image")
        files = {'file': ('test.png', io.BytesIO(TEST_IMAGE_DATA), 'image/png')}
        response = requests.post(f"{BASE_URL}/upload-image", files=files)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        image_result = response.json()
        print(f"   ✓ Image uploaded")
        print(f"   IPFS Hash: {image_result['ipfs_hash']}")
        print(f"   Gateway URL: {image_result['ipfs_url']}")
        
        image_hash = image_result['ipfs_hash']
        
        # Test 2: Upload metadata
        print("\n2. Testing POST /upload-metadata")
        metadata_request = {
            "name": "Test NFT",
            "description": "Automated test NFT",
            "image_ipfs_hash": image_hash,
            "attributes": [
                {"trait_type": "Test", "value": "Automated"}
            ]
        }
        response = requests.post(f"{BASE_URL}/upload-metadata", json=metadata_request)
        assert response.status_code == 200
        metadata_result = response.json()
        print(f"   ✓ Metadata uploaded")
        print(f"   IPFS Hash: {metadata_result['ipfs_hash']}")
        print(f"   Metadata: {json.dumps(metadata_result['metadata'], indent=2)}")
        
        # Test 3: Upload complete NFT bundle
        print("\n3. Testing POST /upload-nft")
        files = {'file': ('bundle_test.png', io.BytesIO(TEST_IMAGE_DATA), 'image/png')}
        data = {
            'name': 'Bundle Test NFT',
            'description': 'Complete NFT bundle test'
        }
        response = requests.post(f"{BASE_URL}/upload-nft", files=files, data=data)
        assert response.status_code == 200
        bundle_result = response.json()
        print(f"   ✓ NFT bundle uploaded")
        print(f"   Image Hash: {bundle_result['image_ipfs_hash']}")
        print(f"   Metadata Hash: {bundle_result['metadata_ipfs_hash']}")
        print(f"   Token URI: {bundle_result['token_uri']}")
        
        # Test 4: Get IPFS URL
        print("\n4. Testing GET /{ipfs_hash}")
        response = requests.get(f"{BASE_URL}/{image_hash}")
        assert response.status_code == 200
        url_result = response.json()
        print(f"   ✓ IPFS URL retrieved")
        print(f"   Gateway URL: {url_result['ipfs_url']}")
        print(f"   IPFS URI: {url_result['ipfs_uri']}")
        
        # Test 5: Verify image is accessible
        print("\n5. Testing image accessibility via gateway")
        response = requests.get(image_result['ipfs_url'])
        assert response.status_code == 200
        print(f"   ✓ Image accessible via Pinata gateway")
        
        # Test 6: Verify metadata is accessible
        print("\n6. Testing metadata accessibility via gateway")
        response = requests.get(metadata_result['ipfs_url'])
        assert response.status_code == 200
        retrieved_metadata = response.json()
        assert retrieved_metadata['name'] == "Test NFT"
        print(f"   ✓ Metadata accessible and correct")
        
        print("\n" + "="*60)
        print("✅ ALL IPFS TESTS PASSED")
        print("="*60)
        print("\n📝 Summary:")
        print(f"   - Image uploaded: {image_result['ipfs_hash']}")
        print(f"   - Metadata uploaded: {metadata_result['ipfs_hash']}")
        print(f"   - Bundle uploaded: {bundle_result['metadata_ipfs_hash']}")
        print(f"   - All content accessible via Pinata gateway")
        print(f"\n💡 Use this token_uri for minting:")
        print(f"   {bundle_result['token_uri']}")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("\nMake sure:")
    print("1. Backend server is running on http://localhost:8000")
    print("2. PINATA_JWT is configured in .env")
    print("\nPress Enter to start tests...")
    input()
    test_ipfs_api()
