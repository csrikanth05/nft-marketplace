const NFTContract = artifacts.require("NFTContract");
const { expect } = require("chai");

contract("NFTContract", (accounts) => {
    let nftContract;
    const [owner, user1, user2, royaltyReceiver] = accounts;

    beforeEach(async () => {
        nftContract = await NFTContract.new({ from: owner });
    });

    describe("Deployment", () => {
        it("should deploy with correct name and symbol", async () => {
            const name = await nftContract.name();
            const symbol = await nftContract.symbol();

            expect(name).to.equal("NFT Marketplace Token");
            expect(symbol).to.equal("NFTM");
        });

        it("should set the correct owner", async () => {
            const contractOwner = await nftContract.owner();
            expect(contractOwner).to.equal(owner);
        });
    });

    describe("Minting", () => {
        it("should mint NFT with correct metadata", async () => {
            const tokenURI = "ipfs://QmTest123";
            const royaltyFee = 500; // 5%

            const result = await nftContract.mintNFT(
                user1,
                tokenURI,
                royaltyReceiver,
                royaltyFee,
                { from: user1 }
            );

            const tokenId = result.logs[0].args.tokenId.toNumber();
            expect(tokenId).to.equal(1);

            const owner = await nftContract.ownerOf(tokenId);
            expect(owner).to.equal(user1);

            const uri = await nftContract.tokenURI(tokenId);
            expect(uri).to.equal(tokenURI);
        });

        it("should emit NFTMinted event", async () => {
            const tokenURI = "ipfs://QmTest123";
            const result = await nftContract.mintNFT(
                user1,
                tokenURI,
                royaltyReceiver,
                500,
                { from: user1 }
            );

            const event = result.logs.find(log => log.event === "NFTMinted");
            expect(event).to.exist;
            expect(event.args.creator).to.equal(user1);
            expect(event.args.tokenURI).to.equal(tokenURI);
        });

        it("should set royalty information correctly", async () => {
            const tokenURI = "ipfs://QmTest123";
            const royaltyFee = 500; // 5%
            const salePrice = web3.utils.toWei("1", "ether");

            const result = await nftContract.mintNFT(
                user1,
                tokenURI,
                royaltyReceiver,
                royaltyFee,
                { from: user1 }
            );

            const tokenId = result.logs[0].args.tokenId.toNumber();

            const royaltyInfo = await nftContract.royaltyInfo(tokenId, salePrice);
            expect(royaltyInfo[0]).to.equal(royaltyReceiver);

            const expectedRoyalty = (salePrice * royaltyFee) / 10000;
            expect(royaltyInfo[1].toString()).to.equal(expectedRoyalty.toString());
        });

        it("should reject minting to zero address", async () => {
            try {
                await nftContract.mintNFT(
                    "0x0000000000000000000000000000000000000000",
                    "ipfs://QmTest",
                    royaltyReceiver,
                    500,
                    { from: user1 }
                );
                expect.fail("Should have thrown an error");
            } catch (error) {
                expect(error.message).to.include("Cannot mint to zero address");
            }
        });

        it("should reject empty URI", async () => {
            try {
                await nftContract.mintNFT(
                    user1,
                    "",
                    royaltyReceiver,
                    500,
                    { from: user1 }
                );
                expect.fail("Should have thrown an error");
            } catch (error) {
                expect(error.message).to.include("URI cannot be empty");
            }
        });

        it("should reject royalty fee over 100%", async () => {
            try {
                await nftContract.mintNFT(
                    user1,
                    "ipfs://QmTest",
                    royaltyReceiver,
                    10001, // Over 100%
                    { from: user1 }
                );
                expect.fail("Should have thrown an error");
            } catch (error) {
                expect(error.message).to.include("Royalty fee too high");
            }
        });

        it("should increment token IDs correctly", async () => {
            await nftContract.mintNFT(user1, "ipfs://QmTest1", royaltyReceiver, 500, { from: user1 });
            await nftContract.mintNFT(user2, "ipfs://QmTest2", royaltyReceiver, 500, { from: user2 });

            const currentTokenId = await nftContract.getCurrentTokenId();
            expect(currentTokenId.toNumber()).to.equal(2);
        });
    });

    describe("Token Management", () => {
        let tokenId;

        beforeEach(async () => {
            const result = await nftContract.mintNFT(
                user1,
                "ipfs://QmTest",
                royaltyReceiver,
                500,
                { from: user1 }
            );
            tokenId = result.logs[0].args.tokenId.toNumber();
        });

        it("should transfer NFT correctly", async () => {
            await nftContract.transferFrom(user1, user2, tokenId, { from: user1 });

            const newOwner = await nftContract.ownerOf(tokenId);
            expect(newOwner).to.equal(user2);
        });

        it("should burn NFT by owner", async () => {
            await nftContract.burn(tokenId, { from: user1 });

            try {
                await nftContract.ownerOf(tokenId);
                expect.fail("Should have thrown an error");
            } catch (error) {
                expect(error.message).to.include("invalid opcode");
            }
        });

        it("should emit NFTBurned event", async () => {
            const result = await nftContract.burn(tokenId, { from: user1 });

            const event = result.logs.find(log => log.event === "NFTBurned");
            expect(event).to.exist;
            expect(event.args.tokenId.toNumber()).to.equal(tokenId);
            expect(event.args.owner).to.equal(user1);
        });

        it("should reject burn by non-owner", async () => {
            try {
                await nftContract.burn(tokenId, { from: user2 });
                expect.fail("Should have thrown an error");
            } catch (error) {
                expect(error.message).to.include("Only owner can burn");
            }
        });

        it("should return creator of token", async () => {
            const creator = await nftContract.creatorOf(tokenId);
            expect(creator).to.equal(user1);
        });

        it("should return tokens owned by address", async () => {
            await nftContract.mintNFT(user1, "ipfs://QmTest2", royaltyReceiver, 500, { from: user1 });
            await nftContract.mintNFT(user1, "ipfs://QmTest3", royaltyReceiver, 500, { from: user1 });

            const tokens = await nftContract.tokensOfOwner(user1);
            expect(tokens.length).to.equal(3);
        });
    });

    describe("ERC721 Compliance", () => {
        it("should support ERC721 interface", async () => {
            const interfaceId = "0x80ac58cd"; // ERC721 interface ID
            const supported = await nftContract.supportsInterface(interfaceId);
            expect(supported).to.be.true;
        });

        it("should support ERC2981 interface", async () => {
            const interfaceId = "0x2a55205a"; // ERC2981 interface ID
            const supported = await nftContract.supportsInterface(interfaceId);
            expect(supported).to.be.true;
        });
    });
});
