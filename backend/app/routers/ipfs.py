from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import Optional
from ..services.ipfs_service import ipfs_service
from ..schemas.ipfs import (
    ImageUploadResponse,
    MetadataUploadRequest,
    MetadataUploadResponse,
    NFTBundleRequest,
    NFTBundleResponse,
    IPFSUrlResponse
)

router = APIRouter(prefix="/ipfs", tags=["IPFS Storage"])


@router.post("/upload-image", response_model=ImageUploadResponse)
async def upload_image(file: UploadFile = File(...)):
    """
    Upload an image file to IPFS via Pinata.
    
    - **file**: Image file (JPEG, PNG, GIF, etc.)
    
    Returns IPFS hash and gateway URL for the uploaded image.
    """
    try:
        # Read file content
        content = await file.read()
        
        # Upload to IPFS
        result = ipfs_service.upload_file(content, file.filename)
        
        return ImageUploadResponse(
            ipfs_hash=result['ipfs_hash'],
            ipfs_url=result['ipfs_url'],
            ipfs_uri=result['ipfs_uri'],
            filename=file.filename
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")


@router.post("/upload-metadata", response_model=MetadataUploadResponse)
async def upload_metadata(request: MetadataUploadRequest):
    """
    Upload NFT metadata JSON to IPFS.
    
    - **name**: NFT name
    - **description**: NFT description
    - **image_ipfs_hash**: IPFS hash of the NFT image
    - **attributes**: Optional list of trait attributes
    
    Returns IPFS hash and URL for the metadata JSON.
    """
    try:
        result = ipfs_service.upload_nft_metadata(
            name=request.name,
            description=request.description,
            image_ipfs_hash=request.image_ipfs_hash,
            attributes=request.attributes
        )
        
        metadata = {
            "name": request.name,
            "description": request.description,
            "image": f"ipfs://{request.image_ipfs_hash}"
        }
        if request.attributes:
            metadata["attributes"] = request.attributes
        
        return MetadataUploadResponse(
            ipfs_hash=result['ipfs_hash'],
            ipfs_url=result['ipfs_url'],
            ipfs_uri=result['ipfs_uri'],
            metadata=metadata
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload metadata: {str(e)}")


@router.post("/upload-nft", response_model=NFTBundleResponse)
async def upload_nft_bundle(
    file: UploadFile = File(...),
    name: str = None,
    description: str = None
):
    """
    Upload a complete NFT: image + metadata in one request.
    
    - **file**: Image file
    - **name**: NFT name (form field)
    - **description**: NFT description (form field)
    
    Returns both image and metadata IPFS hashes. Use `token_uri` for minting.
    """
    try:
        if not name or not description:
            raise HTTPException(status_code=400, detail="Name and description are required")
        
        # Upload image
        image_content = await file.read()
        image_result = ipfs_service.upload_file(image_content, file.filename)
        
        # Upload metadata
        metadata_result = ipfs_service.upload_nft_metadata(
            name=name,
            description=description,
            image_ipfs_hash=image_result['ipfs_hash']
        )
        
        return NFTBundleResponse(
            image_ipfs_hash=image_result['ipfs_hash'],
            image_ipfs_url=image_result['ipfs_url'],
            metadata_ipfs_hash=metadata_result['ipfs_hash'],
            metadata_ipfs_url=metadata_result['ipfs_url'],
            metadata_ipfs_uri=metadata_result['ipfs_uri'],
            token_uri=metadata_result['ipfs_uri']  # Use this for mintNFT
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload NFT bundle: {str(e)}")


@router.get("/{ipfs_hash}", response_model=IPFSUrlResponse)
async def get_ipfs_url(ipfs_hash: str):
    """
    Get gateway URL for an IPFS hash.
    
    - **ipfs_hash**: IPFS hash (e.g., QmXxx...)
    
    Returns the full gateway URL to access the content.
    """
    return IPFSUrlResponse(
        ipfs_hash=ipfs_hash,
        ipfs_url=ipfs_service.get_ipfs_url(ipfs_hash),
        ipfs_uri=ipfs_service.get_ipfs_uri(ipfs_hash)
    )
