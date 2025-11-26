from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..database import get_db
from ..models.models import User
from sqlalchemy import func

router = APIRouter(prefix="/users", tags=["User Profiles"])


class ProfileUpdateRequest(BaseModel):
    username: str
    avatar: str | None = None
    email: str | None = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "CryptoCollector",
                "avatar": "😀",
                "email": "user@example.com"
            }
        }


class ProfileResponse(BaseModel):
    address: str
    username: str | None = None
    avatar: str | None = None
    email: str | None = None
    
    class Config:
        from_attributes = True


@router.post("/profile", response_model=ProfileResponse)
async def create_or_update_profile(
    address: str,
    request: ProfileUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    Create or update user profile.
    
    - **address**: Wallet address
    - **username**: Display name for the user
    - **avatar**: Avatar emoji identifier
    - **email**: User email address
    """
    # Check if user exists (case-insensitive)
    user = db.query(User).filter(func.lower(User.address) == address.lower()).first()
    
    if user:
        # Update existing user
        user.username = request.username
        if request.avatar is not None:
            user.avatar = request.avatar
        if request.email is not None:
            user.email = request.email
    else:
        # Create new user
        user = User(
            address=address.lower(),
            username=request.username,
            avatar=request.avatar,
            email=request.email
        )
        db.add(user)
    
    db.commit()
    db.refresh(user)
    
    return ProfileResponse(
        address=user.address,
        username=user.username,
        avatar=user.avatar,
        email=user.email
    )


@router.get("/{address}/profile", response_model=ProfileResponse)
async def get_user_profile(
    address: str,
    db: Session = Depends(get_db)
):
    """
    Get user profile by wallet address.
    
    - **address**: Wallet address
    """
    user = db.query(User).filter(func.lower(User.address) == address.lower()).first()
    
    if not user:
        # Return address without username if user doesn't exist
        return ProfileResponse(address=address.lower(), username=None, avatar=None, email=None)
    
    return ProfileResponse(
        address=user.address,
        username=user.username,
        avatar=user.avatar,
        email=user.email
    )


class TransactionResponse(BaseModel):
    id: int
    transaction_hash: str
    nft_id: int
    nft_name: str | None = None
    nft_image: str | None = None
    buyer_address: str | None
    seller_address: str | None
    price_eth: float
    gas_fee_eth: float | None
    timestamp: int
    transaction_type: str
    
    class Config:
        from_attributes = True


@router.get("/{address}/transactions", response_model=list[TransactionResponse])
async def get_user_transactions(
    address: str,
    db: Session = Depends(get_db)
):
    """
    Get all transactions for a specific user (buy, sell, mint)
    """
    from ..models.models import Transaction, NFT
    from sqlalchemy import or_

    transactions = db.query(Transaction).join(NFT).filter(
        or_(
            func.lower(Transaction.buyer_address) == address.lower(),
            func.lower(Transaction.seller_address) == address.lower()
        )
    ).order_by(Transaction.timestamp.desc()).all()
    
    result = []
    for tx in transactions:
        # Get NFT details
        nft = db.query(NFT).filter(NFT.id == tx.nft_id).first()
        
        # Determine NFT name/image (this would ideally come from metadata, but we'll use placeholders or what we have)
        # In a real app, we'd fetch metadata from token_uri
        
        result.append(TransactionResponse(
            id=tx.id,
            transaction_hash=tx.transaction_hash,
            nft_id=tx.nft_id,
            nft_name=f"NFT #{nft.token_id}" if nft else "Unknown NFT",
            nft_image=None, # We'd need to fetch this from metadata
            buyer_address=tx.buyer_address,
            seller_address=tx.seller_address,
            price_eth=tx.price_eth,
            gas_fee_eth=tx.gas_fee_eth,
            timestamp=tx.timestamp,
            transaction_type=tx.transaction_type
        ))
        
    return result
