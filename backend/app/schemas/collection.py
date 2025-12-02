from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class CollectionCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    banner_image: Optional[str] = None


class CollectionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    banner_image: Optional[str] = None


class NFTInCollection(BaseModel):
    id: int
    token_id: int
    contract_address: str
    token_uri: str
    added_at: datetime

    class Config:
        from_attributes = True


class CollectionResponse(BaseModel):
    id: int
    owner_address: str
    name: str
    description: Optional[str]
    category: Optional[str]
    banner_image: Optional[str]
    nft_count: int
    created_at: datetime
    updated_at: datetime
    nfts: Optional[List[NFTInCollection]] = []

    class Config:
        from_attributes = True


class CollectionSummary(BaseModel):
    id: int
    owner_address: str
    name: str
    description: Optional[str]
    category: Optional[str]
    banner_image: Optional[str]
    nft_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class AddNFTToCollection(BaseModel):
    nft_id: int


class RemoveNFTFromCollection(BaseModel):
    nft_id: int
