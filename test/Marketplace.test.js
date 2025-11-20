const NFTContract = artifacts.require("NFTContract");
const Marketplace = artifacts.require("Marketplace");
const { expect } = require("chai");

contract("Marketplace", (accounts) => {
    let nftContract;
    let marketplace;
    const [owner, seller, buyer, feeRecipient, royaltyReceiver] = accounts;
    const platformFee = 250; // 2.5%

    beforeEach(async () => {
        nftContract = await NFTContract.new({ from: owner });
        marketplace = await Marketplace.new(platformFee, feeRecipient, { from: owner });
    });

    describe("Deployment", () => {
        it("should deploy with correct platform fee", async () => {
            const fee = await marketplace.platformFee();
            expect(fee.toNumber()).to.equal(platformFee);
        });

        it("should deploy with correct fee recipient", async () => {
            const recipient = await marketplace.feeRecipient();
            expect(recipient).to.equal(feeRecipient);
        });

        it("should reject deployment with fee over 100%", async () => {
            try {
                await Marketplace.new(10001, feeRecipient, { from: owner });
                expect.fail("Should have thrown an error");
            } catch (error) {
                expect(error.message).to.include("Fee too high");
            }
        });
    });

    describe("Listing NFTs", () => {
        let tokenId;
        const price = web3.utils.toWei("1", "ether");

        beforeEach(async () => {
            const result = await nftContract.mintNFT(
                seller,
                "ipfs://QmTest",
                royaltyReceiver,
                500,
                { from: seller }
            );
            tokenId = result.logs[0].args.tokenId.toNumber();
        });

        it("should list NFT successfully", async () => {
            await nftContract.approve(marketplace.address, tokenId, { from: seller });

            const result = await marketplace.listNFT(
                nftContract.address,
                tokenId,
                price,
                { from: seller }
            );

            const listingId = result.logs[0].args.listingId.toNumber();
            expect(listingId).to.equal(1);

            const listing = await marketplace.getListing(listingId);
            expect(listing.seller).to.equal(seller);
            expect(listing.tokenId.toNumber()).to.equal(tokenId);
            expect(listing.price.toString()).to.equal(price);
            expect(listing.active).to.be.true;
        });

        it("should emit NFTListed event", async () => {
            await nftContract.approve(marketplace.address, tokenId, { from: seller });

            const result = await marketplace.listNFT(
                nftContract.address,
                tokenId,
                price,
                { from: seller }
            );

            const event = result.logs.find(log => log.event === "NFTListed");
            expect(event).to.exist;
            expect(event.args.seller).to.equal(seller);
            expect(event.args.tokenId.toNumber()).to.equal(tokenId);
        });

        it("should reject listing without approval", async () => {
            try {
                await marketplace.listNFT(
                    nftContract.address,
                    tokenId,
                    price,
                    { from: seller }
                );
                expect.fail("Should have thrown an error");
            } catch (error) {
                expect(error.message).to.include("Marketplace not approved");
            }
        });

        it("should reject listing by non-owner", async () => {
            await nftContract.approve(marketplace.address, tokenId, { from: seller });

            try {
                await marketplace.listNFT(
                    nftContract.address,
                    tokenId,
                    price,
                    { from: buyer }
                );
                expect.fail("Should have thrown an error");
            } catch (error) {
                expect(error.message).to.include("Not the owner");
            }
        });

        it("should reject listing with zero price", async () => {
            await nftContract.approve(marketplace.address, tokenId, { from: seller });

            try {
                await marketplace.listNFT(
                    nftContract.address,
                    tokenId,
                    0,
                    { from: seller }
                );
                expect.fail("Should have thrown an error");
            } catch (error) {
                expect(error.message).to.include("Price must be greater than 0");
            }
        });
    });

    describe("Buying NFTs", () => {
        let tokenId;
        let listingId;
        const price = web3.utils.toWei("1", "ether");

        beforeEach(async () => {
            const mintResult = await nftContract.mintNFT(
                seller,
                "ipfs://QmTest",
                royaltyReceiver,
                500, // 5% royalty
                { from: seller }
            );
            tokenId = mintResult.logs[0].args.tokenId.toNumber();

            await nftContract.approve(marketplace.address, tokenId, { from: seller });

            const listResult = await marketplace.listNFT(
                nftContract.address,
                tokenId,
                price,
                { from: seller }
            );
            listingId = listResult.logs[0].args.listingId.toNumber();
        });

        it("should buy NFT successfully", async () => {
            const sellerBalanceBefore = BigInt(await web3.eth.getBalance(seller));
            const feeRecipientBalanceBefore = BigInt(await web3.eth.getBalance(feeRecipient));
            const royaltyReceiverBalanceBefore = BigInt(await web3.eth.getBalance(royaltyReceiver));

            await marketplace.buyNFT(listingId, { from: buyer, value: price });

            const newOwner = await nftContract.ownerOf(tokenId);
            expect(newOwner).to.equal(buyer);

            const listing = await marketplace.getListing(listingId);
            expect(listing.active).to.be.false;

            // Check balances increased
            const sellerBalanceAfter = BigInt(await web3.eth.getBalance(seller));
            const feeRecipientBalanceAfter = BigInt(await web3.eth.getBalance(feeRecipient));
            const royaltyReceiverBalanceAfter = BigInt(await web3.eth.getBalance(royaltyReceiver));

            expect(sellerBalanceAfter > sellerBalanceBefore).to.be.true;
            expect(feeRecipientBalanceAfter > feeRecipientBalanceBefore).to.be.true;
            expect(royaltyReceiverBalanceAfter > royaltyReceiverBalanceBefore).to.be.true;
        });

        it("should emit NFTSold event", async () => {
            const result = await marketplace.buyNFT(listingId, { from: buyer, value: price });

            const event = result.logs.find(log => log.event === "NFTSold");
            expect(event).to.exist;
            expect(event.args.buyer).to.equal(buyer);
            expect(event.args.seller).to.equal(seller);
        });

        it("should reject purchase with insufficient payment", async () => {
            const insufficientPrice = web3.utils.toWei("0.5", "ether");

            try {
                await marketplace.buyNFT(listingId, { from: buyer, value: insufficientPrice });
                expect.fail("Should have thrown an error");
            } catch (error) {
                expect(error.message).to.include("Insufficient payment");
            }
        });

        it("should reject seller buying own NFT", async () => {
            try {
                await marketplace.buyNFT(listingId, { from: seller, value: price });
                expect.fail("Should have thrown an error");
            } catch (error) {
                expect(error.message).to.include("Cannot buy your own NFT");
            }
        });

        it("should refund excess payment", async () => {
            const excessPrice = web3.utils.toWei("2", "ether");
            const buyerBalanceBefore = BigInt(await web3.eth.getBalance(buyer));

            const result = await marketplace.buyNFT(listingId, { from: buyer, value: excessPrice });

            const buyerBalanceAfter = BigInt(await web3.eth.getBalance(buyer));
            const gasUsed = BigInt(result.receipt.gasUsed);
            const gasPrice = BigInt((await web3.eth.getTransaction(result.tx)).gasPrice);
            const gasCost = gasUsed * gasPrice;

            const expectedBalance = buyerBalanceBefore - BigInt(price) - gasCost;

            // Allow small difference due to gas estimation
            const difference = buyerBalanceAfter > expectedBalance ?
                buyerBalanceAfter - expectedBalance :
                expectedBalance - buyerBalanceAfter;

            expect(difference < BigInt(web3.utils.toWei("0.01", "ether"))).to.be.true;
        });
    });

    describe("Canceling Listings", () => {
        let tokenId;
        let listingId;
        const price = web3.utils.toWei("1", "ether");

        beforeEach(async () => {
            const mintResult = await nftContract.mintNFT(
                seller,
                "ipfs://QmTest",
                royaltyReceiver,
                500,
                { from: seller }
            );
            tokenId = mintResult.logs[0].args.tokenId.toNumber();

            await nftContract.approve(marketplace.address, tokenId, { from: seller });

            const listResult = await marketplace.listNFT(
                nftContract.address,
                tokenId,
                price,
                { from: seller }
            );
            listingId = listResult.logs[0].args.listingId.toNumber();
        });

        it("should cancel listing successfully", async () => {
            await marketplace.cancelListing(listingId, { from: seller });

            const listing = await marketplace.getListing(listingId);
            expect(listing.active).to.be.false;
        });

        it("should emit ListingCancelled event", async () => {
            const result = await marketplace.cancelListing(listingId, { from: seller });

            const event = result.logs.find(log => log.event === "ListingCancelled");
            expect(event).to.exist;
            expect(event.args.listingId.toNumber()).to.equal(listingId);
        });

        it("should reject cancellation by non-seller", async () => {
            try {
                await marketplace.cancelListing(listingId, { from: buyer });
                expect.fail("Should have thrown an error");
            } catch (error) {
                expect(error.message).to.include("Not the seller");
            }
        });
    });

    describe("Admin Functions", () => {
        it("should update platform fee", async () => {
            const newFee = 500; // 5%
            await marketplace.updatePlatformFee(newFee, { from: owner });

            const fee = await marketplace.platformFee();
            expect(fee.toNumber()).to.equal(newFee);
        });

        it("should update fee recipient", async () => {
            const newRecipient = buyer;
            await marketplace.updateFeeRecipient(newRecipient, { from: owner });

            const recipient = await marketplace.feeRecipient();
            expect(recipient).to.equal(newRecipient);
        });

        it("should reject fee update by non-owner", async () => {
            try {
                await marketplace.updatePlatformFee(500, { from: buyer });
                expect.fail("Should have thrown an error");
            } catch (error) {
                expect(error.message).to.include("caller is not the owner");
            }
        });
    });
});
