// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "@openzeppelin/contracts/token/common/ERC2981.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title NFTContract
 * @dev ERC721 NFT contract with minting, royalties, and metadata support
 */
contract NFTContract is ERC721, ERC721URIStorage, ERC721Enumerable, ERC2981, Ownable {
    
    uint256 private _tokenIdCounter;
    
    // Mapping from token ID to creator address
    mapping(uint256 => address) private _creators;
    
    // Events
    event NFTMinted(uint256 indexed tokenId, address indexed creator, string tokenURI);
    event NFTBurned(uint256 indexed tokenId, address indexed owner);
    event RoyaltySet(uint256 indexed tokenId, address indexed receiver, uint96 feeNumerator);
    
    constructor() ERC721("NFT Marketplace Token", "NFTM") Ownable() {
        // Start token IDs at 1
        _tokenIdCounter = 1;
    }
    
    /**
     * @dev Mint a new NFT
     * @param to Address to mint the NFT to
     * @param uri Metadata URI for the NFT
     * @param royaltyReceiver Address to receive royalties
     * @param royaltyFeeNumerator Royalty fee in basis points (e.g., 250 = 2.5%)
     * @return tokenId The ID of the newly minted token
     */
    function mintNFT(
        address to,
        string memory uri,
        address royaltyReceiver,
        uint96 royaltyFeeNumerator
    ) public returns (uint256) {
        require(to != address(0), "Cannot mint to zero address");
        require(bytes(uri).length > 0, "URI cannot be empty");
        require(royaltyFeeNumerator <= 10000, "Royalty fee too high"); // Max 100%
        
        uint256 tokenId = _tokenIdCounter;
        _tokenIdCounter++;
        
        _safeMint(to, tokenId);
        _setTokenURI(tokenId, uri);
        _creators[tokenId] = msg.sender;
        
        // Set royalty info (ERC2981)
        if (royaltyReceiver != address(0) && royaltyFeeNumerator > 0) {
            _setTokenRoyalty(tokenId, royaltyReceiver, royaltyFeeNumerator);
            emit RoyaltySet(tokenId, royaltyReceiver, royaltyFeeNumerator);
        }
        
        emit NFTMinted(tokenId, msg.sender, uri);
        
        return tokenId;
    }
    
    /**
     * @dev Burn an NFT (only owner can burn)
     * @param tokenId The ID of the token to burn
     */
    function burn(uint256 tokenId) public {
        require(ownerOf(tokenId) == msg.sender, "Only owner can burn");
        delete _creators[tokenId];
        _burn(tokenId);
        emit NFTBurned(tokenId, msg.sender);
    }
    
    /**
     * @dev Get the creator of a token
     * @param tokenId The ID of the token
     * @return The address of the creator
     */
    function creatorOf(uint256 tokenId) public view returns (address) {
        require(_ownerOf(tokenId) != address(0), "Token does not exist");
        return _creators[tokenId];
    }
    
    /**
     * @dev Get all tokens owned by an address
     * @param owner The address to query
     * @return An array of token IDs
     */
    function tokensOfOwner(address owner) public view returns (uint256[] memory) {
        uint256 tokenCount = balanceOf(owner);
        uint256[] memory tokenIds = new uint256[](tokenCount);
        
        for (uint256 i = 0; i < tokenCount; i++) {
            tokenIds[i] = tokenOfOwnerByIndex(owner, i);
        }
        
        return tokenIds;
    }
    
    /**
     * @dev Get the total number of minted tokens
     * @return The total supply
     */
    function getCurrentTokenId() public view returns (uint256) {
        return _tokenIdCounter - 1;
    }
    
    // Required overrides for multiple inheritance
    
    function _beforeTokenTransfer(
        address from,
        address to,
        uint256 tokenId,
        uint256 batchSize
    ) internal override(ERC721, ERC721Enumerable) {
        super._beforeTokenTransfer(from, to, tokenId, batchSize);
    }
    
    function _burn(uint256 tokenId)
        internal
        override(ERC721, ERC721URIStorage)
    {
        super._burn(tokenId);
    }
    
    function tokenURI(uint256 tokenId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (string memory)
    {
        return super.tokenURI(tokenId);
    }
    
    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721, ERC721Enumerable, ERC721URIStorage, ERC2981)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}
