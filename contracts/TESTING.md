# Testing Guide

This guide explains how to run and verify the smart contract test suites.

## Running All Tests

To run the complete test suite:

```bash
npm test
```

Or:

```bash
truffle test
```

**Expected Output**:
```
  Contract: NFTContract
    Deployment
      ✓ should deploy with correct name and symbol
      ✓ should set the correct owner
    Minting
      ✓ should mint NFT with correct metadata
      ✓ should emit NFTMinted event
      ✓ should set royalty information correctly
      ✓ should reject minting to zero address
      ✓ should reject empty URI
      ✓ should reject royalty fee over 100%
      ✓ should increment token IDs correctly
    Token Management
      ✓ should transfer NFT correctly
      ✓ should burn NFT by owner
      ✓ should emit NFTBurned event
      ✓ should reject burn by non-owner
      ✓ should return creator of token
      ✓ should return tokens owned by address
    ERC721 Compliance
      ✓ should support ERC721 interface
      ✓ should support ERC2981 interface

  Contract: Marketplace
    Deployment
      ✓ should deploy with correct platform fee
      ✓ should deploy with correct fee recipient
      ✓ should reject deployment with fee over 100%
    Listing NFTs
      ✓ should list NFT successfully
      ✓ should emit NFTListed event
      ✓ should reject listing without approval
      ✓ should reject listing by non-owner
      ✓ should reject listing with zero price
    Buying NFTs
      ✓ should buy NFT successfully
      ✓ should emit NFTSold event
      ✓ should reject purchase with insufficient payment
      ✓ should reject seller buying own NFT
      ✓ should refund excess payment
    Canceling Listings
      ✓ should cancel listing successfully
      ✓ should emit ListingCancelled event
      ✓ should reject cancellation by non-seller
    Admin Functions
      ✓ should update platform fee
      ✓ should update fee recipient
      ✓ should reject fee update by non-owner

  Contract: Auction
    Deployment
      ✓ should deploy with correct platform fee
      ✓ should deploy with correct fee recipient
    Creating Auctions
      ✓ should create auction successfully
      ✓ should emit AuctionCreated event
      ✓ should reject auction with past start time
      ✓ should reject auction with end time before start time
    Bidding
      ✓ should place bid successfully
      ✓ should emit BidPlaced event
      ✓ should refund previous highest bidder
      ✓ should allow withdrawal of refunded bid
      ✓ should reject bid below reserve price
      ✓ should reject bid not higher than current highest
      ✓ should reject bid from seller
    Ending Auctions
      ✓ should end auction with winner
      ✓ should emit AuctionEnded event
    Canceling Auctions
      ✓ should cancel auction without bids
      ✓ should emit AuctionCancelled event
      ✓ should reject cancellation by non-seller
    Admin Functions
      ✓ should update platform fee
      ✓ should update fee recipient

  XX passing (XXs)
```

## Running Specific Test Files

To run tests for a specific contract:

```bash
# Test NFT Contract only
truffle test test/NFTContract.test.js

# Test Marketplace only
truffle test test/Marketplace.test.js

# Test Auction only
truffle test test/Auction.test.js
```

## Test Coverage

### NFTContract Tests

**File**: `test/NFTContract.test.js`

Tests cover:
- ✅ Contract deployment and initialization
- ✅ NFT minting with metadata and royalties
- ✅ Token transfers between accounts
- ✅ Burning tokens
- ✅ Creator tracking
- ✅ Token enumeration (tokensOfOwner)
- ✅ ERC721 and ERC2981 interface support
- ✅ Input validation and error handling

### Marketplace Tests

**File**: `test/Marketplace.test.js`

Tests cover:
- ✅ Contract deployment with platform fee
- ✅ Listing NFTs for sale
- ✅ Buying listed NFTs
- ✅ Platform fee calculation and distribution
- ✅ Royalty payment to creators
- ✅ Excess payment refunds
- ✅ Canceling listings
- ✅ Admin functions (fee updates)
- ✅ Access control and permissions

### Auction Tests

**File**: `test/Auction.test.js`

Tests cover:
- ✅ Contract deployment
- ✅ Creating auctions with time constraints
- ✅ Placing bids
- ✅ Automatic refunds for outbid users
- ✅ Bid withdrawals
- ✅ Ending auctions and transferring NFTs
- ✅ Fee and royalty distribution
- ✅ Canceling auctions without bids
- ✅ Time-based validation
- ✅ Admin functions

## Manual Testing Workflow

### 1. Mint an NFT

```bash
truffle console
```

```javascript
const accounts = await web3.eth.getAccounts()
const nft = await NFTContract.deployed()

// Mint NFT
const tx = await nft.mintNFT(
  accounts[0],
  "ipfs://QmTestHash123",
  accounts[0],
  500, // 5% royalty
  { from: accounts[0] }
)

const tokenId = tx.logs[0].args.tokenId.toString()
console.log("Minted token ID:", tokenId)
```

### 2. List NFT on Marketplace

```javascript
const marketplace = await Marketplace.deployed()
const price = web3.utils.toWei("1", "ether")

// Approve marketplace
await nft.approve(marketplace.address, tokenId, { from: accounts[0] })

// List NFT
const listTx = await marketplace.listNFT(
  nft.address,
  tokenId,
  price,
  { from: accounts[0] }
)

const listingId = listTx.logs[0].args.listingId.toString()
console.log("Created listing ID:", listingId)
```

### 3. Buy NFT from Marketplace

```javascript
// Buy from different account
await marketplace.buyNFT(listingId, {
  from: accounts[1],
  value: price
})

// Verify new owner
const newOwner = await nft.ownerOf(tokenId)
console.log("New owner:", newOwner)
console.log("Is buyer:", newOwner === accounts[1])
```

### 4. Create an Auction

```javascript
// Mint another NFT
const tx2 = await nft.mintNFT(
  accounts[0],
  "ipfs://QmTestHash456",
  accounts[0],
  500,
  { from: accounts[0] }
)
const tokenId2 = tx2.logs[0].args.tokenId.toString()

const auction = await Auction.deployed()
const reservePrice = web3.utils.toWei("0.5", "ether")

// Approve auction contract
await nft.approve(auction.address, tokenId2, { from: accounts[0] })

// Create auction (starts now, ends in 1 hour)
const currentTime = Math.floor(Date.now() / 1000)
const auctionTx = await auction.createAuction(
  nft.address,
  tokenId2,
  currentTime,
  currentTime + 3600,
  reservePrice,
  { from: accounts[0] }
)

const auctionId = auctionTx.logs[0].args.auctionId.toString()
console.log("Created auction ID:", auctionId)
```

### 5. Place Bids

```javascript
const bidAmount = web3.utils.toWei("1", "ether")

// Place bid from account 1
await auction.placeBid(auctionId, {
  from: accounts[1],
  value: bidAmount
})

// Place higher bid from account 2
const higherBid = web3.utils.toWei("1.5", "ether")
await auction.placeBid(auctionId, {
  from: accounts[2],
  value: higherBid
})

// Check auction state
const auctionData = await auction.getAuction(auctionId)
console.log("Highest bidder:", auctionData.highestBidder)
console.log("Highest bid:", web3.utils.fromWei(auctionData.highestBid, "ether"), "ETH")
```

### 6. Withdraw Refunded Bid

```javascript
// Account 1 was outbid, can withdraw
await auction.withdraw(auctionId, { from: accounts[1] })
console.log("Refund withdrawn successfully")
```

## Verifying Contract Events

Events are crucial for the blockchain indexer. Verify they're emitted correctly:

```javascript
// Check NFT minting event
const nft = await NFTContract.deployed()
const tx = await nft.mintNFT(
  accounts[0],
  "ipfs://test",
  accounts[0],
  500,
  { from: accounts[0] }
)

console.log("Events emitted:")
tx.logs.forEach(log => {
  console.log(`- ${log.event}`)
  console.log(`  Args:`, log.args)
})
```

## Gas Cost Analysis

Check gas costs for operations:

```javascript
const tx = await nft.mintNFT(/* ... */)
console.log("Gas used:", tx.receipt.gasUsed)
console.log("Gas price:", await web3.eth.getGasPrice())

const gasCost = tx.receipt.gasUsed * parseInt(await web3.eth.getGasPrice())
console.log("Total cost:", web3.utils.fromWei(gasCost.toString(), "ether"), "ETH")
```

## Troubleshooting Tests

### Tests Failing Due to Timing

Some auction tests use time-based logic. If tests fail:

1. Ensure Ganache is running
2. Try increasing timeout in `truffle-config.js`:
   ```javascript
   mocha: {
     timeout: 100000
   }
   ```

### Tests Failing Due to Gas

If you see "out of gas" errors:

1. Increase gas limit in `truffle-config.js`
2. Or in Ganache settings

### Resetting Test State

Between test runs, you may need to:

```bash
# Redeploy contracts
truffle migrate --reset

# Or restart Ganache and redeploy
```

## Success Criteria

All tests should pass with:
- ✅ No compilation errors
- ✅ No failed test cases
- ✅ All events emitted correctly
- ✅ Gas costs within reasonable limits
- ✅ All edge cases handled properly

## Next Steps

After all tests pass:
1. ✅ Verify contracts work via Truffle console
2. ✅ Test with MetaMask transactions
3. ✅ Proceed to Phase 2: Backend REST API Layer
