# NFT Listing Feature

## Overview
Added the ability to list NFTs for sale directly from the "My NFTs" page. Users can set a price in ETH and list their NFTs on the marketplace.

## Features Implemented

### 1. ListNFTModal Component
**File**: `frontend/src/components/NFT/ListNFTModal.jsx`

- Modal dialog for listing NFTs
- Price input field (ETH)
- Integrates with marketplace API
- Requests private key for transaction signing
- Success/error handling

### 2. MyNFTCard Component
**File**: `frontend/src/components/NFT/MyNFTCard.jsx`

- Specialized card for "My NFTs" page
- Shows "List for Sale" button for unlisted NFTs
- Shows "Listed for X ETH" badge for listed NFTs
- Click image to view details
- Click button to list for sale

### 3. Updated My NFTs Page
**File**: `frontend/src/pages/MyNFTs.jsx`

- Uses MyNFTCard instead of generic NFTCard
- 4-column grid layout (responsive)
- List button triggers modal
- Reloads NFTs after successful listing

### 4. Grid Layout
**File**: `frontend/src/pages/MyNFTs.css`

- **Desktop**: 4 NFTs per row
- **Tablet**: 3 NFTs per row
- **Mobile**: 2 NFTs per row
- **Small mobile**: 1 NFT per row
- Adequate spacing between cards

## User Flow

1. **Go to "My NFTs"** page
2. **See your NFTs** in 4-column grid
3. **Click "List for Sale"** button on any NFT
4. **Enter price** in ETH (e.g., 0.5)
5. **Enter private key** when prompted
6. **NFT gets listed** on marketplace
7. **Badge shows** "Listed for X ETH"
8. **NFT appears** on marketplace page

## Technical Details

### API Integration
- **Endpoint**: `POST /api/v1/marketplace/list`
- **Parameters**: token_id, price_eth, from_address, private_key
- **Response**: Transaction hash and listing details

### State Management
- Tracks selected NFT for listing
- Reloads NFTs after successful listing
- Updates UI to show listing status

### Responsive Design
- Grid adapts to screen size
- Maintains clean spacing
- Cards scale appropriately

## Files Created
- `frontend/src/components/NFT/ListNFTModal.jsx`
- `frontend/src/components/NFT/ListNFTModal.css`
- `frontend/src/components/NFT/MyNFTCard.jsx`
- `frontend/src/components/NFT/MyNFTCard.css`

## Files Modified
- `frontend/src/pages/MyNFTs.jsx` - Added listing functionality
- `frontend/src/pages/MyNFTs.css` - 4-column grid layout

## Next Steps

After listing, NFTs will:
- ✅ Appear on the marketplace page
- ✅ Show price in ETH
- ✅ Be available for purchase by other users
- ✅ Show "Listed" badge on My NFTs page

The marketplace is now fully functional for buying and selling NFTs!
