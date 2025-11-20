# NFT Marketplace Backend API

FastAPI backend for NFT marketplace with Web3 blockchain integration.

## Features

- **NFT Operations**: Mint, transfer, burn, and query NFTs
- **Marketplace**: List NFTs for sale, buy, and cancel listings
- **Auctions**: Create time-based auctions, place bids, end auctions
- **Web3 Integration**: Direct interaction with Ethereum smart contracts
- **Auto-generated Documentation**: Swagger UI and ReDoc
- **CORS Support**: Configured for frontend integration

## Tech Stack

- **FastAPI**: Modern async Python web framework
- **Web3.py**: Ethereum blockchain interaction
- **Pydantic**: Data validation and serialization
- **SQLAlchemy**: Database ORM (ready for future use)
- **Uvicorn**: ASGI server

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration
│   ├── database.py          # Database setup
│   ├── routers/             # API endpoints
│   │   ├── nft.py
│   │   ├── marketplace.py
│   │   └── auction.py
│   ├── services/            # Business logic
│   │   ├── web3_service.py
│   │   ├── nft_service.py
│   │   ├── marketplace_service.py
│   │   └── auction_service.py
│   └── schemas/             # Pydantic models
│       ├── nft.py
│       ├── marketplace.py
│       └── auction.py
├── requirements.txt
├── .env.example
└── README.md
```

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and update with your contract addresses:

```bash
cp .env.example .env
```

Update the contract addresses in `.env` with your deployed contract addresses from Ganache.

### 3. Start the Server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### 4. Access Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### NFT Operations

- `POST /api/v1/nft/mint` - Mint new NFT
- `GET /api/v1/nft/{token_id}` - Get NFT details
- `GET /api/v1/nft/owner/{address}` - Get NFTs by owner
- `POST /api/v1/nft/transfer` - Transfer NFT
- `DELETE /api/v1/nft/{token_id}` - Burn NFT

### Marketplace Operations

- `POST /api/v1/marketplace/list` - List NFT for sale
- `POST /api/v1/marketplace/buy/{listing_id}` - Buy NFT
- `DELETE /api/v1/marketplace/listing/{listing_id}` - Cancel listing
- `GET /api/v1/marketplace/listing/{listing_id}` - Get listing details
- `GET /api/v1/marketplace/listings` - Get all active listings

### Auction Operations

- `POST /api/v1/auction/create` - Create auction
- `POST /api/v1/auction/{auction_id}/bid` - Place bid
- `POST /api/v1/auction/{auction_id}/end` - End auction
- `DELETE /api/v1/auction/{auction_id}` - Cancel auction
- `POST /api/v1/auction/{auction_id}/withdraw` - Withdraw refunded bid
- `GET /api/v1/auction/{auction_id}` - Get auction details
- `GET /api/v1/auction/active/all` - Get all active auctions

## Testing

See [BACKEND_API.md](BACKEND_API.md) for detailed API documentation and examples.

See [DEPLOYMENT.md](DEPLOYMENT.md) for deployment and testing instructions.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `BLOCKCHAIN_RPC_URL` | Ganache/Ethereum RPC URL | `http://127.0.0.1:7545` |
| `NFT_CONTRACT_ADDRESS` | Deployed NFT contract address | Required |
| `MARKETPLACE_CONTRACT_ADDRESS` | Deployed Marketplace contract address | Required |
| `AUCTION_CONTRACT_ADDRESS` | Deployed Auction contract address | Required |
| `DATABASE_URL` | Database connection string | `sqlite:///./nft_marketplace.db` |
| `SECRET_KEY` | JWT secret key | Required |

## Development

```bash
# Run with auto-reload
uvicorn app.main:app --reload --port 8000

# Run in production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## License

MIT
