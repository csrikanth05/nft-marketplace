from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import time
from ..schemas.marketplace import (
    ListNFTRequest,
    ListNFTResponse,
    BuyNFTRequest,
    BuyNFTResponse,
    ListingDetailsResponse,
    CancelListingRequest
)
from ..services.marketplace_service import marketplace_service
from ..services.email_service import email_service
from ..database import get_db
from ..models.models import User, Transaction, NFT, Listing

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
async def buy_nft(
    listing_id: int, 
    request: BuyNFTRequest,
    db: Session = Depends(get_db)
):
    """
    Buy a listed NFT
    
    - **listing_id**: ID of the listing to purchase
    - **from_address**: Buyer address
    - **private_key**: Private key for signing
    
    The transaction will include the listing price plus gas fees
    """
    try:
        result = marketplace_service.buy_nft(
            listing_id=listing_id,
            from_address=request.from_address,
            private_key=request.private_key
        )
        
        # Record transaction in database
        try:
            new_transaction = Transaction(
                transaction_hash=result["transaction_hash"],
                nft_id=listing_id, # Note: listing_id is passed, but we need nft_id. 
                           # Wait, listing_id is the ID of the listing.
                           # The Transaction model has nft_id.
                           # result has token_id and nft_contract.
                           # We need to find the NFT record in DB to get its ID.
            )
            # Actually, let's look at the Transaction model.
            # nft_id = Column(Integer, ForeignKey("nfts.id"))
            # We need the internal DB ID of the NFT.
            
            # Fetch the listing to get the NFT ID
            # We can use the listing_id (which is the on-chain ID) to find the Listing record in DB?
            # Or we can find the NFT by contract and token_id.
            
            nft = db.query(NFT).filter(
                NFT.contract_address == result["nft_contract"],
                NFT.token_id == result["token_id"]
            ).first()
            
            if nft:
                new_transaction = Transaction(
                    transaction_hash=result["transaction_hash"],
                    nft_id=nft.id,
                    buyer_address=request.from_address,
                    seller_address=result["seller_address"],
                    price_eth=result["price_eth"],
                    gas_fee_eth=result["gas_fee_eth"],
                    timestamp=int(time.time()),
                    transaction_type='buy'
                )
                db.add(new_transaction)
                
                # Update NFT owner and clear listing
                nft.owner_address = request.from_address
                nft.is_listed = False
                
                # Also update the Listing record if it exists
                db_listing = db.query(Listing).filter(Listing.listing_id == listing_id).first()
                if db_listing:
                    db_listing.active = False
                    db_listing.sold = True
                
                db.commit()
            else:
                print(f"NFT not found in DB for transaction recording: {result['nft_contract']} #{result['token_id']}")

        except Exception as e:
            print(f"Failed to record transaction: {e}")
            db.rollback()

        # Send email notifications
        try:
            # Fetch buyer and seller details
            buyer = db.query(User).filter(User.address == request.from_address).first()
            seller = db.query(User).filter(User.address == result["seller_address"]).first()
            
            nft_name = f"NFT #{result['token_id']}"
            price_eth = result["price_eth"]
            tx_hash = result["transaction_hash"]
            
            # Send email to buyer
            if buyer and buyer.email:
                email_service.send_nft_bought_email(
                    to_email=buyer.email,
                    username=buyer.username or "User",
                    nft_name=nft_name,
                    price_eth=price_eth,
                    tx_hash=tx_hash
                )
                
            # Send email to seller
            if seller and seller.email:
                email_service.send_nft_sold_email(
                    to_email=seller.email,
                    username=seller.username or "User",
                    nft_name=nft_name,
                    price_eth=price_eth,
                    tx_hash=tx_hash
                )
        except Exception as e:
            # Don't fail the request if email sending fails
            print(f"Failed to send email notifications: {e}")
            
        return BuyNFTResponse(
            transaction_hash=result["transaction_hash"], 
            listing_id=listing_id
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/estimate-gas/buy/{listing_id}")
async def estimate_buy_gas(listing_id: int, from_address: str):
    """
    Estimate gas fee for buying an NFT
    
    Returns estimated gas fee in ETH
    """
    try:
        gas_fee = marketplace_service.estimate_buy_gas(listing_id, from_address)
        return {"gas_fee_eth": gas_fee}
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
