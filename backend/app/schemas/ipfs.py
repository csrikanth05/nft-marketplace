from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class ImageUploadResponse(BaseModel):
    """Response for image upload"""
    ipfs_hash: str
    ipfs_url: str
    ipfs_uri: str
    filename: str


class MetadataUploadRequest(BaseModel):
    """Request for uploading NFT metadata"""
    name: str
    description: str
    image_ipfs_hash: str
    attributes: Optional[List[Dict[str, Any]]] = None


class MetadataUploadResponse(BaseModel):
    """Response for metadata upload"""
    ipfs_hash: str
    ipfs_url: str
    ipfs_uri: str
    metadata: Dict[str, Any]


class NFTBundleRequest(BaseModel):
    """Request for uploading complete NFT (image + metadata)"""
    name: str
    description: str
    attributes: Optional[List[Dict[str, Any]]] = None


class NFTBundleResponse(BaseModel):
    """Response for complete NFT upload"""
    image_ipfs_hash: str
    image_ipfs_url: str
    metadata_ipfs_hash: str
    metadata_ipfs_url: str
    metadata_ipfs_uri: str
    token_uri: str  # This is what you pass to mintNFT


class IPFSUrlResponse(BaseModel):
    """Response for IPFS URL retrieval"""
    ipfs_hash: str
    ipfs_url: str
    ipfs_uri: str
