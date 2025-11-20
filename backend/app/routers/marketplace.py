from fastapi import APIRouter, HTTPException
from typing import List
from ..schemas.marketplace import (
    ListNFTRequest,
    ListNFTResponse,
    BuyNFTRequest,
    BuyNFTResponse,
    ListingDetailsResponse,
    CancelListingRequest
)
from ..services.marketplace_service import marketplace_service

router = APIRouter(prefix="/marketplace", tags=["Marketplace"])


@router.post("/list", response_model=ListNFTResponse)
async def list_nft(request: ListNFTRequest):
    """
    List an NFT for sale on the marketplace
    
    - **nft_contract_address**: Address of the NFT contract
    - **token_id**: Token ID to list
    - **price_eth**: Sale price in ETH
    - **from_address**: Seller address (must be NFT owner)
    - **private_key**: Private key for signing
    
    Note: NFT must be approved for the marketplace contract before listing
    """
    try:
        result = marketplace_service.list_nft(
            nft_contract_address=request.nft_contract_address,
            token_id=request.token_id,
            price_eth=request.price_eth,
            from_address=request.from_address,
            private_key=request.private_key
        )
        return ListNFTResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/buy/{listing_id}", response_model=BuyNFTResponse)
async def buy_nft(listing_id: int, request: BuyNFTRequest):
    """
    Buy a listed NFT
    
    - **listing_id**: ID of the listing to purchase
    - **from_address**: Buyer address
    - **private_key**: Private key for signing
    
    The transaction will include the listing price plus gas fees
    """
    try:
        tx_hash = marketplace_service.buy_nft(
            listing_id=listing_id,
            from_address=request.from_address,
            private_key=request.private_key
        )
        return BuyNFTResponse(transaction_hash=tx_hash, listing_id=listing_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/listing/{listing_id}")
async def cancel_listing(listing_id: int, request: CancelListingRequest):
    """
    Cancel a listing
    
    Only the seller can cancel their own listing
    """
    try:
        tx_hash = marketplace_service.cancel_listing(
            listing_id=listing_id,
            from_address=request.from_address,
            private_key=request.private_key
        )
        return {"transaction_hash": tx_hash, "listing_id": listing_id, "status": "cancelled"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/listing/{listing_id}", response_model=ListingDetailsResponse)
async def get_listing(listing_id: int):
    """
    Get details of a specific listing
    
    Returns seller, NFT contract, token ID, price, and active status
    """
    try:
        listing = marketplace_service.get_listing(listing_id)
        return ListingDetailsResponse(**listing)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/listings", response_model=List[ListingDetailsResponse])
async def get_all_active_listings():
    """
    Get all active listings on the marketplace
    
    Returns a list of all currently active listings
    """
    try:
        listings = marketplace_service.get_all_active_listings()
        return [ListingDetailsResponse(**listing) for listing in listings]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/stats/platform-fee")
async def get_platform_fee():
    """Get current platform fee in basis points"""
    try:
        fee = marketplace_service.get_platform_fee()
        return {"platform_fee_bps": fee, "platform_fee_percent": fee / 100}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
