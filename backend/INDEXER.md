# Blockchain Indexer Documentation

The blockchain indexer is a background service that listens for events from the smart contracts and syncs them to a local SQLite database. This allows for efficient querying of data without constant blockchain calls.

## Architecture

- **Service**: `IndexerService` (`backend/app/services/indexer_service.py`)
- **Database**: SQLite (`backend/nft_marketplace.db`)
- **Models**: SQLAlchemy models in `backend/app/models/models.py`

## Indexed Data

The following data is indexed:

1. **Users**: Addresses interacting with the platform
2. **NFTs**: Token metadata, current owner, creator
3. **Listings**: Marketplace listings, price, status (active/sold/cancelled)
4. **Auctions**: Auction details, bids, status (active/ended/cancelled)
5. **Bids**: Bid history for auctions

## How it Works

1. **Startup**: The indexer starts automatically with the FastAPI application (`app.main:app`).
2. **Polling**: It polls the blockchain every 5 seconds for new blocks.
3. **Processing**:
   - Checks for new events since the last processed block.
   - Updates the database accordingly (e.g., changing NFT owner on transfer).
   - Updates the `EventProcessed` table to track progress.

## Manual Testing

To verify the indexer is working:

1. **Run the Test Script**:
   ```bash
   cd backend
   python test_indexer.py
   ```
   This script manually triggers the indexing process for all blocks from 0 to current and prints the data found in the database.

2. **Check Database**:
   You can inspect `nft_marketplace.db` using any SQLite viewer to see the populated tables.

## Integration

The indexer runs in the background of the main API process. No separate process is required for development.
