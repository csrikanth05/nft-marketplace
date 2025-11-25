from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from ..database import get_db
from ..models.models import User
from ..services.email_service import email_service
from sqlalchemy import func
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/email", tags=["Email Notifications"])


class NFTMintedNotification(BaseModel):
    user_address: str
    nft_name: str
    token_id: int
    contract_address: str
    tx_hash: str | None = None


@router.post("/nft-minted")
async def send_nft_minted_notification(
    notification: NFTMintedNotification,
    db: Session = Depends(get_db)
):
    """
    Send NFT minted notification email to user.
    
    - **user_address**: Wallet address of the user
    - **nft_name**: Name of the minted NFT
    - **token_id**: Token ID of the NFT
    - **contract_address**: NFT contract address
    - **tx_hash**: Transaction hash (optional)
    """
    # Get user profile
    user = db.query(User).filter(
        func.lower(User.address) == notification.user_address.lower()
    ).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not user.email:
        logger.warning(f"User {user.address} has no email configured")
        return {"success": False, "message": "User has no email configured"}
    
    # Send email
    success = email_service.send_nft_minted_email(
        to_email=user.email,
        username=user.username or "Collector",
        nft_name=notification.nft_name,
        token_id=notification.token_id,
        contract_address=notification.contract_address,
        tx_hash=notification.tx_hash
    )
    
    if success:
        return {"success": True, "message": f"Email sent to {user.email}"}
    else:
        return {"success": False, "message": "Failed to send email"}
