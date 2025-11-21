from pydantic import BaseModel
from typing import Optional, List


class NFTResponse(BaseModel):
    """Response model for NFT details"""
    id: int
    token_id: int
    contract_address: str
    owner_address: str
    creator_address: str
    token_uri: str
    is_listed: bool

    class Config:
        from_attributes = True


class ListingResponse(BaseModel):
    """Response model for marketplace listing"""
    id: int
    listing_id: int
    seller_address: str
    price_wei: str
    price_eth: float
    active: bool
    sold: bool
    cancelled: bool
    nft: Optional[NFTResponse] = None

    class Config:
        from_attributes = True


class BidResponse(BaseModel):
    """Response model for auction bid"""
    id: int
    bidder_address: str
    amount_wei: str
    amount_eth: float
    timestamp: int

    class Config:
        from_attributes = True


class AuctionResponse(BaseModel):
    """Response model for auction"""
    id: int
    auction_id: int
    seller_address: str
    start_time: int
    end_time: int
    reserve_price_wei: str
    reserve_price_eth: float
    highest_bid_wei: str
    highest_bid_eth: float
    highest_bidder_address: Optional[str] = None
    active: bool
    ended: bool
    cancelled: bool
    nft: Optional[NFTResponse] = None
    bids: List[BidResponse] = []

    class Config:
        from_attributes = True


class UserStatsResponse(BaseModel):
    """Response model for user statistics"""
    address: str
    nfts_owned: int
    active_listings: int
    active_auctions: int
    total_bids: int


class UserProfileResponse(BaseModel):
    """Response model for user profile"""
    address: str
    username: Optional[str] = None
    stats: UserStatsResponse
    nfts: List[NFTResponse] = []

    class Config:
        from_attributes = True
