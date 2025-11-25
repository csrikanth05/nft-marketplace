from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..database import get_db
from ..models.models import User
from sqlalchemy import func

router = APIRouter(prefix="/users", tags=["User Profiles"])


class ProfileUpdateRequest(BaseModel):
    username: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "CryptoCollector"
            }
        }


class ProfileResponse(BaseModel):
    address: str
    username: str | None = None
    
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
    """
    # Check if user exists (case-insensitive)
    user = db.query(User).filter(func.lower(User.address) == address.lower()).first()
    
    if user:
        # Update existing user
        user.username = request.username
    else:
        # Create new user
        user = User(
            address=address.lower(),
            username=request.username
        )
        db.add(user)
    
    db.commit()
    db.refresh(user)
    
    return ProfileResponse(
        address=user.address,
        username=user.username
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
        return ProfileResponse(address=address.lower(), username=None)
    
    return ProfileResponse(
        address=user.address,
        username=user.username
    )
