const NFTContract = artifacts.require("NFTContract");
const Marketplace = artifacts.require("Marketplace");
const Auction = artifacts.require("Auction");

module.exports = async function (deployer, network, accounts) {
    // Platform fee: 2.5% (250 basis points)
    const PLATFORM_FEE = 250;

    // Fee recipient (use first account as default)
    const feeRecipient = accounts[0];

    console.log("Deploying contracts...");
    console.log("Network:", network);
    console.log("Deployer account:", accounts[0]);
    console.log("Fee recipient:", feeRecipient);
    console.log("Platform fee:", PLATFORM_FEE / 100, "%");

    // Deploy NFT Contract
    console.log("\n1. Deploying NFTContract...");
    await deployer.deploy(NFTContract);
    const nftContract = await NFTContract.deployed();
    console.log("NFTContract deployed at:", nftContract.address);

    // Deploy Marketplace
    console.log("\n2. Deploying Marketplace...");
    await deployer.deploy(Marketplace, PLATFORM_FEE, feeRecipient);
    const marketplace = await Marketplace.deployed();
    console.log("Marketplace deployed at:", marketplace.address);

    // Deploy Auction
    console.log("\n3. Deploying Auction...");
    await deployer.deploy(Auction, PLATFORM_FEE, feeRecipient);
    const auction = await Auction.deployed();
    console.log("Auction deployed at:", auction.address);

    console.log("\n=== Deployment Summary ===");
    console.log("NFTContract:", nftContract.address);
    console.log("Marketplace:", marketplace.address);
    console.log("Auction:", auction.address);
    console.log("========================\n");
};
