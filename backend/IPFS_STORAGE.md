# Phase 5: IPFS Storage Layer - Documentation

## Overview
Phase 5 integrates IPFS (InterPlanetary File System) for decentralized storage of NFT images and metadata via Pinata, enabling NFTs to display visual content permanently and immutably.

## Features Implemented

### 1. IPFS Service (`backend/app/services/ipfs_service.py`)
Core service for interacting with Pinata API:
- `upload_file()` - Upload images/files to IPFS
- `upload_json()` - Upload JSON data to IPFS
- `upload_nft_metadata()` - Upload ERC-721 compliant metadata
- `get_ipfs_url()` - Convert IPFS hash to gateway URL
- `get_ipfs_uri()` - Convert IPFS hash to ipfs:// URI

### 2. API Endpoints (4 endpoints)
- **POST /api/v1/ipfs/upload-image** - Upload image file
- **POST /api/v1/ipfs/upload-metadata** - Upload metadata JSON
- **POST /api/v1/ipfs/upload-nft** - Upload complete NFT (image + metadata)
- **GET /api/v1/ipfs/{hash}** - Get gateway URL for IPFS hash

### 3. Response Schemas
- `ImageUploadResponse` - Image upload result with IPFS hash and URLs
- `MetadataUploadResponse` - Metadata upload result
- `NFTBundleResponse` - Complete NFT upload with both hashes
- `IPFSUrlResponse` - IPFS URL conversion result

## How It Works

### Upload Flow
```
Image File → Pinata API → IPFS Network → Gateway URL
     ↓
Metadata JSON → Pinata API → IPFS Network → token_uri
     ↓
Mint NFT with token_uri → Blockchain
```

### ERC-721 Metadata Standard
All metadata follows the standard format:
```json
{
  "name": "NFT Name",
  "description": "NFT Description",
  "image": "ipfs://QmImageHash",
  "attributes": [
    {"trait_type": "Background", "value": "Blue"},
    {"trait_type": "Rarity", "value": "Common"}
  ]
}
```

## Usage Examples

### Option 1: Upload Image and Metadata Separately
```bash
# 1. Upload image
POST /api/v1/ipfs/upload-image
# Returns: ipfs_hash

# 2. Upload metadata with image hash
POST /api/v1/ipfs/upload-metadata
{
  "name": "My NFT",
  "description": "...",
  "image_ipfs_hash": "QmXxx..."
}
# Returns: metadata ipfs_uri

# 3. Mint NFT with metadata URI
POST /api/v1/nfts/mint
{
  "token_uri": "ipfs://QmYyy..."
}
```

### Option 2: Upload Complete NFT Bundle (Recommended)
```bash
# Upload image + metadata in one request
POST /api/v1/ipfs/upload-nft
Form data:
- file: image.png
- name: "My NFT"
- description: "..."

# Returns: token_uri ready for minting
{
  "token_uri": "ipfs://QmYyy..."
}

# Mint directly
POST /api/v1/nfts/mint
{
  "token_uri": "ipfs://QmYyy..."
}
```

## Configuration

### Environment Variables
```bash
PINATA_JWT=your_pinata_jwt_token
PINATA_GATEWAY=https://gateway.pinata.cloud/ipfs/
```

### Pinata Setup
1. Create account at https://pinata.cloud
2. Generate API JWT (Settings → API Keys)
3. Add to `.env` file
4. Free tier: 1GB storage, unlimited bandwidth

## Testing

### Automated Testing
```bash
cd backend
python test_ipfs.py
```

Tests:
- Image upload to IPFS
- Metadata upload
- Complete NFT bundle upload
- Gateway accessibility
- Data integrity

### Manual Testing
Follow `MANUAL_TESTING_PHASE5.md` for step-by-step Swagger UI testing.

## Benefits

1. **Decentralization**: Content stored on IPFS, not centralized servers
2. **Permanence**: Pinata keeps files pinned indefinitely
3. **Immutability**: IPFS hashes ensure content can't be changed
4. **Accessibility**: Public gateway URLs for easy viewing
5. **Standard Compliance**: ERC-721 metadata format
6. **Integration**: Seamless with NFT minting workflow

## Files Created
- `backend/app/services/ipfs_service.py` - IPFS/Pinata integration
- `backend/app/schemas/ipfs.py` - Request/response models
- `backend/app/routers/ipfs.py` - API endpoints
- `backend/test_ipfs.py` - Automated tests
- `backend/MANUAL_TESTING_PHASE5.md` - Testing guide
- `backend/IPFS_STORAGE.md` - This documentation

## Files Modified
- `backend/app/config.py` - Added Pinata settings
- `backend/app/main.py` - Registered IPFS router
- `backend/requirements.txt` - Added `requests` dependency
- `backend/.env.example` - Added Pinata configuration

## Next Steps

With Phase 5 complete, you can now:
- Upload NFT images to IPFS
- Generate proper metadata URIs
- Mint NFTs with visual content
- Display NFT images in your frontend

The complete NFT marketplace backend is now ready for production!
