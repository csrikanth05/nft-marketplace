const NFTContract = artifacts.require("NFTContract");
const Auction = artifacts.require("Auction");
const { expect } = require("chai");

contract("Auction", (accounts) => {
    let nftContract;
    let auction;
    const [owner, seller, bidder1, bidder2, feeRecipient, royaltyReceiver] = accounts;
    const platformFee = 250; // 2.5%

    beforeEach(async () => {
        nftContract = await NFTContract.new({ from: owner });
        auction = await Auction.new(platformFee, feeRecipient, { from: owner });
    });

    describe("Deployment", () => {
        it("should deploy with correct platform fee", async () => {
            const fee = await auction.platformFee();
            expect(fee.toNumber()).to.equal(platformFee);
        });

        it("should deploy with correct fee recipient", async () => {
            const recipient = await auction.feeRecipient();
            expect(recipient).to.equal(feeRecipient);
        });
    });

    describe("Creating Auctions", () => {
        let tokenId;
        const reservePrice = web3.utils.toWei("1", "ether");

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

        it("should create auction successfully", async () => {
            await nftContract.approve(auction.address, tokenId, { from: seller });

            const currentTime = Math.floor(Date.now() / 1000);
            const startTime = currentTime + 60; // Start in 1 minute
            const endTime = startTime + 3600; // End in 1 hour

            const result = await auction.createAuction(
                nftContract.address,
                tokenId,
                startTime,
                endTime,
                reservePrice,
                { from: seller }
            );

            const auctionId = result.logs[0].args.auctionId.toNumber();
            expect(auctionId).to.equal(1);

            const auctionData = await auction.getAuction(auctionId);
            expect(auctionData.seller).to.equal(seller);
            expect(auctionData.tokenId.toNumber()).to.equal(tokenId);
            expect(auctionData.reservePrice.toString()).to.equal(reservePrice);
            expect(auctionData.active).to.be.true;
        });

        it("should emit AuctionCreated event", async () => {
            await nftContract.approve(auction.address, tokenId, { from: seller });

            const currentTime = Math.floor(Date.now() / 1000);
            const startTime = currentTime + 60;
            const endTime = startTime + 3600;

            const result = await auction.createAuction(
                nftContract.address,
                tokenId,
                startTime,
                endTime,
                reservePrice,
                { from: seller }
            );

            const event = result.logs.find(log => log.event === "AuctionCreated");
            expect(event).to.exist;
            expect(event.args.seller).to.equal(seller);
        });

        it("should reject auction with past start time", async () => {
            await nftContract.approve(auction.address, tokenId, { from: seller });

            const pastTime = Math.floor(Date.now() / 1000) - 3600;
            const endTime = pastTime + 7200;

            try {
                await auction.createAuction(
                    nftContract.address,
                    tokenId,
                    pastTime,
                    endTime,
                    reservePrice,
                    { from: seller }
                );
                expect.fail("Should have thrown an error");
            } catch (error) {
                expect(error.message).to.include("Start time must be in future");
            }
        });

        it("should reject auction with end time before start time", async () => {
            await nftContract.approve(auction.address, tokenId, { from: seller });

            const currentTime = Math.floor(Date.now() / 1000);
            const startTime = currentTime + 3600;
            const endTime = startTime - 1800;

            try {
                await auction.createAuction(
                    nftContract.address,
                    tokenId,
                    startTime,
                    endTime,
                    reservePrice,
                    { from: seller }
                );
                expect.fail("Should have thrown an error");
            } catch (error) {
                expect(error.message).to.include("End time must be after start time");
            }
        });
    });

    describe("Bidding", () => {
        let tokenId;
        let auctionId;
        const reservePrice = web3.utils.toWei("1", "ether");

        beforeEach(async () => {
            const mintResult = await nftContract.mintNFT(
                seller,
                "ipfs://QmTest",
                royaltyReceiver,
                500,
                { from: seller }
            );
            tokenId = mintResult.logs[0].args.tokenId.toNumber();

            await nftContract.approve(auction.address, tokenId, { from: seller });

            // Create auction that starts immediately
            const currentTime = Math.floor(Date.now() / 1000);
            const startTime = currentTime - 10; // Started 10 seconds ago
            const endTime = currentTime + 3600; // Ends in 1 hour

            const auctionResult = await auction.createAuction(
                nftContract.address,
                tokenId,
                startTime,
                endTime,
                reservePrice,
                { from: seller }
            );
            auctionId = auctionResult.logs[0].args.auctionId.toNumber();
        });

        it("should place bid successfully", async () => {
            const bidAmount = web3.utils.toWei("1.5", "ether");

            await auction.placeBid(auctionId, { from: bidder1, value: bidAmount });

            const auctionData = await auction.getAuction(auctionId);
            expect(auctionData.highestBidder).to.equal(bidder1);
            expect(auctionData.highestBid.toString()).to.equal(bidAmount);
        });

        it("should emit BidPlaced event", async () => {
            const bidAmount = web3.utils.toWei("1.5", "ether");

            const result = await auction.placeBid(auctionId, { from: bidder1, value: bidAmount });

            const event = result.logs.find(log => log.event === "BidPlaced");
            expect(event).to.exist;
            expect(event.args.bidder).to.equal(bidder1);
            expect(event.args.amount.toString()).to.equal(bidAmount);
        });

        it("should refund previous highest bidder", async () => {
            const bid1 = web3.utils.toWei("1.5", "ether");
            const bid2 = web3.utils.toWei("2", "ether");

            await auction.placeBid(auctionId, { from: bidder1, value: bid1 });
            await auction.placeBid(auctionId, { from: bidder2, value: bid2 });

            const pendingReturn = await auction.pendingReturns(auctionId, bidder1);
            expect(pendingReturn.toString()).to.equal(bid1);
        });

        it("should allow withdrawal of refunded bid", async () => {
            const bid1 = web3.utils.toWei("1.5", "ether");
            const bid2 = web3.utils.toWei("2", "ether");

            await auction.placeBid(auctionId, { from: bidder1, value: bid1 });
            await auction.placeBid(auctionId, { from: bidder2, value: bid2 });

            const balanceBefore = BigInt(await web3.eth.getBalance(bidder1));
            const result = await auction.withdraw(auctionId, { from: bidder1 });
            const balanceAfter = BigInt(await web3.eth.getBalance(bidder1));

            const gasUsed = BigInt(result.receipt.gasUsed);
            const gasPrice = BigInt((await web3.eth.getTransaction(result.tx)).gasPrice);
            const gasCost = gasUsed * gasPrice;

            const expectedBalance = balanceBefore + BigInt(bid1) - gasCost;

            // Allow small difference due to gas estimation
            const difference = balanceAfter > expectedBalance ?
                balanceAfter - expectedBalance :
                expectedBalance - balanceAfter;

            expect(difference < BigInt(web3.utils.toWei("0.01", "ether"))).to.be.true;
        });

        it("should reject bid below reserve price", async () => {
            const lowBid = web3.utils.toWei("0.5", "ether");

            try {
                await auction.placeBid(auctionId, { from: bidder1, value: lowBid });
                expect.fail("Should have thrown an error");
            } catch (error) {
                expect(error.message).to.include("Bid below reserve price");
            }
        });

        it("should reject bid not higher than current highest", async () => {
            const bid1 = web3.utils.toWei("1.5", "ether");
            const bid2 = web3.utils.toWei("1.5", "ether");

            await auction.placeBid(auctionId, { from: bidder1, value: bid1 });

            try {
                await auction.placeBid(auctionId, { from: bidder2, value: bid2 });
                expect.fail("Should have thrown an error");
            } catch (error) {
                expect(error.message).to.include("Bid too low");
            }
        });

        it("should reject bid from seller", async () => {
            const bidAmount = web3.utils.toWei("1.5", "ether");

            try {
                await auction.placeBid(auctionId, { from: seller, value: bidAmount });
                expect.fail("Should have thrown an error");
            } catch (error) {
                expect(error.message).to.include("Seller cannot bid");
            }
        });
    });

    describe("Ending Auctions", () => {
        let tokenId;
        let auctionId;
        const reservePrice = web3.utils.toWei("1", "ether");

        beforeEach(async () => {
            const mintResult = await nftContract.mintNFT(
                seller,
                "ipfs://QmTest",
                royaltyReceiver,
                500,
                { from: seller }
            );
            tokenId = mintResult.logs[0].args.tokenId.toNumber();

            await nftContract.approve(auction.address, tokenId, { from: seller });

            // Create auction that ends soon
            const currentTime = Math.floor(Date.now() / 1000);
            const startTime = currentTime - 3600; // Started 1 hour ago
            const endTime = currentTime - 10; // Ended 10 seconds ago

            const auctionResult = await auction.createAuction(
                nftContract.address,
                tokenId,
                startTime,
                endTime,
                reservePrice,
                { from: seller }
            );
            auctionId = auctionResult.logs[0].args.auctionId.toNumber();
        });

        it("should end auction with winner", async () => {
            // Need to create new auction that we can bid on then end
            const mintResult = await nftContract.mintNFT(
                seller,
                "ipfs://QmTest2",
                royaltyReceiver,
                500,
                { from: seller }
            );
            const newTokenId = mintResult.logs[0].args.tokenId.toNumber();

            await nftContract.approve(auction.address, newTokenId, { from: seller });

            const currentTime = Math.floor(Date.now() / 1000);
            const startTime = currentTime - 100;
            const endTime = currentTime + 2; // Ends in 2 seconds

            const auctionResult = await auction.createAuction(
                nftContract.address,
                newTokenId,
                startTime,
                endTime,
                reservePrice,
                { from: seller }
            );
            const newAuctionId = auctionResult.logs[0].args.auctionId.toNumber();

            // Place bid
            const bidAmount = web3.utils.toWei("1.5", "ether");
            await auction.placeBid(newAuctionId, { from: bidder1, value: bidAmount });

            // Wait for auction to end
            await new Promise(resolve => setTimeout(resolve, 3000));

            // End auction
            await auction.endAuction(newAuctionId, { from: seller });

            const newOwner = await nftContract.ownerOf(newTokenId);
            expect(newOwner).to.equal(bidder1);

            const auctionData = await auction.getAuction(newAuctionId);
            expect(auctionData.ended).to.be.true;
            expect(auctionData.active).to.be.false;
        });

        it("should emit AuctionEnded event", async () => {
            const result = await auction.endAuction(auctionId, { from: seller });

            const event = result.logs.find(log => log.event === "AuctionEnded");
            expect(event).to.exist;
        });
    });

    describe("Canceling Auctions", () => {
        let tokenId;
        let auctionId;
        const reservePrice = web3.utils.toWei("1", "ether");

        beforeEach(async () => {
            const mintResult = await nftContract.mintNFT(
                seller,
                "ipfs://QmTest",
                royaltyReceiver,
                500,
                { from: seller }
            );
            tokenId = mintResult.logs[0].args.tokenId.toNumber();

            await nftContract.approve(auction.address, tokenId, { from: seller });

            const currentTime = Math.floor(Date.now() / 1000);
            const startTime = currentTime + 60;
            const endTime = startTime + 3600;

            const auctionResult = await auction.createAuction(
                nftContract.address,
                tokenId,
                startTime,
                endTime,
                reservePrice,
                { from: seller }
            );
            auctionId = auctionResult.logs[0].args.auctionId.toNumber();
        });

        it("should cancel auction without bids", async () => {
            await auction.cancelAuction(auctionId, { from: seller });

            const auctionData = await auction.getAuction(auctionId);
            expect(auctionData.active).to.be.false;
            expect(auctionData.ended).to.be.true;
        });

        it("should emit AuctionCancelled event", async () => {
            const result = await auction.cancelAuction(auctionId, { from: seller });

            const event = result.logs.find(log => log.event === "AuctionCancelled");
            expect(event).to.exist;
        });

        it("should reject cancellation by non-seller", async () => {
            try {
                await auction.cancelAuction(auctionId, { from: bidder1 });
                expect.fail("Should have thrown an error");
            } catch (error) {
                expect(error.message).to.include("Not the seller");
            }
        });
    });

    describe("Admin Functions", () => {
        it("should update platform fee", async () => {
            const newFee = 500;
            await auction.updatePlatformFee(newFee, { from: owner });

            const fee = await auction.platformFee();
            expect(fee.toNumber()).to.equal(newFee);
        });

        it("should update fee recipient", async () => {
            const newRecipient = bidder1;
            await auction.updateFeeRecipient(newRecipient, { from: owner });

            const recipient = await auction.feeRecipient();
            expect(recipient).to.equal(newRecipient);
        });
    });
});
