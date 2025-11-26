from pydantic import BaseModel, Field
from typing import Optional


class ListNFTRequest(BaseModel):
    nft_contract_address: str = Field(..., description="NFT contract address")
    token_id: int = Field(..., description="Token ID to list")
    price_eth: float = Field(..., gt=0, description="Price in ETH")
    from_address: str = Field(..., description="Seller address")
    private_key: str = Field(..., description="Private key for signing")


class ListNFTResponse(BaseModel):
    transaction_hash: str
    listing_id: Optional[int]
    token_id: int
    price_eth: float


class BuyNFTRequest(BaseModel):
    listing_id: Optional[int] = Field(None, description="Listing ID to purchase (optional if passed in URL)")
    from_address: str = Field(..., description="Buyer address")
    private_key: str = Field(..., description="Private key for signing")


class BuyNFTResponse(BaseModel):
    transaction_hash: str
    listing_id: int


class ListingDetailsResponse(BaseModel):
    listing_id: int
    seller: str
    nft_contract: str
    token_id: int
    price_wei: int
    price_eth: float
    active: bool


class CancelListingRequest(BaseModel):
    listing_id: int
    from_address: str
    private_key: str
