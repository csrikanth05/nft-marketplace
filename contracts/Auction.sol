// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/IERC721.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/common/ERC2981.sol";

/**
 * @title Auction
 * @dev NFT auction contract with bidding, automatic transfers, and royalty support
 */
contract Auction is ReentrancyGuard, Ownable {
    
    // Auction structure
    struct AuctionData {
        address seller;
        address nftContract;
        uint256 tokenId;
        uint256 startTime;
        uint256 endTime;
        uint256 reservePrice;
        address highestBidder;
        uint256 highestBid;
        bool active;
        bool ended;
    }
    
    // Platform fee (in basis points, e.g., 250 = 2.5%)
    uint256 public platformFee;
    
    // Address to receive platform fees
    address public feeRecipient;
    
    // Auction ID counter
    uint256 private _auctionIdCounter;
    
    // Mapping from auction ID to AuctionData
    mapping(uint256 => AuctionData) public auctions;
    
    // Mapping from auction ID to bidder to bid amount (for refunds)
    mapping(uint256 => mapping(address => uint256)) public pendingReturns;
    
    // Events
    event AuctionCreated(
        uint256 indexed auctionId,
        address indexed seller,
        address indexed nftContract,
        uint256 tokenId,
        uint256 startTime,
        uint256 endTime,
        uint256 reservePrice
    );
    
    event BidPlaced(
        uint256 indexed auctionId,
        address indexed bidder,
        uint256 amount
    );
    
    event AuctionEnded(
        uint256 indexed auctionId,
        address indexed winner,
        uint256 amount
    );
    
    event AuctionCancelled(uint256 indexed auctionId);
    
    event PlatformFeeUpdated(uint256 newFee);
    
    event FeeRecipientUpdated(address newRecipient);
    
    constructor(uint256 _platformFee, address _feeRecipient) Ownable() {
        require(_platformFee <= 10000, "Fee too high"); // Max 100%
        require(_feeRecipient != address(0), "Invalid fee recipient");
        
        platformFee = _platformFee;
        feeRecipient = _feeRecipient;
        _auctionIdCounter = 1;
    }
    
    /**
     * @dev Create a new auction
     * @param nftContract Address of the NFT contract
     * @param tokenId ID of the token to auction
     * @param startTime Auction start time (unix timestamp)
     * @param endTime Auction end time (unix timestamp)
     * @param reservePrice Minimum price to accept
     * @return auctionId The ID of the created auction
     */
    function createAuction(
        address nftContract,
        uint256 tokenId,
        uint256 startTime,
        uint256 endTime,
        uint256 reservePrice
    ) external nonReentrant returns (uint256) {
        require(startTime >= block.timestamp, "Start time must be in future");
        require(endTime > startTime, "End time must be after start time");
        require(reservePrice > 0, "Reserve price must be greater than 0");
        
        IERC721 nft = IERC721(nftContract);
        require(nft.ownerOf(tokenId) == msg.sender, "Not the owner");
        require(
            nft.isApprovedForAll(msg.sender, address(this)) || 
            nft.getApproved(tokenId) == address(this),
            "Auction contract not approved"
        );
        
        uint256 auctionId = _auctionIdCounter++;
        
        auctions[auctionId] = AuctionData({
            seller: msg.sender,
            nftContract: nftContract,
            tokenId: tokenId,
            startTime: startTime,
            endTime: endTime,
            reservePrice: reservePrice,
            highestBidder: address(0),
            highestBid: 0,
            active: true,
            ended: false
        });
        
        emit AuctionCreated(
            auctionId,
            msg.sender,
            nftContract,
            tokenId,
            startTime,
            endTime,
            reservePrice
        );
        
        return auctionId;
    }
    
    /**
     * @dev Place a bid on an auction
     * @param auctionId ID of the auction to bid on
     */
    function placeBid(uint256 auctionId) external payable nonReentrant {
        AuctionData storage auction = auctions[auctionId];
        
        require(auction.active, "Auction not active");
        require(!auction.ended, "Auction already ended");
        require(block.timestamp >= auction.startTime, "Auction not started");
        require(block.timestamp < auction.endTime, "Auction ended");
        require(msg.sender != auction.seller, "Seller cannot bid");
        require(msg.value > auction.highestBid, "Bid too low");
        require(msg.value >= auction.reservePrice, "Bid below reserve price");
        
        // Refund previous highest bidder
        if (auction.highestBidder != address(0)) {
            pendingReturns[auctionId][auction.highestBidder] += auction.highestBid;
        }
        
        auction.highestBidder = msg.sender;
        auction.highestBid = msg.value;
        
        emit BidPlaced(auctionId, msg.sender, msg.value);
    }
    
    /**
     * @dev End an auction and transfer NFT to winner
     * @param auctionId ID of the auction to end
     */
    function endAuction(uint256 auctionId) external nonReentrant {
        AuctionData storage auction = auctions[auctionId];
        
        require(auction.active, "Auction not active");
        require(!auction.ended, "Auction already ended");
        require(block.timestamp >= auction.endTime, "Auction not yet ended");
        
        auction.ended = true;
        auction.active = false;
        
        IERC721 nft = IERC721(auction.nftContract);
        
        // If there's a winner
        if (auction.highestBidder != address(0)) {
            // Calculate fees
            uint256 platformFeeAmount = (auction.highestBid * platformFee) / 10000;
            uint256 royaltyAmount = 0;
            address royaltyReceiver = address(0);
            
            // Check for ERC2981 royalty support
            if (nft.supportsInterface(type(ERC2981).interfaceId)) {
                (royaltyReceiver, royaltyAmount) = ERC2981(auction.nftContract).royaltyInfo(
                    auction.tokenId,
                    auction.highestBid
                );
            }
            
            uint256 sellerProceeds = auction.highestBid - platformFeeAmount - royaltyAmount;
            
            // Transfer NFT to winner
            nft.safeTransferFrom(auction.seller, auction.highestBidder, auction.tokenId);
            
            // Transfer payments
            payable(feeRecipient).transfer(platformFeeAmount);
            
            if (royaltyAmount > 0 && royaltyReceiver != address(0)) {
                payable(royaltyReceiver).transfer(royaltyAmount);
            }
            
            payable(auction.seller).transfer(sellerProceeds);
            
            emit AuctionEnded(auctionId, auction.highestBidder, auction.highestBid);
        } else {
            // No bids, auction failed
            emit AuctionEnded(auctionId, address(0), 0);
        }
    }
    
    /**
     * @dev Cancel an auction (only if no bids)
     * @param auctionId ID of the auction to cancel
     */
    function cancelAuction(uint256 auctionId) external nonReentrant {
        AuctionData storage auction = auctions[auctionId];
        
        require(auction.active, "Auction not active");
        require(!auction.ended, "Auction already ended");
        require(auction.seller == msg.sender, "Not the seller");
        require(auction.highestBidder == address(0), "Cannot cancel with bids");
        
        auction.active = false;
        auction.ended = true;
        
        emit AuctionCancelled(auctionId);
    }
    
    /**
     * @dev Withdraw a refunded bid
     * @param auctionId ID of the auction
     */
    function withdraw(uint256 auctionId) external nonReentrant {
        uint256 amount = pendingReturns[auctionId][msg.sender];
        require(amount > 0, "No funds to withdraw");
        
        pendingReturns[auctionId][msg.sender] = 0;
        payable(msg.sender).transfer(amount);
    }
    
    /**
     * @dev Update platform fee (only owner)
     * @param newFee New platform fee in basis points
     */
    function updatePlatformFee(uint256 newFee) external onlyOwner {
        require(newFee <= 10000, "Fee too high");
        platformFee = newFee;
        emit PlatformFeeUpdated(newFee);
    }
    
    /**
     * @dev Update fee recipient (only owner)
     * @param newRecipient New fee recipient address
     */
    function updateFeeRecipient(address newRecipient) external onlyOwner {
        require(newRecipient != address(0), "Invalid recipient");
        feeRecipient = newRecipient;
        emit FeeRecipientUpdated(newRecipient);
    }
    
    /**
     * @dev Get auction details
     * @param auctionId ID of the auction
     * @return Auction details
     */
    function getAuction(uint256 auctionId) external view returns (AuctionData memory) {
        return auctions[auctionId];
    }
    
    /**
     * @dev Get current auction ID counter
     * @return Current counter value
     */
    function getCurrentAuctionId() external view returns (uint256) {
        return _auctionIdCounter - 1;
    }
}
