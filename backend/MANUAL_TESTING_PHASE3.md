# Manual Testing Guide - Phase 3: Blockchain Indexer

This guide will help you verify that the Blockchain Indexer is correctly listening to blockchain events and syncing them to your local database.

## 🛠️ Prerequisites

1. **VS Code Extension**: Install **"SQLite Viewer"** by Florian Klampfer (or any similar SQLite viewer).
   - *Why?* To view the contents of `backend/nft_marketplace.db` directly in VS Code.
2. **Ganache**: Running on port `7545`.
3. **Backend Server**: Running (`uvicorn app.main:app --reload`).

## 🧪 Testing Steps

### Step 1: Start Fresh (Optional but Recommended)
1. Stop the backend server.
2. Delete the file `backend/nft_marketplace.db` (if it exists).
3. Restart Ganache (Workspace -> Restart) to reset the blockchain.
4. Redeploy contracts: `truffle migrate --reset`.
5. Update `.env` with new contract addresses if they changed.
6. Start the backend: `uvicorn app.main:app --reload`.
   - *Observation*: The server logs should show "Starting Indexer Service...". A new `nft_marketplace.db` file will be created.

### Step 2: Verify Initial State
1. Open `backend/nft_marketplace.db` using the SQLite Viewer extension.
2. Check the tables `nfts`, `listings`, `auctions`. They should be empty.

### Step 3: Mint an NFT (Trigger `NFTMinted`)
1. Go to Swagger UI: `http://localhost:8000/docs`.
2. Execute **POST /api/v1/nfts/mint**.
   - **Request Body**:
     ```json
     {
       "to_address": "YOUR_WALLET_ADDRESS",
       "token_uri": "ipfs://test-metadata",
       "royalty_receiver": "YOUR_WALLET_ADDRESS",
       "royalty_fee": 500,
       "from_address": "YOUR_WALLET_ADDRESS",
       "private_key": "YOUR_PRIVATE_KEY"
     }
     ```
3. Wait 5-10 seconds (for the indexer to poll).
4. **Verify in DB**:
   - Refresh the `nfts` table.
   - You should see a new row with `token_id=1` and your `owner_address`.

### Step 4: List NFT on Marketplace (Trigger `NFTListed`)
1. Execute **POST /api/v1/marketplace/list**.
   - **Request Body**:
     ```json
     {
       "nft_contract_address": "NFT_CONTRACT_ADDRESS",
       "token_id": 1,
       "price_eth": 0.1,
       "from_address": "YOUR_WALLET_ADDRESS",
       "private_key": "YOUR_PRIVATE_KEY"
     }
     ```
2. Wait 5-10 seconds.
3. **Verify in DB**:
   - Refresh the `listings` table.
   - You should see a new row with `active=1` (True).
   - Check `nfts` table: `is_listed` should be `1` (True).

### Step 5: Buy NFT (Trigger `NFTSold`)
1. Use a **different** Ganache account (Account 2) for buying.
2. Execute **POST /api/v1/marketplace/buy**.
   - **Request Body**:
     ```json
     {
       "listing_id": 1,
       "price_eth": 0.1,
       "from_address": "ACCOUNT_2_ADDRESS",
       "private_key": "ACCOUNT_2_PRIVATE_KEY"
     }
     ```
3. Wait 5-10 seconds.
4. **Verify in DB**:
   - Refresh `listings` table: `active` should be `0`, `sold` should be `1`.
   - Refresh `nfts` table: `owner_address` should be Account 2's address, `is_listed` should be `0`.

### Step 6: Create Auction (Trigger `AuctionCreated`)
1. Mint a new NFT (Token ID 2) using Account 1 (or Account 2).
2. Execute **POST /api/v1/auctions/create**.
   - **Request Body**:
     ```json
     {
       "nft_contract_address": "NFT_CONTRACT_ADDRESS",
       "token_id": 2,
       "start_time": 1,
       "end_time": 9999999999,
       "reserve_price_eth": 0.5,
       "from_address": "OWNER_ADDRESS",
       "private_key": "OWNER_PRIVATE_KEY"
     }
     ```
3. Wait 5-10 seconds.
4. **Verify in DB**:
   - Refresh `auctions` table.
   - You should see a new row with `active=1`.

### Step 7: Place Bid (Trigger `BidPlaced`)
1. Use a different account to bid.
2. Execute **POST /api/v1/auctions/bid**.
3. Wait 5-10 seconds.
4. **Verify in DB**:
   - Refresh `bids` table: New bid record.
   - Refresh `auctions` table: `highest_bid_eth` should be updated.

## ❓ Troubleshooting

- **Data not showing up?**
  - Check the terminal where `uvicorn` is running. Do you see "Indexed ..." logs?
  - If not, the indexer might be stuck or waiting. Restart the backend.
- **"Database is locked" error?**
  - This can happen with SQLite if multiple processes access it. Ensure only one server instance is running.
