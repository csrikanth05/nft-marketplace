# Phase 4: Database Layer API - Features & Documentation

## Overview
Phase 4 adds **read-only API endpoints** that serve indexed blockchain data from the local database. These endpoints enable efficient querying without making expensive blockchain calls.

## Features Implemented

### 1. NFT Query Endpoints (3 endpoints)
- **GET /api/v1/db/nfts** - Get all NFTs with pagination
- **GET /api/v1/db/nfts/{token_id}** - Get specific NFT details
- **GET /api/v1/db/users/{address}/nfts** - Get all NFTs owned by a user

### 2. Marketplace Query Endpoints (3 endpoints)
- **GET /api/v1/db/listings** - Get all listings (with active_only filter)
- **GET /api/v1/db/listings/{listing_id}** - Get specific listing details
- **GET /api/v1/db/users/{address}/listings** - Get user's listings

### 3. Auction Query Endpoints (4 endpoints)
- **GET /api/v1/db/auctions** - Get all auctions (with active_only filter)
- **GET /api/v1/db/auctions/{auction_id}** - Get auction with bid history
- **GET /api/v1/db/users/{address}/auctions** - Get user's auctions
- **GET /api/v1/db/users/{address}/bids** - Get user's bid history

### 4. User Profile Endpoints (2 endpoints)
- **GET /api/v1/db/users/{address}** - Get user profile with statistics
- **GET /api/v1/db/users** - Get all users with stats

## How It Works

### Data Flow
```
Blockchain Events → Indexer Service → SQLite Database → Database API → Frontend
```

1. **Indexer** (Phase 3) continuously syncs blockchain events to the database
2. **Database API** (Phase 4) serves this data via REST endpoints
3. **Frontend** can query data efficiently without blockchain calls

### Key Features

#### Pagination
All list endpoints support pagination:
```
GET /api/v1/db/nfts?skip=0&limit=100
```

#### Filtering
Marketplace and auction endpoints support filtering:
```
GET /api/v1/db/listings?active_only=true
GET /api/v1/db/auctions?active_only=false
```

#### Nested Data
Responses include related data:
- Listings include NFT details
- Auctions include NFT details and bid history
- User profiles include owned NFTs and statistics

#### Statistics
User profiles automatically calculate:
- NFTs owned
- Active listings count
- Active auctions count
- Total bids placed

## Response Schemas

### NFTResponse
```json
{
  "id": 1,
  "token_id": 1,
  "contract_address": "0x...",
  "owner_address": "0x...",
  "creator_address": "0x...",
  "token_uri": "ipfs://...",
  "is_listed": false
}
```

### ListingResponse
```json
{
  "id": 1,
  "listing_id": 1,
  "seller_address": "0x...",
  "price_wei": "1000000000000000000",
  "price_eth": 1.0,
  "active": true,
  "sold": false,
  "cancelled": false,
  "nft": { /* NFTResponse */ }
}
```

### AuctionResponse
```json
{
  "id": 1,
  "auction_id": 1,
  "seller_address": "0x...",
  "start_time": 1700000000,
  "end_time": 1700003600,
  "reserve_price_eth": 0.5,
  "highest_bid_eth": 2.0,
  "highest_bidder_address": "0x...",
  "active": true,
  "ended": false,
  "nft": { /* NFTResponse */ },
  "bids": [ /* BidResponse[] */ ]
}
```

### UserProfileResponse
```json
{
  "address": "0x...",
  "username": null,
  "stats": {
    "address": "0x...",
    "nfts_owned": 3,
    "active_listings": 1,
    "active_auctions": 2,
    "total_bids": 5
  },
  "nfts": [ /* NFTResponse[] */ ]
}
```

## Testing

### Automated Testing
Run the automated test suite:
```bash
cd backend
python test_database_api.py
```

This tests:
- All endpoint responses
- Pagination
- Filtering
- 404 error handling
- Data integrity

### Manual Testing
Follow the step-by-step guide in `MANUAL_TESTING_PHASE4.md` to test each endpoint via Swagger UI at `http://localhost:8000/docs`.

## Architecture

### Files Created
- `backend/app/schemas/database.py` - Response models
- `backend/app/routers/database.py` - API endpoints
- `backend/test_database_api.py` - Automated tests
- `backend/MANUAL_TESTING_PHASE4.md` - Manual testing guide
- `backend/DATABASE_API.md` - This documentation

### Integration
The database router is registered in `backend/app/main.py` alongside the existing NFT, Marketplace, and Auction routers.

## Benefits

1. **Performance**: No blockchain calls needed for queries
2. **Efficiency**: Database queries are much faster than RPC calls
3. **Flexibility**: Easy filtering, pagination, and sorting
4. **User Experience**: Instant data retrieval for frontend
5. **Statistics**: Aggregated data (user stats) without complex calculations

## Next Steps

With Phase 4 complete, the backend now has:
- ✅ Smart contracts (Phase 1)
- ✅ Blockchain interaction APIs (Phase 2)
- ✅ Event indexing (Phase 3)
- ✅ Database query APIs (Phase 4)

Future phases could include:
- Phase 5: IPFS integration for metadata storage
- Phase 6: User authentication and authorization
- Phase 7: Advanced features (search, recommendations, analytics)
