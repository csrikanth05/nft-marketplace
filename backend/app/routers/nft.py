from fastapi import APIRouter, HTTPException
from typing import List
from ..schemas.nft import (
    MintNFTRequest,
    MintNFTResponse,
    NFTDetailsResponse,
    TransferNFTRequest,
    TransferNFTResponse,
    ApproveNFTRequest,
    ApproveNFTResponse
)
from ..services.nft_service import nft_service

router = APIRouter(prefix="/nfts", tags=["NFT"])


@router.post("/mint", response_model=MintNFTResponse)
async def mint_nft(request: MintNFTRequest):
    """
    Mint a new NFT
    
    - **to_address**: Address to mint the NFT to
    - **token_uri**: Metadata URI (IPFS hash)
    - **royalty_receiver**: Address to receive royalties
    - **royalty_fee**: Royalty fee in basis points (0-10000, e.g., 500 = 5%)
    - **from_address**: Sender address (must own the private key)
    - **private_key**: Private key for signing the transaction
    """
    try:
        result = nft_service.mint_nft(
            to_address=request.to_address,
            token_uri=request.token_uri,
            royalty_receiver=request.royalty_receiver,
            royalty_fee=request.royalty_fee,
            from_address=request.from_address,
            private_key=request.private_key
        )
        return MintNFTResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{token_id}", response_model=NFTDetailsResponse)
async def get_nft_details(token_id: int):
    """
    Get NFT details by token ID
    
    Returns owner, creator, metadata URI, and royalty information
    """
    try:
        details = nft_service.get_nft_details(token_id)
        return NFTDetailsResponse(**details)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/owner/{address}", response_model=List[int])
async def get_tokens_by_owner(address: str):
    """
    Get all token IDs owned by an address
    
    Returns a list of token IDs
    """
    try:
        tokens = nft_service.get_tokens_by_owner(address)
        return tokens
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/transfer", response_model=TransferNFTResponse)
async def transfer_nft(request: TransferNFTRequest):
    """
    Transfer an NFT to another address
    
    - **from_address**: Current owner address
    - **to_address**: Recipient address
    - **token_id**: Token ID to transfer
    - **private_key**: Private key of the current owner
    """
    try:
        tx_hash = nft_service.transfer_nft(
            from_address=request.from_address,
            to_address=request.to_address,
            token_id=request.token_id,
            private_key=request.private_key
        )
        return TransferNFTResponse(
            transaction_hash=tx_hash,
            token_id=request.token_id,
            from_address=request.from_address,
            to_address=request.to_address
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/approve", response_model=ApproveNFTResponse)
async def approve_nft(request: ApproveNFTRequest):
    """
    Approve an address to transfer an NFT
    
    - **to_address**: Address to approve (e.g., marketplace contract)
    - **token_id**: Token ID to approve
    - **from_address**: NFT owner address
    - **private_key**: Private key of the owner
    """
    try:
        tx_hash = nft_service.approve_nft(
            to_address=request.to_address,
            token_id=request.token_id,
            from_address=request.from_address,
            private_key=request.private_key
        )
        return ApproveNFTResponse(
            transaction_hash=tx_hash,
            token_id=request.token_id,
            approved_address=request.to_address
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{token_id}")
async def burn_nft(token_id: int, from_address: str, private_key: str):
    """
    Burn an NFT (permanently destroy it)
    
    Only the owner can burn their NFT
    """
    try:
        tx_hash = nft_service.burn_nft(
            token_id=token_id,
            from_address=from_address,
            private_key=private_key
        )
        return {"transaction_hash": tx_hash, "token_id": token_id, "status": "burned"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/stats/total-supply")
async def get_total_supply():
    """Get total number of minted NFTs"""
    try:
        total = nft_service.get_total_supply()
        return {"total_supply": total}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
