from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from ..schemas.collection import (
    CollectionCreate,
    CollectionUpdate,
    CollectionResponse,
    CollectionSummary,
    AddNFTToCollection,
    NFTInCollection
)
from ..database import get_db
from ..models.models import Collection, CollectionNFT, NFT, User

router = APIRouter(prefix="/collection", tags=["Collection"])


@router.post("/create", response_model=CollectionResponse)
async def create_collection(request: CollectionCreate, owner_address: str, db: Session = Depends(get_db)):
    """
    Create a new NFT collection
    
    - **name**: Collection name (required)
    - **description**: Collection description
    - **category**: Collection category
    - **banner_image**: URL or path to banner image
    - **owner_address**: Address of the collection owner
    """
    try:
        # Ensure user exists
        user = db.query(User).filter(User.address == owner_address).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Create collection
        new_collection = Collection(
            owner_address=owner_address,
            name=request.name,
            description=request.description,
            category=request.category,
            banner_image=request.banner_image
        )
        
        db.add(new_collection)
        db.commit()
        db.refresh(new_collection)
        
        return CollectionResponse(
            id=new_collection.id,
            owner_address=new_collection.owner_address,
            name=new_collection.name,
            description=new_collection.description,
            category=new_collection.category,
            banner_image=new_collection.banner_image,
            nft_count=0,
            created_at=new_collection.created_at,
            updated_at=new_collection.updated_at,
            nfts=[]
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{collection_id}", response_model=CollectionResponse)
async def get_collection(collection_id: int, db: Session = Depends(get_db)):
    """Get collection details including all NFTs in the collection"""
    collection = db.query(Collection).filter(Collection.id == collection_id).first()
    
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    # Get NFTs in collection
    collection_nfts = db.query(CollectionNFT).filter(
        CollectionNFT.collection_id == collection_id
    ).all()
    
    nfts = []
    for cn in collection_nfts:
        nft = db.query(NFT).filter(NFT.id == cn.nft_id).first()
        if nft:
            nfts.append(NFTInCollection(
                id=nft.id,
                token_id=nft.token_id,
                contract_address=nft.contract_address,
                token_uri=nft.token_uri,
                added_at=cn.added_at
            ))
    
    return CollectionResponse(
        id=collection.id,
        owner_address=collection.owner_address,
        name=collection.name,
        description=collection.description,
        category=collection.category,
        banner_image=collection.banner_image,
        nft_count=len(nfts),
        created_at=collection.created_at,
        updated_at=collection.updated_at,
        nfts=nfts
    )


@router.get("/user/{address}", response_model=List[CollectionSummary])
async def get_user_collections(address: str, db: Session = Depends(get_db)):
    """Get all collections owned by a user"""
    collections = db.query(Collection).filter(Collection.owner_address == address).all()
    
    result = []
    for collection in collections:
        nft_count = db.query(CollectionNFT).filter(
            CollectionNFT.collection_id == collection.id
        ).count()
        
        result.append(CollectionSummary(
            id=collection.id,
            owner_address=collection.owner_address,
            name=collection.name,
            description=collection.description,
            category=collection.category,
            banner_image=collection.banner_image,
            nft_count=nft_count,
            created_at=collection.created_at
        ))
    
    return result


@router.put("/{collection_id}", response_model=CollectionResponse)
async def update_collection(
    collection_id: int,
    request: CollectionUpdate,
    owner_address: str,
    db: Session = Depends(get_db)
):
    """Update collection metadata"""
    collection = db.query(Collection).filter(Collection.id == collection_id).first()
    
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    # Verify ownership
    if collection.owner_address != owner_address:
        raise HTTPException(status_code=403, detail="Not authorized to update this collection")
    
    # Update fields
    if request.name is not None:
        collection.name = request.name
    if request.description is not None:
        collection.description = request.description
    if request.category is not None:
        collection.category = request.category
    if request.banner_image is not None:
        collection.banner_image = request.banner_image
    
    collection.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(collection)
    
    # Get NFT count
    nft_count = db.query(CollectionNFT).filter(
        CollectionNFT.collection_id == collection_id
    ).count()
    
    return CollectionResponse(
        id=collection.id,
        owner_address=collection.owner_address,
        name=collection.name,
        description=collection.description,
        category=collection.category,
        banner_image=collection.banner_image,
        nft_count=nft_count,
        created_at=collection.created_at,
        updated_at=collection.updated_at,
        nfts=[]
    )


@router.delete("/{collection_id}")
async def delete_collection(collection_id: int, owner_address: str, db: Session = Depends(get_db)):
    """Delete a collection"""
    collection = db.query(Collection).filter(Collection.id == collection_id).first()
    
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    # Verify ownership
    if collection.owner_address != owner_address:
        raise HTTPException(status_code=403, detail="Not authorized to delete this collection")
    
    db.delete(collection)
    db.commit()
    
    return {"message": "Collection deleted successfully", "collection_id": collection_id}


@router.post("/{collection_id}/add-nft")
async def add_nft_to_collection(
    collection_id: int,
    request: AddNFTToCollection,
    owner_address: str,
    db: Session = Depends(get_db)
):
    """Add an NFT to a collection"""
    # Verify collection exists and user owns it
    collection = db.query(Collection).filter(Collection.id == collection_id).first()
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    if collection.owner_address != owner_address:
        raise HTTPException(status_code=403, detail="Not authorized to modify this collection")
    
    # Verify NFT exists and user owns it
    nft = db.query(NFT).filter(NFT.id == request.nft_id).first()
    if not nft:
        raise HTTPException(status_code=404, detail="NFT not found")
    
    if nft.owner_address != owner_address:
        raise HTTPException(status_code=403, detail="You don't own this NFT")
    
    # Check if NFT is already in collection
    existing = db.query(CollectionNFT).filter(
        CollectionNFT.collection_id == collection_id,
        CollectionNFT.nft_id == request.nft_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="NFT already in collection")
    
    # Add NFT to collection
    collection_nft = CollectionNFT(
        collection_id=collection_id,
        nft_id=request.nft_id
    )
    
    db.add(collection_nft)
    collection.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "NFT added to collection", "collection_id": collection_id, "nft_id": request.nft_id}


@router.delete("/{collection_id}/remove-nft/{nft_id}")
async def remove_nft_from_collection(
    collection_id: int,
    nft_id: int,
    owner_address: str,
    db: Session = Depends(get_db)
):
    """Remove an NFT from a collection"""
    # Verify collection exists and user owns it
    collection = db.query(Collection).filter(Collection.id == collection_id).first()
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    if collection.owner_address != owner_address:
        raise HTTPException(status_code=403, detail="Not authorized to modify this collection")
    
    # Find and remove the collection-NFT relationship
    collection_nft = db.query(CollectionNFT).filter(
        CollectionNFT.collection_id == collection_id,
        CollectionNFT.nft_id == nft_id
    ).first()
    
    if not collection_nft:
        raise HTTPException(status_code=404, detail="NFT not in this collection")
    
    db.delete(collection_nft)
    collection.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "NFT removed from collection", "collection_id": collection_id, "nft_id": nft_id}
