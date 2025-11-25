from pydantic import BaseModel, Field
from typing import Optional


class MintNFTRequest(BaseModel):
    to_address: str = Field(..., description="Address to mint NFT to")
    token_uri: str = Field(..., description="Metadata URI (IPFS hash)")
    royalty_receiver: str = Field(..., description="Address to receive royalties")
    royalty_fee: int = Field(..., ge=0, le=10000, description="Royalty fee in basis points (0-10000)")
    from_address: str = Field(..., description="Sender address")
    private_key: str = Field(..., description="Private key for signing")


class MintNFTResponse(BaseModel):
    transaction_hash: str
    token_id: Optional[int]
    to_address: str
    token_uri: str


class NFTDetailsResponse(BaseModel):
    token_id: int
    owner: str
    creator: str
    token_uri: str
    royalty_receiver: str
    royalty_amount: float


class TransferNFTRequest(BaseModel):
    from_address: str
    to_address: str
    token_id: int
    private_key: str


class TransferNFTResponse(BaseModel):
    transaction_hash: str
    token_id: int
    from_address: str
    to_address: str


class ApproveNFTRequest(BaseModel):
    to_address: str = Field(..., description="Address to approve (e.g., marketplace)")
    token_id: int = Field(..., description="Token ID to approve")
    from_address: str = Field(..., description="NFT owner address")
    private_key: str = Field(..., description="Private key for signing")


class ApproveNFTResponse(BaseModel):
    transaction_hash: str
    token_id: int
    approved_address: str
