# Backend Deployment and Testing Guide

This guide covers deploying and testing the FastAPI backend for the NFT marketplace.

## Prerequisites

- Python 3.8 or higher
- Ganache running with deployed smart contracts
- Contract addresses from Phase 1 deployment

## Installation Steps

### 1. Navigate to Backend Directory

```bash
cd c:\Users\csrik\Desktop\crypto\nft-marketplace\backend
```

### 2. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Expected output:
```
Successfully installed fastapi-0.104.1 uvicorn-0.24.0 web3-6.11.3 ...
```

### 4. Configure Environment Variables

Copy the example environment file:

```bash
copy .env.example .env
```

Edit `.env` and update with your contract addresses from Phase 1:

```env
# Update these with your actual deployed contract addresses
NFT_CONTRACT_ADDRESS=0x131F714E9BD464D31a6f7C09369af53D82E03834
MARKETPLACE_CONTRACT_ADDRESS=0x98afa0f7785cc0C5Fbd515A497Db4C553852eBdc
AUCTION_CONTRACT_ADDRESS=0xcd1c32196Fb2b0e1CEe685Ce49118343eA97f5Bc

# Generate a secure secret key
SECRET_KEY=your-secret-key-change-this-in-production
```

**Generate a secure secret key**:
```python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 5. Verify Ganache is Running

Ensure Ganache is running on `http://127.0.0.1:7545` with your deployed contracts.

## Running the Backend

### Development Mode (with auto-reload)

```bash
uvicorn app.main:app --reload
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Custom Port

```bash
uvicorn app.main:app --reload --port 8080
```

## Testing the API

### 1. Health Check

Open your browser or use curl:

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "healthy"}
```

### 2. Access API Documentation

Open in browser:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 3. Test NFT Minting

Using the Swagger UI (`/docs`):

1. Navigate to `POST /api/v1/nft/mint`
2. Click "Try it out"
3. Fill in the request body:

```json
{
  "to_address": "0x379f3Fe5316cf87c988B8C0C47D8A4f4049d5add",
  "token_uri": "ipfs://QmTestHash123",
  "royalty_receiver": "0x379f3Fe5316cf87c988B8C0C47D8A4f4049d5add",
  "royalty_fee": 500,
  "from_address": "0x379f3Fe5316cf87c988B8C0C47D8A4f4049d5add",
  "private_key": "YOUR_GANACHE_PRIVATE_KEY"
}
```

4. Click "Execute"
5. Check the response for `transaction_hash` and `token_id`

### 4. Test with cURL

```bash
curl -X POST "http://localhost:8000/api/v1/nft/mint" \
  -H "Content-Type: application/json" \
  -d '{
    "to_address": "0x379f3Fe5316cf87c988B8C0C47D8A4f4049d5add",
    "token_uri": "ipfs://QmTest",
    "royalty_receiver": "0x379f3Fe5316cf87c988B8C0C47D8A4f4049d5add",
    "royalty_fee": 500,
    "from_address": "0x379f3Fe5316cf87c988B8C0C47D8A4f4049d5add",
    "private_key": "YOUR_PRIVATE_KEY"
  }'
```

### 5. Test with Python

Create a test script `test_api.py`:

```python
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# Your Ganache account details
FROM_ADDRESS = "0x379f3Fe5316cf87c988B8C0C47D8A4f4049d5add"
PRIVATE_KEY = "YOUR_GANACHE_PRIVATE_KEY"

# Test 1: Mint NFT
print("Testing NFT Minting...")
response = requests.post(f"{BASE_URL}/nft/mint", json={
    "to_address": FROM_ADDRESS,
    "token_uri": "ipfs://QmTestHash123",
    "royalty_receiver": FROM_ADDRESS,
    "royalty_fee": 500,
    "from_address": FROM_ADDRESS,
    "private_key": PRIVATE_KEY
})
print(f"Mint Response: {response.json()}")
token_id = response.json().get("token_id")

# Test 2: Get NFT Details
print(f"\nGetting NFT {token_id} details...")
response = requests.get(f"{BASE_URL}/nft/{token_id}")
print(f"NFT Details: {response.json()}")

# Test 3: Get tokens by owner
print(f"\nGetting tokens owned by {FROM_ADDRESS}...")
response = requests.get(f"{BASE_URL}/nft/owner/{FROM_ADDRESS}")
print(f"Owned Tokens: {response.json()}")

# Test 4: Get all marketplace listings
print("\nGetting all marketplace listings...")
response = requests.get(f"{BASE_URL}/marketplace/listings")
print(f"Active Listings: {response.json()}")

print("\n✅ All tests completed!")
```

Run the test:
```bash
python test_api.py
```

## Complete Testing Workflow

### Step 1: Mint an NFT

```bash
curl -X POST "http://localhost:8000/api/v1/nft/mint" \
  -H "Content-Type: application/json" \
  -d '{...}'
```

### Step 2: Approve Marketplace (via Truffle Console)

```bash
cd ..
npx truffle console
```

```javascript
const nft = await NFTContract.deployed()
const marketplace = await Marketplace.deployed()
await nft.approve(marketplace.address, 1, {from: "0x379f3Fe5316cf87c988B8C0C47D8A4f4049d5add"})
```

### Step 3: List NFT on Marketplace (via API)

```bash
curl -X POST "http://localhost:8000/api/v1/marketplace/list" \
  -H "Content-Type: application/json" \
  -d '{
    "nft_contract_address": "0x131F714E9BD464D31a6f7C09369af53D82E03834",
    "token_id": 1,
    "price_eth": 1.5,
    "from_address": "0x379f3Fe5316cf87c988B8C0C47D8A4f4049d5add",
    "private_key": "YOUR_PRIVATE_KEY"
  }'
```

### Step 4: View Listing

```bash
curl "http://localhost:8000/api/v1/marketplace/listings"
```

### Step 5: Buy NFT (from different account)

```bash
curl -X POST "http://localhost:8000/api/v1/marketplace/buy/1" \
  -H "Content-Type: application/json" \
  -d '{
    "listing_id": 1,
    "from_address": "BUYER_ADDRESS",
    "private_key": "BUYER_PRIVATE_KEY"
  }'
```

## Troubleshooting

### Issue: "Failed to connect to blockchain"

**Solution**:
- Ensure Ganache is running
- Check `BLOCKCHAIN_RPC_URL` in `.env`
- Verify the port (7545 or 8545)

### Issue: "Contract address not found"

**Solution**:
- Verify contract addresses in `.env` match your deployed contracts
- Check that contracts are deployed to Ganache

### Issue: "Transaction failed"

**Solution**:
- Ensure the account has sufficient ETH
- Check that NFT is approved before listing/auctioning
- Verify private key is correct

### Issue: "Module not found"

**Solution**:
```bash
pip install -r requirements.txt
```

### Issue: "Port already in use"

**Solution**:
```bash
# Use a different port
uvicorn app.main:app --reload --port 8080
```

## Monitoring and Logs

### View Logs

The FastAPI server outputs logs to the console. Watch for:
- Request logs
- Error messages
- Transaction hashes

### Enable Debug Mode

In `.env`:
```env
DEBUG=True
```

## Production Deployment

### Using Gunicorn (Linux/macOS)

```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Using Docker

Create `Dockerfile`:
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t nft-marketplace-backend .
docker run -p 8000:8000 nft-marketplace-backend
```

## Next Steps

After successful deployment and testing:

1. ✅ Verify all endpoints work correctly
2. ✅ Test with multiple accounts
3. ✅ Check transaction confirmations in Ganache
4. ✅ Proceed to Phase 3: Blockchain Indexer / Event Listener

## API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/nft/mint` | Mint new NFT |
| GET | `/api/v1/nft/{token_id}` | Get NFT details |
| GET | `/api/v1/nft/owner/{address}` | Get NFTs by owner |
| POST | `/api/v1/marketplace/list` | List NFT for sale |
| POST | `/api/v1/marketplace/buy/{listing_id}` | Buy NFT |
| GET | `/api/v1/marketplace/listings` | Get all listings |
| POST | `/api/v1/auction/create` | Create auction |
| POST | `/api/v1/auction/{auction_id}/bid` | Place bid |
| GET | `/api/v1/auction/active/all` | Get active auctions |

For complete API documentation, see [BACKEND_API.md](BACKEND_API.md)
