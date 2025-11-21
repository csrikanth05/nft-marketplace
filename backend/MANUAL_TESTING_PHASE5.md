# Manual Testing Guide - Phase 5: IPFS Storage

This guide will help you test the IPFS upload endpoints using Swagger UI.

## 🛠️ Prerequisites

1. **Backend Server**: Running (`uvicorn app.main:app --reload`)
2. **Pinata JWT**: Added to `.env` file
3. **Swagger UI**: Open at `http://localhost:8000/docs`
4. **Test Image**: Have a small image file ready (PNG, JPG, etc.)

## 📋 Testing Endpoints

### Test 1: Upload Image to IPFS
1. Navigate to **POST /api/v1/ipfs/upload-image**
2. Click "Try it out"
3. Click "Choose File" and select a test image
4. Execute
5. **Expected Response**:
   ```json
   {
     "ipfs_hash": "QmXxx...",
     "ipfs_url": "https://gateway.pinata.cloud/ipfs/QmXxx...",
     "ipfs_uri": "ipfs://QmXxx...",
     "filename": "your-image.png"
   }
   ```
6. **Verify**: Copy the `ipfs_url` and paste it in your browser. You should see your image!

---

### Test 2: Upload Metadata JSON
1. Navigate to **POST /api/v1/ipfs/upload-metadata**
2. Click "Try it out"
3. Use this request body (replace `QmXxx` with your image hash from Test 1):
   ```json
   {
     "name": "My First NFT",
     "description": "This is a test NFT created via the API",
     "image_ipfs_hash": "QmXxx...",
     "attributes": [
       {"trait_type": "Background", "value": "Blue"},
       {"trait_type": "Rarity", "value": "Common"}
     ]
   }
   ```
4. Execute
5. **Expected Response**:
   ```json
   {
     "ipfs_hash": "QmYyy...",
     "ipfs_url": "https://gateway.pinata.cloud/ipfs/QmYyy...",
     "ipfs_uri": "ipfs://QmYyy...",
     "metadata": { ... }
   }
   ```
6. **Verify**: Open the `ipfs_url` in your browser. You should see the JSON metadata.

---

### Test 3: Upload Complete NFT Bundle
This is the **easiest way** to upload an NFT - it uploads both image and metadata in one request!

1. Navigate to **POST /api/v1/ipfs/upload-nft**
2. Click "Try it out"
3. Fill in the form:
   - **file**: Choose your image file
   - **name**: "My Bundle NFT"
   - **description**: "Uploaded as a complete bundle"
4. Execute
5. **Expected Response**:
   ```json
   {
     "image_ipfs_hash": "QmXxx...",
     "image_ipfs_url": "https://gateway.pinata.cloud/ipfs/QmXxx...",
     "metadata_ipfs_hash": "QmYyy...",
     "metadata_ipfs_url": "https://gateway.pinata.cloud/ipfs/QmYyy...",
     "metadata_ipfs_uri": "ipfs://QmYyy...",
     "token_uri": "ipfs://QmYyy..."
   }
   ```
6. **Important**: Copy the `token_uri` value - this is what you'll use when minting an NFT!

---

### Test 4: Get IPFS URL from Hash
1. Navigate to **GET /api/v1/ipfs/{ipfs_hash}**
2. Click "Try it out"
3. Enter an IPFS hash from previous tests (e.g., `QmXxx...`)
4. Execute
5. **Expected Response**:
   ```json
   {
     "ipfs_hash": "QmXxx...",
     "ipfs_url": "https://gateway.pinata.cloud/ipfs/QmXxx...",
     "ipfs_uri": "ipfs://QmXxx..."
   }
   ```

---

## 🎨 Test 5: Mint NFT with IPFS Metadata

Now let's use the IPFS metadata to mint an actual NFT!

1. First, upload an NFT bundle (Test 3) and copy the `token_uri`
2. Navigate to **POST /api/v1/nfts/mint**
3. Use this request body:
   ```json
   {
     "to_address": "YOUR_WALLET_ADDRESS",
     "token_uri": "ipfs://QmYyy...",  // From Test 3
     "royalty_receiver": "YOUR_WALLET_ADDRESS",
     "royalty_fee": 500,
     "from_address": "YOUR_WALLET_ADDRESS",
     "private_key": "YOUR_PRIVATE_KEY"
   }
   ```
4. Execute
5. **Expected**: NFT minted successfully with IPFS metadata!

---

## 🔍 Verification Checklist

- [ ] Image uploaded successfully to IPFS
- [ ] Image accessible via gateway URL in browser
- [ ] Metadata JSON uploaded successfully
- [ ] Metadata accessible via gateway URL
- [ ] Complete NFT bundle uploaded in one request
- [ ] `token_uri` can be used for minting
- [ ] Minted NFT has correct IPFS metadata

---

## 💡 Tips

1. **Image Size**: Keep test images small (< 5MB) for faster uploads
2. **Gateway URL**: The Pinata gateway URL makes your content publicly accessible
3. **IPFS URI**: The `ipfs://` format is what smart contracts use
4. **Persistence**: Pinata keeps your files pinned permanently (on free tier, up to 1GB)

---

## 🐛 Troubleshooting

**Error: "PINATA_JWT not configured"**
- Make sure you added the JWT to your `.env` file
- Restart the backend server after adding it

**Error: "Pinata upload failed"**
- Check your Pinata JWT token is valid
- Verify you haven't exceeded Pinata's free tier limits

**Image not loading in browser**
- Wait a few seconds - IPFS propagation can take time
- Try refreshing the page
- Check the IPFS hash is correct
