from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models.models import User, NFT, Listing, Auction, Bid
from ..schemas.database import (
    NFTResponse,
    ListingResponse,
    AuctionResponse,
    BidResponse,
    UserProfileResponse,
    UserStatsResponse
)

router = APIRouter(prefix="/db", tags=["Database Queries"])


# ==================== NFT Endpoints ====================

@router.get("/nfts", response_model=List[NFTResponse])
async def get_all_nfts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get all NFTs with pagination.
    
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100, max: 1000)
    """
    nfts = db.query(NFT).offset(skip).limit(limit).all()
    return nfts


@router.get("/nfts/{token_id}", response_model=NFTResponse)
async def get_nft_by_token_id(
    token_id: int,
    db: Session = Depends(get_db)
):
    """
    Get NFT details by token ID.
    
    - **token_id**: The token ID to query
    """
    nft = db.query(NFT).filter(NFT.token_id == token_id).first()
    if not nft:
        raise HTTPException(status_code=404, detail=f"NFT with token_id {token_id} not found")
    return nft


@router.get("/users/{address}/nfts", response_model=List[NFTResponse])
async def get_nfts_by_owner(
    address: str,
    db: Session = Depends(get_db)
):
    """
    Get all NFTs owned by a specific address.
    
    - **address**: Wallet address of the owner
    """
    nfts = db.query(NFT).filter(NFT.owner_address == address).all()
    return nfts


# ==================== Marketplace Endpoints ====================

@router.get("/listings", response_model=List[ListingResponse])
async def get_all_listings(
    active_only: bool = Query(True),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get all marketplace listings.
    
    - **active_only**: Filter for active listings only (default: True)
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100, max: 1000)
    """
    query = db.query(Listing)
    if active_only:
        query = query.filter(Listing.active == True)
    listings = query.offset(skip).limit(limit).all()
    return listings


@router.get("/listings/{listing_id}", response_model=ListingResponse)
async def get_listing_by_id(
    listing_id: int,
    db: Session = Depends(get_db)
):
    """
    Get listing details by listing ID.
    
    - **listing_id**: The listing ID to query
    """
    listing = db.query(Listing).filter(Listing.listing_id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail=f"Listing {listing_id} not found")
    return listing


@router.get("/users/{address}/listings", response_model=List[ListingResponse])
async def get_listings_by_seller(
    address: str,
    active_only: bool = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get all listings created by a specific seller.
    
    - **address**: Wallet address of the seller
    - **active_only**: Filter for active listings only (default: False)
    """
    query = db.query(Listing).filter(Listing.seller_address == address)
    if active_only:
        query = query.filter(Listing.active == True)
    listings = query.all()
    return listings


# ==================== Auction Endpoints ====================

@router.get("/auctions", response_model=List[AuctionResponse])
async def get_all_auctions(
    active_only: bool = Query(True),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get all auctions.
    
    - **active_only**: Filter for active auctions only (default: True)
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100, max: 1000)
    """
    query = db.query(Auction)
    if active_only:
        query = query.filter(Auction.active == True)
    auctions = query.offset(skip).limit(limit).all()
    return auctions


@router.get("/auctions/{auction_id}", response_model=AuctionResponse)
async def get_auction_by_id(
    auction_id: int,
    db: Session = Depends(get_db)
):
    """
    Get auction details by auction ID, including bid history.
    
    - **auction_id**: The auction ID to query
    """
    auction = db.query(Auction).filter(Auction.auction_id == auction_id).first()
    if not auction:
        raise HTTPException(status_code=404, detail=f"Auction {auction_id} not found")
    return auction


@router.get("/users/{address}/auctions", response_model=List[AuctionResponse])
async def get_auctions_by_seller(
    address: str,
    active_only: bool = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get all auctions created by a specific seller.
    
    - **address**: Wallet address of the seller
    - **active_only**: Filter for active auctions only (default: False)
    """
    query = db.query(Auction).filter(Auction.seller_address == address)
    if active_only:
        query = query.filter(Auction.active == True)
    auctions = query.all()
    return auctions


@router.get("/users/{address}/bids", response_model=List[BidResponse])
async def get_bids_by_user(
    address: str,
    db: Session = Depends(get_db)
):
    """
    Get all bids placed by a specific user.
    
    - **address**: Wallet address of the bidder
    """
    bids = db.query(Bid).filter(Bid.bidder_address == address).all()
    return bids


# ==================== User Endpoints ====================

@router.get("/users/{address}", response_model=UserProfileResponse)
async def get_user_profile(
    address: str,
    include_nfts: bool = Query(True),
    db: Session = Depends(get_db)
):
    """
    Get user profile with statistics and optionally their NFTs.
    
    - **address**: Wallet address of the user
    - **include_nfts**: Include user's NFTs in response (default: True)
    """
    user = db.query(User).filter(User.address == address).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User {address} not found")
    
    # Calculate stats
    nfts_owned = db.query(NFT).filter(NFT.owner_address == address).count()
    active_listings = db.query(Listing).filter(
        Listing.seller_address == address,
        Listing.active == True
    ).count()
    active_auctions = db.query(Auction).filter(
        Auction.seller_address == address,
        Auction.active == True
    ).count()
    total_bids = db.query(Bid).filter(Bid.bidder_address == address).count()
    
    stats = UserStatsResponse(
        address=address,
        nfts_owned=nfts_owned,
        active_listings=active_listings,
        active_auctions=active_auctions,
        total_bids=total_bids
    )
    
    nfts = []
    if include_nfts:
        nfts = db.query(NFT).filter(NFT.owner_address == address).all()
    
    return UserProfileResponse(
        address=user.address,
        username=user.username,
        stats=stats,
        nfts=nfts
    )


@router.get("/users", response_model=List[UserProfileResponse])
async def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get all users with their statistics.
    
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100, max: 1000)
    """
    users = db.query(User).offset(skip).limit(limit).all()
    
    result = []
    for user in users:
        nfts_owned = db.query(NFT).filter(NFT.owner_address == user.address).count()
        active_listings = db.query(Listing).filter(
            Listing.seller_address == user.address,
            Listing.active == True
        ).count()
        active_auctions = db.query(Auction).filter(
            Auction.seller_address == user.address,
            Auction.active == True
        ).count()
        total_bids = db.query(Bid).filter(Bid.bidder_address == user.address).count()
        
        stats = UserStatsResponse(
            address=user.address,
            nfts_owned=nfts_owned,
            active_listings=active_listings,
            active_auctions=active_auctions,
            total_bids=total_bids
        )
        
        result.append(UserProfileResponse(
            address=user.address,
            username=user.username,
            stats=stats,
            nfts=[]
        ))
    
    return result
