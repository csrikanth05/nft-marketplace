// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/IERC721.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/common/ERC2981.sol";

/**
 * @title Marketplace
 * @dev NFT marketplace for buying and selling NFTs with platform fees
 */
contract Marketplace is ReentrancyGuard, Ownable {
    
    // Listing structure
    struct Listing {
        address seller;
        address nftContract;
        uint256 tokenId;
        uint256 price;
        bool active;
    }
    
    // Platform fee (in basis points, e.g., 250 = 2.5%)
    uint256 public platformFee;
    
    // Address to receive platform fees
    address public feeRecipient;
    
    // Listing ID counter
    uint256 private _listingIdCounter;
    
    // Mapping from listing ID to Listing
    mapping(uint256 => Listing) public listings;
    
    // Events
    event NFTListed(
        uint256 indexed listingId,
        address indexed seller,
        address indexed nftContract,
        uint256 tokenId,
        uint256 price
    );
    
    event NFTSold(
        uint256 indexed listingId,
        address indexed buyer,
        address indexed seller,
        address nftContract,
        uint256 tokenId,
        uint256 price
    );
    
    event ListingCancelled(uint256 indexed listingId);
    
    event PlatformFeeUpdated(uint256 newFee);
    
    event FeeRecipientUpdated(address newRecipient);
    
    constructor(uint256 _platformFee, address _feeRecipient) Ownable() {
        require(_platformFee <= 10000, "Fee too high"); // Max 100%
        require(_feeRecipient != address(0), "Invalid fee recipient");
        
        platformFee = _platformFee;
        feeRecipient = _feeRecipient;
        _listingIdCounter = 1;
    }
    
    /**
     * @dev List an NFT for sale
     * @param nftContract Address of the NFT contract
     * @param tokenId ID of the token to list
     * @param price Sale price in wei
     * @return listingId The ID of the created listing
     */
    function listNFT(
        address nftContract,
        uint256 tokenId,
        uint256 price
    ) external nonReentrant returns (uint256) {
        require(price > 0, "Price must be greater than 0");
        
        IERC721 nft = IERC721(nftContract);
        require(nft.ownerOf(tokenId) == msg.sender, "Not the owner");
        require(
            nft.isApprovedForAll(msg.sender, address(this)) || 
            nft.getApproved(tokenId) == address(this),
            "Marketplace not approved"
        );
        
        uint256 listingId = _listingIdCounter++;
        
        listings[listingId] = Listing({
            seller: msg.sender,
            nftContract: nftContract,
            tokenId: tokenId,
            price: price,
            active: true
        });
        
        emit NFTListed(listingId, msg.sender, nftContract, tokenId, price);
        
        return listingId;
    }
    
    /**
     * @dev Buy a listed NFT
     * @param listingId ID of the listing to purchase
     */
    function buyNFT(uint256 listingId) external payable nonReentrant {
        Listing storage listing = listings[listingId];
        
        require(listing.active, "Listing not active");
        require(msg.value >= listing.price, "Insufficient payment");
        require(msg.sender != listing.seller, "Cannot buy your own NFT");
        
        IERC721 nft = IERC721(listing.nftContract);
        require(nft.ownerOf(listing.tokenId) == listing.seller, "Seller no longer owns NFT");
        
        // Mark as inactive
        listing.active = false;
        
        // Calculate fees
        uint256 platformFeeAmount = (listing.price * platformFee) / 10000;
        uint256 royaltyAmount = 0;
        address royaltyReceiver = address(0);
        
        // Check for ERC2981 royalty support
        if (nft.supportsInterface(type(ERC2981).interfaceId)) {
            (royaltyReceiver, royaltyAmount) = ERC2981(listing.nftContract).royaltyInfo(
                listing.tokenId,
                listing.price
            );
        }
        
        uint256 sellerProceeds = listing.price - platformFeeAmount - royaltyAmount;
        
        // Transfer NFT to buyer
        nft.safeTransferFrom(listing.seller, msg.sender, listing.tokenId);
        
        // Transfer payments
        payable(feeRecipient).transfer(platformFeeAmount);
        
        if (royaltyAmount > 0 && royaltyReceiver != address(0)) {
            payable(royaltyReceiver).transfer(royaltyAmount);
        }
        
        payable(listing.seller).transfer(sellerProceeds);
        
        // Refund excess payment
        if (msg.value > listing.price) {
            payable(msg.sender).transfer(msg.value - listing.price);
        }
        
        emit NFTSold(
            listingId,
            msg.sender,
            listing.seller,
            listing.nftContract,
            listing.tokenId,
            listing.price
        );
    }
    
    /**
     * @dev Cancel a listing
     * @param listingId ID of the listing to cancel
     */
    function cancelListing(uint256 listingId) external nonReentrant {
        Listing storage listing = listings[listingId];
        
        require(listing.active, "Listing not active");
        require(listing.seller == msg.sender, "Not the seller");
        
        listing.active = false;
        
        emit ListingCancelled(listingId);
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
     * @dev Get listing details
     * @param listingId ID of the listing
     * @return Listing details
     */
    function getListing(uint256 listingId) external view returns (Listing memory) {
        return listings[listingId];
    }
    
    /**
     * @dev Get current listing ID counter
     * @return Current counter value
     */
    function getCurrentListingId() external view returns (uint256) {
        return _listingIdCounter - 1;
    }
}
