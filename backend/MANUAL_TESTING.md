# NFT Marketplace API - Manual Testing Guide

This guide provides step-by-step instructions for manually testing all API endpoints using the FastAPI Swagger UI.

## Prerequisites

1. ✅ Backend running: `uvicorn app.main:app --reload`
2. ✅ Ganache running on port 7545
3. ✅ Contracts deployed
4. ✅ Browser open to: http://localhost:8000/docs

## Contract Addresses (Your Deployment)

```
NFTContract: 0x7D89BCf357cD820A6A88D1ac9266e47f704734Ba
Marketplace: 0xBF4e7AeB704F2249b48ACec5037A6a43525B13a6
Auction: 0xAA9390E163Ff8Dd7Ddc5913065A47115c35eF712
```

## Ganache Account Details

Get these from your Ganache GUI:
- **Account 1 Address**: Click on the key icon next to the first account
- **Private Key**: Copy the private key shown

For this guide, we'll use:
- **Address**: `0x379f3Fe5316cf87c988B8C0C47D8A4f4049d5add` (your deployer account)
- **Private Key**: Get from Ganache

---

## Test 1: Health Check

**Endpoint**: `GET /health`

1. Scroll to the top of Swagger UI
2. Find `GET /health`
3. Click "Try it out"
4. Click "Execute"

**Expected Response**:
```json
{
  "status": "healthy"
}
```

✅ **Pass Criteria**: Status code 200, response shows "healthy"

---

## Test 2: Mint NFT

**Endpoint**: `POST /api/v1/nft/mint`

1. Find `POST /api/v1/nft/mint` in the NFT section
2. Click "Try it out"
3. Replace the request body with:

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

4. Replace `YOUR_GANACHE_PRIVATE_KEY` with the actual private key from Ganache
5. Click "Execute"

**Expected Response**:
```json
{
  "transaction_hash": "0x...",
  "token_id": 1,
  "to_address": "0x379f3Fe5316cf87c988B8C0C47D8A4f4049d5add",
  "token_uri": "ipfs://QmTestHash123"
}
```

✅ **Pass Criteria**: Status code 200, token_id = 1, transaction_hash present

**Note the token_id for next tests!**

---

## Test 3: Get NFT Details

**Endpoint**: `GET /api/v1/nft/{token_id}`

1. Find `GET /api/v1/nft/{token_id}`
2. Click "Try it out"
3. Enter `1` in the token_id field
4. Click "Execute"

**Expected Response**:
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

✅ **Pass Criteria**: Status code 200, correct owner and creator addresses

---

## Test 4: Get NFTs by Owner

**Endpoint**: `GET /api/v1/nft/owner/{address}`

1. Find `GET /api/v1/nft/owner/{address}`
2. Click "Try it out"
3. Enter your address: `0x379f3Fe5316cf87c988B8C0C47D8A4f4049d5add`
4. Click "Execute"

**Expected Response**:
```json
[1]
```

✅ **Pass Criteria**: Status code 200, array contains token ID 1

---

## Test 5: Get Total Supply

**Endpoint**: `GET /api/v1/nft/stats/total-supply`

1. Find `GET /api/v1/nft/stats/total-supply`
2. Click "Try it out"
3. Click "Execute"

**Expected Response**:
```json
{
  "total_supply": 1
}
```

✅ **Pass Criteria**: Status code 200, total_supply = 1

---

## Test 6: Approve Marketplace (via Truffle Console)

**Important**: Before listing on marketplace, approve the marketplace contract.

Open a new terminal:

```bash
cd c:\Users\csrik\Desktop\crypto\nft-marketplace
npx truffle console
```

In the console:

```javascript
const nft = await NFTContract.deployed()
const marketplace = await Marketplace.deployed()
await nft.approve(marketplace.address, 1, {from: "0x379f3Fe5316cf87c988B8C0C47D8A4f4049d5add"})
.exit
```

✅ **Pass Criteria**: Transaction successful

---

## Test 7: List NFT on Marketplace

**Endpoint**: `POST /api/v1/marketplace/list`

1. Find `POST /api/v1/marketplace/list`
2. Click "Try it out"
3. Use this request body:

```json
{
  "nft_contract_address": "0x7D89BCf357cD820A6A88D1ac9266e47f704734Ba",
  "token_id": 1,
  "price_eth": 1.5,
  "from_address": "0x379f3Fe5316cf87c988B8C0C47D8A4f4049d5add",
  "private_key": "YOUR_GANACHE_PRIVATE_KEY"
}
```

4. Click "Execute"

**Expected Response**:
```json
{
  "transaction_hash": "0x...",
  "listing_id": 1,
  "token_id": 1,
  "price_eth": 1.5
}
```

✅ **Pass Criteria**: Status code 200, listing_id = 1

**Note the listing_id!**

---

## Test 8: Get Listing Details

**Endpoint**: `GET /api/v1/marketplace/listing/{listing_id}`

1. Find `GET /api/v1/marketplace/listing/{listing_id}`
2. Click "Try it out"
3. Enter `1` for listing_id
4. Click "Execute"

**Expected Response**:
```json
{
  "listing_id": 1,
  "seller": "0x379f3Fe5316cf87c988B8C0C47D8A4f4049d5add",
  "nft_contract": "0x7D89BCf357cD820A6A88D1ac9266e47f704734Ba",
  "token_id": 1,
  "price_wei": "1500000000000000000",
  "price_eth": 1.5,
  "active": true
}
```

✅ **Pass Criteria**: Status code 200, active = true, price_eth = 1.5

---

## Test 9: Get All Active Listings

**Endpoint**: `GET /api/v1/marketplace/listings`

1. Find `GET /api/v1/marketplace/listings`
2. Click "Try it out"
3. Click "Execute"

**Expected Response**:
```json
[
  {
    "listing_id": 1,
    "seller": "0x379f3Fe5316cf87c988B8C0C47D8A4f4049d5add",
    "nft_contract": "0x7D89BCf357cD820A6A88D1ac9266e47f704734Ba",
    "token_id": 1,
    "price_wei": "1500000000000000000",
    "price_eth": 1.5,
    "active": true
  }
]
```

✅ **Pass Criteria**: Status code 200, array contains 1 listing

---

## Test 10: Get Platform Fee

**Endpoint**: `GET /api/v1/marketplace/stats/platform-fee`

1. Find `GET /api/v1/marketplace/stats/platform-fee`
2. Click "Try it out"
3. Click "Execute"

**Expected Response**:
```json
{
  "platform_fee_bps": 250,
  "platform_fee_percent": 2.5
}
```

✅ **Pass Criteria**: Status code 200, platform_fee_percent = 2.5

---

## Test 11: Buy NFT (from different account)

**Endpoint**: `POST /api/v1/marketplace/buy/{listing_id}`

**Note**: Use a different Ganache account for this test.

1. Get Account 2 from Ganache (address and private key)
2. Find `POST /api/v1/marketplace/buy/1`
3. Click "Try it out"
4. Use this request body:

```json
{
  "listing_id": 1,
  "from_address": "ACCOUNT_2_ADDRESS",
  "private_key": "ACCOUNT_2_PRIVATE_KEY"
}
```

5. Click "Execute"

**Expected Response**:
```json
{
  "transaction_hash": "0x...",
  "listing_id": 1
}
```

✅ **Pass Criteria**: Status code 200, transaction successful

---

## Test 12: Verify NFT Owner Changed

**Endpoint**: `GET /api/v1/nft/1`

1. Find `GET /api/v1/nft/1`
2. Click "Try it out"
3. Click "Execute"

**Expected Response**:
```json
{
  "token_id": 1,
  "owner": "ACCOUNT_2_ADDRESS",
  ...
}
```

✅ **Pass Criteria**: Owner is now Account 2

---

## Test 13: Mint Another NFT (for auction)

**Endpoint**: `POST /api/v1/nft/mint`

1. Mint another NFT using the same process as Test 2
2. Note the new token_id (should be 2)

---

## Test 14: Approve Auction Contract

In Truffle console:

```javascript
const nft = await NFTContract.deployed()
const auction = await Auction.deployed()
await nft.approve(auction.address, 2, {from: "0x379f3Fe5316cf87c988B8C0C47D8A4f4049d5add"})
```

---

## Test 15: Create Auction

**Endpoint**: `POST /api/v1/auction/create`

1. Find `POST /api/v1/auction/create`
2. Click "Try it out"
3. Calculate timestamps:
   - Start time: Current time (use https://www.unixtimestamp.com/)
   - End time: Current time + 3600 (1 hour later)

```json
{
  "nft_contract_address": "0x7D89BCf357cD820A6A88D1ac9266e47f704734Ba",
  "token_id": 2,
  "start_time": 1763654000,
  "end_time": 1763655000,
  "reserve_price_eth": 0.5,
  "from_address": "0x379f3Fe5316cf87c988B8C0C47D8A4f4049d5add",
  "private_key": "YOUR_GANACHE_PRIVATE_KEY"
}
```

4. Click "Execute"

**Expected Response**:
```json
{
  "transaction_hash": "0x...",
  "auction_id": 1,
  "token_id": 2,
  "reserve_price_eth": 0.5
}
```

✅ **Pass Criteria**: Status code 200, auction_id = 1

---

## Test 16: Get Auction Details

**Endpoint**: `GET /api/v1/auction/{auction_id}`

1. Find `GET /api/v1/auction/1`
2. Click "Try it out"
3. Click "Execute"

**Expected Response**:
```json
{
  "auction_id": 1,
  "seller": "0x379f3Fe5316cf87c988B8C0C47D8A4f4049d5add",
  "nft_contract": "0x7D89BCf357cD820A6A88D1ac9266e47f704734Ba",
  "token_id": 2,
  "start_time": 1700000000,
  "end_time": 1700003600,
  "reserve_price_eth": 0.5,
  "highest_bidder": "0x0000000000000000000000000000000000000000",
  "highest_bid_eth": 0,
  "active": true,
  "ended": false
}
```

✅ **Pass Criteria**: Status code 200, active = true, ended = false

---

## Test 17: Place Bid

**Endpoint**: `POST /api/v1/auction/{auction_id}/bid`

Use Account 2 for bidding:

```json
{
  "auction_id": 1,
  "bid_amount_eth": 1.0,
  "from_address": "ACCOUNT_2_ADDRESS",
  "private_key": "ACCOUNT_2_PRIVATE_KEY"
}
```

**Expected Response**:
```json
{
  "transaction_hash": "0x...",
  "auction_id": 1,
  "bid_amount_eth": 1.0
}
```

✅ **Pass Criteria**: Status code 200, bid placed successfully

---

## Test 18: Get All Active Auctions

**Endpoint**: `GET /api/v1/auction/active/all`

1. Find `GET /api/v1/auction/active/all`
2. Click "Try it out"
3. Click "Execute"

**Expected Response**: Array with 1 auction

✅ **Pass Criteria**: Status code 200, array contains auction with highest_bid_eth = 1.0

---

## Test Summary Checklist

- [ ] Test 1: Health Check
- [ ] Test 2: Mint NFT
- [ ] Test 3: Get NFT Details
- [ ] Test 4: Get NFTs by Owner
- [ ] Test 5: Get Total Supply
- [ ] Test 6: Approve Marketplace
- [ ] Test 7: List NFT on Marketplace
- [ ] Test 8: Get Listing Details
- [ ] Test 9: Get All Active Listings
- [ ] Test 10: Get Platform Fee
- [ ] Test 11: Buy NFT
- [ ] Test 12: Verify NFT Owner Changed
- [ ] Test 13: Mint Another NFT
- [ ] Test 14: Approve Auction Contract
- [ ] Test 15: Create Auction
- [ ] Test 16: Get Auction Details
- [ ] Test 17: Place Bid
- [ ] Test 18: Get All Active Auctions

---

## Troubleshooting

### Error: "Failed to connect to blockchain"
- Ensure Ganache is running on port 7545
- Check `.env` file has correct `BLOCKCHAIN_RPC_URL`

### Error: "Marketplace not approved"
- Run the approval step in Truffle console (Test 6)

### Error: "Not the owner"
- Verify you're using the correct account address and private key

### Error: "Insufficient payment"
- Check the price in the listing and ensure sufficient ETH

---

## Quick Reference

**Your Contract Addresses**:
```
NFT: 0x7D89BCf357cD820A6A88D1ac9266e47f704734Ba
Marketplace: 0xBF4e7AeB704F2249b48ACec5037A6a43525B13a6
Auction: 0xAA9390E163Ff8Dd7Ddc5913065A47115c35eF712
```

**Swagger UI**: http://localhost:8000/docs

**Get Ganache Private Key**: Ganache GUI → Click key icon next to account
