# NFT Marketplace - Performance Optimization Guide

## Current Image Loading Speed

The images load in 2 steps:
1. Fetch metadata JSON from IPFS (~1-2 seconds)
2. Fetch image from IPFS (~2-3 seconds)
**Total: 3-5 seconds per NFT**

## Optimizations Implemented ✅

1. **Faster IPFS Gateway**: Using `ipfs.io` instead of Pinata gateway
2. **Loading Spinner**: Visual feedback while loading
3. **Lazy Loading**: Images load only when scrolled into view
4. **Better Error Handling**: Graceful fallbacks

## Further Optimizations (Optional)

### Option 1: Cache Metadata in Database (Recommended)
Store the image URL directly in the database when minting:

**Benefits:**
- Instant image loading (no IPFS fetch needed)
- Reduced IPFS gateway load
- Better user experience

**Implementation:**
- Modify the indexer to fetch and cache metadata
- Add `image_url` and `metadata` columns to NFT table
- Update frontend to use cached data

### Option 2: Use Multiple IPFS Gateways (Fallback)
Try multiple gateways if one is slow:

```javascript
const IPFS_GATEWAYS = [
    'https://ipfs.io/ipfs/',
    'https://cloudflare-ipfs.com/ipfs/',
    'https://gateway.pinata.cloud/ipfs/'
];
```

### Option 3: Local IPFS Node
Run your own IPFS node for fastest access:
- Download IPFS Desktop
- Pin your NFT files locally
- Use `http://localhost:8080/ipfs/` as gateway

## Current Performance

With the optimizations:
- **First load**: 2-3 seconds (fetching from IPFS)
- **Subsequent loads**: Instant (browser cache)
- **Multiple NFTs**: Load in parallel

## Tips

1. **Small Images**: Keep NFT images under 1MB for faster loading
2. **Browser Cache**: Images are cached after first load
3. **Network**: IPFS speed depends on your internet connection
4. **Gateway Health**: Different gateways have different speeds at different times

## Testing Different Gateways

To test which gateway is fastest for you, try each one:
1. `https://ipfs.io/ipfs/` (usually fastest)
2. `https://cloudflare-ipfs.com/ipfs/` (very reliable)
3. `https://gateway.pinata.cloud/ipfs/` (your uploaded files)

You can change the gateway in `NFTCard.jsx` line 7.
