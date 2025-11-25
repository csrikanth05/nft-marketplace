# NFT Marketplace Frontend

A clean, modern, and sleek React frontend for the NFT Marketplace with a blue-white theme.

## 🎨 Design Features

- **Color Scheme**: Blue and white with subtle gradients
- **Typography**: Clean sans-serif fonts
- **Layout**: Generous spacing, symmetrical design
- **Borders**: Rounded corners (12-16px), minimal sharp edges
- **Animations**: Smooth hover effects and transitions
- **Responsive**: Mobile-friendly design

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ installed
- Backend server running on `http://localhost:8000`
- MetaMask browser extension installed

### Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The application will open at `http://localhost:5173`

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Layout/
│   │   │   ├── Header.jsx        # Navigation header
│   │   │   └── Header.css
│   │   ├── NFT/
│   │   │   ├── NFTCard.jsx       # Individual NFT card
│   │   │   ├── NFTCard.css
│   │   │   ├── NFTGrid.jsx       # Grid layout for NFTs
│   │   │   └── NFTGrid.css
│   │   └── UI/
│   │       ├── Button.jsx        # Reusable button component
│   │       ├── Button.css
│   │       ├── Card.jsx          # Card container component
│   │       └── Card.css
│   ├── pages/
│   │   ├── Home.jsx              # Marketplace homepage
│   │   ├── CreateNFT.jsx         # NFT creation page
│   │   ├── MyNFTs.jsx            # User's NFT collection
│   │   └── Auctions.jsx          # Active auctions
│   ├── services/
│   │   └── api.js                # Backend API integration
│   ├── App.jsx                   # Main app with routing
│   ├── index.css                 # Global styles & design system
│   └── main.jsx                  # Entry point
```

## 🎯 Features

### Pages

1. **Home (Marketplace)**
   - Browse all listed NFTs
   - View NFT cards with images and prices
   - Click to view details

2. **Create NFT**
   - Upload image to IPFS
   - Add NFT metadata (name, description)
   - Set royalty fees
   - Mint NFT to blockchain

3. **My NFTs**
   - View your NFT collection
   - Requires wallet connection

4. **Auctions**
   - Browse active auctions
   - View current bids

### Components

- **Header**: Navigation with wallet connection
- **NFTCard**: Displays NFT with image, name, owner, price
- **NFTGrid**: Responsive grid layout for NFT cards
- **Button**: Styled button with variants (primary, secondary, ghost)
- **Card**: Container with shadow and hover effects

## 🎨 Design System

### Colors
```css
--primary-blue: #2563eb
--light-blue: #60a5fa
--dark-blue: #1e40af
--white: #ffffff
--off-white: #f8fafc
```

### Spacing
- xs: 0.5rem
- sm: 1rem
- md: 1.5rem
- lg: 2rem
- xl: 3rem
- 2xl: 4rem

### Border Radius
- sm: 8px
- md: 12px
- lg: 16px
- xl: 24px
- full: 9999px (pill shape)

## 🔌 API Integration

The frontend connects to the backend at `http://localhost:8000/api/v1`:

- **GET /db/nfts** - Fetch all NFTs
- **GET /db/listings** - Fetch marketplace listings
- **GET /db/auctions** - Fetch active auctions
- **POST /ipfs/upload-nft** - Upload image + metadata to IPFS
- **POST /nfts/mint** - Mint new NFT

## 🦊 Wallet Integration

- **MetaMask** required for wallet connection
- Connects to Ganache (localhost:7545)
- Displays connected address in header
- Required for creating NFTs and transactions

## 🛠️ Development

### Available Scripts

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Environment Variables

Create `.env` file if needed:
```
VITE_API_URL=http://localhost:8000/api/v1
```

## 📦 Deployment

### Build for Production

```bash
npm run build
```

This creates an optimized build in the `dist/` folder.

### Deploy to Vercel/Netlify

1. Push code to GitHub
2. Connect repository to Vercel/Netlify
3. Set build command: `npm run build`
4. Set publish directory: `dist`
5. Deploy!

### Deploy Locally

```bash
# Build the project
npm run build

# Serve the dist folder
npm run preview
```

## 🧪 Testing

### Manual Testing Steps

1. **Start Backend**:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. **Start Frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

3. **Test Wallet Connection**:
   - Click "Connect Wallet" in header
   - Approve MetaMask connection
   - Verify address displays in header

4. **Test NFT Creation**:
   - Go to "Create NFT" page
   - Upload an image
   - Fill in name and description
   - Click "Create NFT"
   - Enter private key when prompted
   - Wait for IPFS upload and minting

5. **Test Marketplace**:
   - Go to home page
   - Verify NFTs are displayed
   - Click on an NFT card

6. **Test My NFTs**:
   - Connect wallet
   - Go to "My NFTs"
   - Verify your NFTs are displayed

## 🎯 Key Features Implemented

✅ Clean blue-white theme
✅ Rounded corners throughout
✅ Generous spacing and padding
✅ Smooth hover animations
✅ Responsive grid layouts
✅ Wallet connection with MetaMask
✅ IPFS image upload
✅ NFT minting integration
✅ Marketplace browsing
✅ User NFT collection view
✅ Auction browsing

## 🐛 Troubleshooting

**Issue**: "Cannot connect wallet"
- **Solution**: Install MetaMask browser extension

**Issue**: "Failed to load NFTs"
- **Solution**: Ensure backend is running on port 8000

**Issue**: "CORS error"
- **Solution**: Backend CORS is configured for localhost:5173

**Issue**: "Images not loading"
- **Solution**: Check IPFS gateway URL in NFTCard.jsx

## 📝 Notes

- Private keys are requested via browser prompt (for development only)
- In production, use proper wallet signing instead of private keys
- IPFS images use Pinata gateway for display
- All transactions require MetaMask confirmation
