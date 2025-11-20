# Smart Contracts Setup Guide

This guide will walk you through setting up the development environment for the NFT Marketplace smart contracts.

## Prerequisites

Before you begin, ensure you have the following installed:

1. **Node.js** (v16 or higher)
   - Download from: https://nodejs.org/
   - Verify installation: `node --version`

2. **npm** (comes with Node.js)
   - Verify installation: `npm --version`

3. **Ganache** (Local Blockchain)
   - **Option A - Ganache GUI** (Recommended for beginners):
     - Download from: https://trufflesuite.com/ganache/
     - Install and launch the application
     - Create a new workspace or quickstart
     - Default RPC Server: `http://127.0.0.1:7545`
   
   - **Option B - Ganache CLI**:
     ```bash
     npm install -g ganache
     ganache
     ```
     - Default RPC Server: `http://127.0.0.1:8545`

4. **Truffle** (Smart Contract Development Framework)
   ```bash
   npm install -g truffle
   ```
   - Verify installation: `truffle version`

5. **MetaMask** (Browser Wallet)
   - Install browser extension from: https://metamask.io/
   - Available for Chrome, Firefox, Brave, Edge

## Step 1: Install Project Dependencies

Navigate to the project directory and install dependencies:

```bash
cd c:\Users\csrik\Desktop\crypto\nft-marketplace
npm install
```

This will install:
- OpenZeppelin Contracts (secure, audited contract libraries)
- Truffle and testing dependencies
- Web3 provider for deployment

## Step 2: Configure Ganache

### Using Ganache GUI:

1. Launch Ganache
2. Click "New Workspace" or "Quickstart"
3. Note the following settings:
   - **RPC Server**: `http://127.0.0.1:7545`
   - **Network ID**: `5777` (or any number shown)
   - **Port**: `7545`
4. You should see 10 accounts, each with 100 ETH
5. Keep Ganache running in the background

### Using Ganache CLI:

```bash
ganache --port 7545
```

Keep this terminal window open.

## Step 3: Configure MetaMask

1. **Open MetaMask** in your browser
2. **Add Ganache Network**:
   - Click the network dropdown (top center)
   - Click "Add Network" → "Add a network manually"
   - Fill in the details:
     - **Network Name**: Ganache Local
     - **New RPC URL**: `http://127.0.0.1:7545`
     - **Chain ID**: `1337` (or `5777` if using GUI)
     - **Currency Symbol**: ETH
   - Click "Save"

3. **Import Ganache Account**:
   - In Ganache, click the key icon next to any account to reveal the private key
   - Copy the private key
   - In MetaMask, click the account icon → "Import Account"
   - Paste the private key
   - Click "Import"
   - You should now see the account with 100 ETH

## Step 4: Compile Smart Contracts

Compile the Solidity contracts:

```bash
npm run compile
```

Or:

```bash
truffle compile
```

**Expected Output**:
```
Compiling your contracts...
===========================
> Compiling .\contracts\NFTContract.sol
> Compiling .\contracts\Marketplace.sol
> Compiling .\contracts\Auction.sol
> Compiling @openzeppelin\contracts\...

> Artifacts written to c:\Users\csrik\Desktop\crypto\nft-marketplace\build\contracts
> Compiled successfully using:
   - solc: 0.8.20
```

## Step 5: Deploy Contracts to Ganache

Deploy the contracts to your local Ganache blockchain:

```bash
npm run migrate
```

Or:

```bash
truffle migrate
```

**Expected Output**:
```
Deploying contracts...
Network: development
Deployer account: 0x...
Fee recipient: 0x...
Platform fee: 2.5 %

1. Deploying NFTContract...
NFTContract deployed at: 0x...

2. Deploying Marketplace...
Marketplace deployed at: 0x...

3. Deploying Auction...
Auction deployed at: 0x...

=== Deployment Summary ===
NFTContract: 0x...
Marketplace: 0x...
Auction: 0x...
========================
```

**Important**: Save these contract addresses! You'll need them for interacting with the contracts.

## Step 6: Verify Deployment

### Option A: Using Truffle Console

Open the Truffle console:

```bash
npm run console
```

Or:

```bash
truffle console
```

Inside the console, verify the contracts:

```javascript
// Get deployed instances
const nft = await NFTContract.deployed()
const marketplace = await Marketplace.deployed()
const auction = await Auction.deployed()

// Check contract addresses
nft.address
marketplace.address
auction.address

// Check NFT contract name
await nft.name()
// Should return: "NFT Marketplace Token"

// Check NFT contract symbol
await nft.symbol()
// Should return: "NFTM"

// Check marketplace platform fee
(await marketplace.platformFee()).toString()
// Should return: "250" (2.5%)

// Exit console
.exit
```

### Option B: Check in Ganache

1. Open Ganache
2. Go to the "Blocks" tab
3. You should see several blocks created (from contract deployment)
4. Go to the "Transactions" tab
5. You should see deployment transactions

## Step 7: Interact with Contracts (Optional)

Try minting an NFT using Truffle console:

```bash
truffle console
```

```javascript
// Get accounts
const accounts = await web3.eth.getAccounts()
const owner = accounts[0]

// Get NFT contract
const nft = await NFTContract.deployed()

// Mint an NFT
const result = await nft.mintNFT(
  owner,
  "ipfs://QmTestMetadata123",
  owner,
  500, // 5% royalty
  { from: owner }
)

// Get token ID from event
const tokenId = result.logs[0].args.tokenId.toString()
console.log("Minted NFT with token ID:", tokenId)

// Verify ownership
const tokenOwner = await nft.ownerOf(tokenId)
console.log("Token owner:", tokenOwner)
console.log("Matches minter:", tokenOwner === owner)

// Get token URI
const uri = await nft.tokenURI(tokenId)
console.log("Token URI:", uri)
```

## Troubleshooting

### Issue: "Error: Could not connect to your Ethereum client"

**Solution**: 
- Ensure Ganache is running
- Check that the port in `truffle-config.js` matches Ganache (7545 or 8545)
- Verify the network configuration

### Issue: "Error: Exceeds block gas limit"

**Solution**:
- Increase the gas limit in `truffle-config.js`
- Or in Ganache GUI: Settings → Server → Gas Limit

### Issue: "Error: Returned error: VM Exception while processing transaction: revert"

**Solution**:
- Check the error message for specific revert reason
- Ensure you're using the correct account
- Verify contract state and requirements

### Issue: Compilation errors

**Solution**:
- Ensure you have the correct Solidity version (0.8.20)
- Run `npm install` to ensure all dependencies are installed
- Delete `build` folder and recompile: `rm -rf build && truffle compile`

## Next Steps

Now that your smart contracts are deployed and working:

1. ✅ Run the test suite (see [TESTING.md](file:///c:/Users/csrik/Desktop/crypto/nft-marketplace/contracts/TESTING.md))
2. ✅ Experiment with contract interactions via Truffle console
3. ✅ Move on to Phase 2: Backend REST API Layer (FastAPI)

## Useful Commands

```bash
# Compile contracts
npm run compile

# Deploy contracts
npm run migrate

# Deploy with reset (redeploy all)
npm run migrate:reset

# Open Truffle console
npm run console

# Run tests
npm test
```

## Important Notes

- **Never commit private keys** to version control
- Ganache accounts are for **development only**
- Each time you restart Ganache, you'll need to redeploy contracts
- MetaMask may need to be reset if you restart Ganache (Settings → Advanced → Reset Account)
