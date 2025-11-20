# NFT Marketplace Backend API - Complete Documentation

This document provides comprehensive documentation for all API endpoints with request/response examples.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

Currently, the API uses private keys for transaction signing. Future versions will include JWT authentication for user management.

---

## NFT Endpoints

### 1. Mint NFT

**Endpoint**: `POST /nft/mint`

**Description**: Mint a new NFT with metadata and royalty information.

**Request Body**:
```json
{
  "to_address": "0x379f3Fe5316cf87c988B8C0C47D8A4f4049d5add",
  "token_uri": "ipfs://QmTestHash123",
  "royalty_receiver": "0x379f3Fe5316cf87c988B8C0C47D8A4f4049d5add",
  "royalty_fee": 500,
  "from_address": "0x379f3Fe5316cf87c988B8C0C47D8A4f4049d5add",
  "private_key": "0x..."
}
```

**Response**:
```json
{
  "transaction_hash": "0x...",
  "token_id": 1,
  "to_address": "0x379f3Fe5316cf87c988B8C0C47D8A4f4049d5add",
  "token_uri": "ipfs://QmTestHash123"
}
```

### 2. Get NFT Details

**Endpoint**: `GET /nft/{token_id}`

**Example**: `GET /nft/1`

**Response**:
```json
{
  "token_id": 1,
  "owner": "0x379f3Fe5316cf87c988B8C0C47D8A4f4049d5add",
  "creator": "0x379f3Fe5316cf87c988B8C0C47D8A4f4049d5add",
  "token_uri": "ipfs://QmTestHash123",
  "royalty_receiver": "0x379f3Fe5316cf87c988B8C0C47D8A4f4049d5add",
  "royalty_amount": 0.05
}
```

### 3. Get NFTs by Owner

**Endpoint**: `GET /nft/owner/{address}`

**Example**: `GET /nft/owner/0x379f3Fe5316cf87c988B8C0C47D8A4f4049d5add`

**Response**:
```json
[1, 2, 3]
```

### 4. Transfer NFT

**Endpoint**: `POST /nft/transfer`

**Request Body**:
```json
{
  "from_address": "0x379f3Fe5316cf87c988B8C0C47D8A4f4049d5add",
  "to_address": "0xRecipientAddress",
  "token_id": 1,
  "private_key": "0x..."
}
```

**Response**:
```json
{
  "transaction_hash": "0x...",
  "token_id": 1,
  "from_address": "0x379f3Fe5316cf87c988B8C0C47D8A4f4049d5add",
  "to_address": "0xRecipientAddress"
}
```

### 5. Burn NFT

**Endpoint**: `DELETE /nft/{token_id}?from_address=...&private_key=...`

**Response**:
```json
{
  "transaction_hash": "0x...",
  "token_id": 1,
  "status": "burned"
}
```

---

## Marketplace Endpoints

### 1. List NFT for Sale

**Endpoint**: `POST /marketplace/list`

**Request Body**:
```json
{
  "nft_contract_address": "0x131F714E9BD464D31a6f7C09369af53D82E03834",
  "token_id": 1,
  "price_eth": 1.5,
  "from_address": "0x379f3Fe5316cf87c988B8C0C47D8A4f4049d5add",
  "private_key": "0x..."
}
```

**Response**:
```json
{
  "transaction_hash": "0x...",
  "listing_id": 1,
  "token_id": 1,
  "price_eth": 1.5
}
```

**Note**: Before listing, approve the marketplace contract:
```javascript
// Using Web3
await nftContract.approve(marketplaceAddress, tokenId)
```

### 2. Buy NFT

**Endpoint**: `POST /marketplace/buy/{listing_id}`

**Request Body**:
```json
{
  "listing_id": 1,
  "from_address": "0xBuyerAddress",
  "private_key": "0x..."
}
```

**Response**:
```json
{
  "transaction_hash": "0x...",
  "listing_id": 1
}
```

### 3. Cancel Listing

**Endpoint**: `DELETE /marketplace/listing/{listing_id}`

**Request Body**:
```json
{
  "listing_id": 1,
  "from_address": "0x379f3Fe5316cf87c988B8C0C47D8A4f4049d5add",
  "private_key": "0x..."
}
```

**Response**:
```json
{
  "transaction_hash": "0x...",
  "listing_id": 1,
  "status": "cancelled"
}
```

### 4. Get Listing Details

**Endpoint**: `GET /marketplace/listing/{listing_id}`

**Response**:
```json
{
  "listing_id": 1,
  "seller": "0x379f3Fe5316cf87c988B8C0C47D8A4f4049d5add",
  "nft_contract": "0x131F714E9BD464D31a6f7C09369af53D82E03834",
  "token_id": 1,
  "price_wei": "1500000000000000000",
  "price_eth": 1.5,
  "active": true
}
```

### 5. Get All Active Listings

**Endpoint**: `GET /marketplace/listings`

**Response**:
```json
[
  {
    "listing_id": 1,
    "seller": "0x379f3Fe5316cf87c988B8C0C47D8A4f4049d5add",
    "nft_contract": "0x131F714E9BD464D31a6f7C09369af53D82E03834",
    "token_id": 1,
    "price_wei": "1500000000000000000",
    "price_eth": 1.5,
    "active": true
  }
]
```

---

## Auction Endpoints

### 1. Create Auction

**Endpoint**: `POST /auction/create`

**Request Body**:
```json
{
  "nft_contract_address": "0x131F714E9BD464D31a6f7C09369af53D82E03834",
  "token_id": 1,
  "start_time": 1700000000,
  "end_time": 1700086400,
  "reserve_price_eth": 0.5,
  "from_address": "0x379f3Fe5316cf87c988B8C0C47D8A4f4049d5add",
  "private_key": "0x..."
}
```

**Response**:
```json
{
  "transaction_hash": "0x...",
  "auction_id": 1,
  "token_id": 1,
  "reserve_price_eth": 0.5
}
```

### 2. Place Bid

**Endpoint**: `POST /auction/{auction_id}/bid`

**Request Body**:
```json
{
  "auction_id": 1,
  "bid_amount_eth": 1.0,
  "from_address": "0xBidderAddress",
  "private_key": "0x..."
}
```

**Response**:
```json
{
  "transaction_hash": "0x...",
  "auction_id": 1,
  "bid_amount_eth": 1.0
}
```

### 3. End Auction

**Endpoint**: `POST /auction/{auction_id}/end`

**Request Body**:
```json
{
  "auction_id": 1,
  "from_address": "0x379f3Fe5316cf87c988B8C0C47D8A4f4049d5add",
  "private_key": "0x..."
}
```

**Response**:
```json
{
  "transaction_hash": "0x...",
  "auction_id": 1,
  "status": "ended"
}
```

### 4. Withdraw Refunded Bid

**Endpoint**: `POST /auction/{auction_id}/withdraw`

**Request Body**:
```json
{
  "auction_id": 1,
  "from_address": "0xBidderAddress",
  "private_key": "0x..."
}
```

**Response**:
```json
{
  "transaction_hash": "0x...",
  "auction_id": 1,
  "status": "withdrawn"
}
```

### 5. Get Auction Details

**Endpoint**: `GET /auction/{auction_id}`

**Response**:
```json
{
  "auction_id": 1,
  "seller": "0x379f3Fe5316cf87c988B8C0C47D8A4f4049d5add",
  "nft_contract": "0x131F714E9BD464D31a6f7C09369af53D82E03834",
  "token_id": 1,
  "start_time": 1700000000,
  "end_time": 1700086400,
  "reserve_price_wei": "500000000000000000",
  "reserve_price_eth": 0.5,
  "highest_bidder": "0xBidderAddress",
  "highest_bid_wei": "1000000000000000000",
  "highest_bid_eth": 1.0,
  "active": true,
  "ended": false
}
```

### 6. Get All Active Auctions

**Endpoint**: `GET /auction/active/all`

**Response**: Array of auction details

---

## Error Responses

All endpoints return standard HTTP status codes:

- `200 OK`: Success
- `400 Bad Request`: Invalid request or blockchain error
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

**Error Response Format**:
```json
{
  "detail": "Error message describing what went wrong"
}
```

## Testing with cURL

### Mint NFT
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

### Get NFT Details
```bash
curl "http://localhost:8000/api/v1/nft/1"
```

### Get All Listings
```bash
curl "http://localhost:8000/api/v1/marketplace/listings"
```

## Testing with Python

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Mint NFT
response = requests.post(f"{BASE_URL}/nft/mint", json={
    "to_address": "0x379f3Fe5316cf87c988B8C0C47D8A4f4049d5add",
    "token_uri": "ipfs://QmTest",
    "royalty_receiver": "0x379f3Fe5316cf87c988B8C0C47D8A4f4049d5add",
    "royalty_fee": 500,
    "from_address": "0x379f3Fe5316cf87c988B8C0C47D8A4f4049d5add",
    "private_key": "YOUR_PRIVATE_KEY"
})
print(response.json())

# Get NFT details
response = requests.get(f"{BASE_URL}/nft/1")
print(response.json())
```

## Interactive Documentation

Visit `http://localhost:8000/docs` for interactive Swagger UI where you can test all endpoints directly from your browser.
