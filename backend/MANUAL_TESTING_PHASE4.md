# Manual Testing Guide - Phase 4: Database Layer API

This guide will help you test all the database query endpoints using Swagger UI.

## 🛠️ Prerequisites

1. **Backend Server**: Running (`uvicorn app.main:app --reload`)
2. **Database**: Populated with data from Phase 3 indexer
3. **Swagger UI**: Open at `http://localhost:8000/docs`

## 📋 Testing Endpoints

### NFT Endpoints

#### Test 1: Get All NFTs
1. Navigate to **GET /api/v1/db/nfts**
2. Click "Try it out"
3. Set `skip=0`, `limit=100`
4. Execute
5. **Expected**: List of all NFTs with owner addresses

#### Test 2: Get NFT by Token ID
1. Navigate to **GET /api/v1/db/nfts/{token_id}**
2. Click "Try it out"
3. Enter `token_id=1`
4. Execute
5. **Expected**: Details of NFT with token_id 1

#### Test 3: Get NFTs by Owner
1. Navigate to **GET /api/v1/db/users/{address}/nfts**
2. Click "Try it out"
3. Enter a wallet address (e.g., from Test 1)
4. Execute
5. **Expected**: List of NFTs owned by that address

---

### Marketplace Endpoints

#### Test 4: Get Active Listings
1. Navigate to **GET /api/v1/db/listings**
2. Click "Try it out"
3. Set `active_only=true`
4. Execute
5. **Expected**: Only active listings (not sold/cancelled)

#### Test 5: Get All Listings
1. Same endpoint as Test 4
2. Set `active_only=false`
3. Execute
4. **Expected**: All listings including sold/cancelled

#### Test 6: Get Listing by ID
1. Navigate to **GET /api/v1/db/listings/{listing_id}**
2. Click "Try it out"
3. Enter `listing_id=1`
4. Execute
5. **Expected**: Details of listing 1 with NFT info

#### Test 7: Get User's Listings
1. Navigate to **GET /api/v1/db/users/{address}/listings**
2. Click "Try it out"
3. Enter a seller address
4. Execute
5. **Expected**: All listings created by that user

---

### Auction Endpoints

#### Test 8: Get Active Auctions
1. Navigate to **GET /api/v1/db/auctions**
2. Click "Try it out"
3. Set `active_only=true`
4. Execute
5. **Expected**: Only active auctions

#### Test 9: Get Auction by ID with Bids
1. Navigate to **GET /api/v1/db/auctions/{auction_id}**
2. Click "Try it out"
3. Enter `auction_id=1`
4. Execute
5. **Expected**: Auction details with bid history in `bids` array

#### Test 10: Get User's Auctions
1. Navigate to **GET /api/v1/db/users/{address}/auctions**
2. Click "Try it out"
3. Enter a seller address
4. Execute
5. **Expected**: All auctions created by that user

#### Test 11: Get User's Bids
1. Navigate to **GET /api/v1/db/users/{address}/bids**
2. Click "Try it out"
3. Enter a bidder address
4. Execute
5. **Expected**: All bids placed by that user

---

### User Endpoints

#### Test 12: Get User Profile
1. Navigate to **GET /api/v1/db/users/{address}**
2. Click "Try it out"
3. Enter a user address
4. Set `include_nfts=true`
5. Execute
6. **Expected**: User profile with:
   - `stats`: NFTs owned, active listings, active auctions, total bids
   - `nfts`: Array of NFTs owned

#### Test 13: Get All Users
1. Navigate to **GET /api/v1/db/users**
2. Click "Try it out"
3. Execute
4. **Expected**: List of all users with their statistics

---

## 🧪 Advanced Testing

### Pagination Test
1. Use **GET /api/v1/db/nfts**
2. Set `limit=1`, `skip=0`
3. Execute → Should return 1 NFT
4. Set `skip=1` → Should return the next NFT

### 404 Error Test
1. Use **GET /api/v1/db/nfts/{token_id}**
2. Enter `token_id=99999` (non-existent)
3. Execute
4. **Expected**: 404 error with message "NFT with token_id 99999 not found"

---

## ✅ Verification Checklist

- [ ] All NFT endpoints return correct data
- [ ] Filtering works (active_only parameter)
- [ ] Pagination works correctly
- [ ] User profile shows accurate statistics
- [ ] Auction endpoint includes bid history
- [ ] 404 errors for non-existent resources
- [ ] Response schemas match expected format

## 📊 Compare with Database

You can verify the API responses match the database by:
1. Running `python check_db_state.py`
2. Comparing counts and values with API responses
