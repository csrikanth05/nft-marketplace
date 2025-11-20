from pydantic import BaseModel, Field
from typing import Optional


class CreateAuctionRequest(BaseModel):
    nft_contract_address: str = Field(..., description="NFT contract address")
    token_id: int = Field(..., description="Token ID to auction")
    start_time: int = Field(..., description="Auction start time (unix timestamp)")
    end_time: int = Field(..., description="Auction end time (unix timestamp)")
    reserve_price_eth: float = Field(..., gt=0, description="Reserve price in ETH")
    from_address: str = Field(..., description="Seller address")
    private_key: str = Field(..., description="Private key for signing")


class CreateAuctionResponse(BaseModel):
    transaction_hash: str
    auction_id: Optional[int]
    token_id: int
    reserve_price_eth: float


class PlaceBidRequest(BaseModel):
    auction_id: int = Field(..., description="Auction ID")
    bid_amount_eth: float = Field(..., gt=0, description="Bid amount in ETH")
    from_address: str = Field(..., description="Bidder address")
    private_key: str = Field(..., description="Private key for signing")


class PlaceBidResponse(BaseModel):
    transaction_hash: str
    auction_id: int
    bid_amount_eth: float


class AuctionDetailsResponse(BaseModel):
    auction_id: int
    seller: str
    nft_contract: str
    token_id: int
    start_time: int
    end_time: int
    reserve_price_wei: int
    reserve_price_eth: float
    highest_bidder: str
    highest_bid_wei: int
    highest_bid_eth: float
    active: bool
    ended: bool


class EndAuctionRequest(BaseModel):
    auction_id: int
    from_address: str
    private_key: str


class WithdrawBidRequest(BaseModel):
    auction_id: int
    from_address: str
    private_key: str
