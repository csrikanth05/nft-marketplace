from fastapi import APIRouter, HTTPException
from typing import List
from ..schemas.auction import (
    CreateAuctionRequest,
    CreateAuctionResponse,
    PlaceBidRequest,
    PlaceBidResponse,
    AuctionDetailsResponse,
    EndAuctionRequest,
    WithdrawBidRequest
)
from ..services.auction_service import auction_service

router = APIRouter(prefix="/auction", tags=["Auction"])


@router.post("/create", response_model=CreateAuctionResponse)
async def create_auction(request: CreateAuctionRequest):
    """
    Create a new auction
    
    - **nft_contract_address**: Address of the NFT contract
    - **token_id**: Token ID to auction
    - **start_time**: Auction start time (unix timestamp)
    - **end_time**: Auction end time (unix timestamp)
    - **reserve_price_eth**: Minimum acceptable price in ETH
    - **from_address**: Seller address (must be NFT owner)
    - **private_key**: Private key for signing
    
    Note: NFT must be approved for the auction contract before creating auction
    """
    try:
        result = auction_service.create_auction(
            nft_contract_address=request.nft_contract_address,
            token_id=request.token_id,
            start_time=request.start_time,
            end_time=request.end_time,
            reserve_price_eth=request.reserve_price_eth,
            from_address=request.from_address,
            private_key=request.private_key
        )
        return CreateAuctionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{auction_id}/bid", response_model=PlaceBidResponse)
async def place_bid(auction_id: int, request: PlaceBidRequest):
    """
    Place a bid on an auction
    
    - **auction_id**: ID of the auction
    - **bid_amount_eth**: Bid amount in ETH (must be higher than current highest bid)
    - **from_address**: Bidder address
    - **private_key**: Private key for signing
    
    If outbid, previous bidder can withdraw their refunded bid
    """
    try:
        tx_hash = auction_service.place_bid(
            auction_id=auction_id,
            bid_amount_eth=request.bid_amount_eth,
            from_address=request.from_address,
            private_key=request.private_key
        )
        return PlaceBidResponse(
            transaction_hash=tx_hash,
            auction_id=auction_id,
            bid_amount_eth=request.bid_amount_eth
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{auction_id}/end")
async def end_auction(auction_id: int, request: EndAuctionRequest):
    """
    End an auction
    
    Can only be called after the auction end time has passed.
    Transfers NFT to highest bidder and distributes payments.
    """
    try:
        tx_hash = auction_service.end_auction(
            auction_id=auction_id,
            from_address=request.from_address,
            private_key=request.private_key
        )
        return {"transaction_hash": tx_hash, "auction_id": auction_id, "status": "ended"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{auction_id}")
async def cancel_auction(auction_id: int, from_address: str, private_key: str):
    """
    Cancel an auction
    
    Can only be cancelled if there are no bids yet.
    Only the seller can cancel their auction.
    """
    try:
        tx_hash = auction_service.cancel_auction(
            auction_id=auction_id,
            from_address=from_address,
            private_key=private_key
        )
        return {"transaction_hash": tx_hash, "auction_id": auction_id, "status": "cancelled"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{auction_id}/withdraw")
async def withdraw_bid(auction_id: int, request: WithdrawBidRequest):
    """
    Withdraw a refunded bid
    
    When outbid, bidders can withdraw their previous bid amount
    """
    try:
        tx_hash = auction_service.withdraw_bid(
            auction_id=auction_id,
            from_address=request.from_address,
            private_key=request.private_key
        )
        return {"transaction_hash": tx_hash, "auction_id": auction_id, "status": "withdrawn"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{auction_id}", response_model=AuctionDetailsResponse)
async def get_auction(auction_id: int):
    """
    Get details of a specific auction
    
    Returns seller, NFT info, times, prices, highest bidder, and status
    """
    try:
        auction = auction_service.get_auction(auction_id)
        return AuctionDetailsResponse(**auction)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{auction_id}/pending-return/{bidder_address}")
async def get_pending_return(auction_id: int, bidder_address: str):
    """
    Get pending return amount for a bidder
    
    Shows how much ETH a bidder can withdraw after being outbid
    """
    try:
        amount = auction_service.get_pending_return(auction_id, bidder_address)
        return {"auction_id": auction_id, "bidder": bidder_address, "pending_return_eth": amount}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/active/all", response_model=List[AuctionDetailsResponse])
async def get_all_active_auctions():
    """
    Get all active auctions
    
    Returns a list of all currently active and not-ended auctions
    """
    try:
        auctions = auction_service.get_all_active_auctions()
        return [AuctionDetailsResponse(**auction) for auction in auctions]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
