from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import time
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
from ..services.web3_service import web3_service
from ..services.email_service import email_service
from ..database import get_db
from ..models.models import Auction, Bid, NFT, User

router = APIRouter(prefix="/auction", tags=["Auction"])


@router.post("/create", response_model=CreateAuctionResponse)
async def create_auction(request: CreateAuctionRequest, db: Session = Depends(get_db)):
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
        
        # Save to DB
        try:
            # Find NFT
            nft = db.query(NFT).filter(
                NFT.contract_address == request.nft_contract_address,
                NFT.token_id == request.token_id
            ).first()
            
            if nft:
                new_auction = Auction(
                    auction_id=result['auction_id'],
                    nft_id=nft.id,
                    seller_address=request.from_address,
                    start_time=request.start_time,
                    end_time=request.end_time,
                    reserve_price_eth=request.reserve_price_eth,
                    reserve_price_wei=str(web3_service.w3.to_wei(request.reserve_price_eth, 'ether')),
                    active=True,
                    ended=False
                )
                db.add(new_auction)
                db.commit()
        except Exception as e:
            print(f"Failed to save auction to DB: {e}")
            
        return CreateAuctionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{auction_id}/bid", response_model=PlaceBidResponse)
async def place_bid(auction_id: int, request: PlaceBidRequest, db: Session = Depends(get_db)):
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
        
        # Save to DB
        try:
            auction = db.query(Auction).filter(Auction.auction_id == auction_id).first()
            if auction:
                # Store previous bidder info for email
                previous_bidder_addr = auction.highest_bidder_address
                
                # Update auction highest bid
                auction.highest_bid_eth = request.bid_amount_eth
                auction.highest_bid_wei = str(web3_service.w3.to_wei(request.bid_amount_eth, 'ether'))
                auction.highest_bidder_address = request.from_address
                
                # Create Bid record
                new_bid = Bid(
                    auction_id=auction.id,
                    bidder_address=request.from_address,
                    amount_eth=request.bid_amount_eth,
                    amount_wei=str(web3_service.w3.to_wei(request.bid_amount_eth, 'ether')),
                    timestamp=int(time.time())
                )
                db.add(new_bid)
                db.commit()
                
                # Send Emails
                try:
                    # 1. Send Bid Placed Email to new bidder
                    bidder = db.query(User).filter(User.address == request.from_address).first()
                    nft = db.query(NFT).filter(NFT.id == auction.nft_id).first()
                    nft_name = f"NFT #{nft.token_id}" if nft else f"NFT #{auction.token_id}"
                    
                    if bidder and bidder.email:
                        email_service.send_bid_placed_email(
                            to_email=bidder.email,
                            username=bidder.username or "User",
                            nft_name=nft_name,
                            bid_amount=request.bid_amount_eth
                        )
                        
                    # 2. Send Outbid Email to previous bidder
                    if previous_bidder_addr and previous_bidder_addr != request.from_address and previous_bidder_addr != '0x0000000000000000000000000000000000000000':
                        prev_bidder = db.query(User).filter(User.address == previous_bidder_addr).first()
                        if prev_bidder and prev_bidder.email:
                            email_service.send_outbid_email(
                                to_email=prev_bidder.email,
                                username=prev_bidder.username or "User",
                                nft_name=nft_name,
                                new_bid_amount=request.bid_amount_eth
                            )
                except Exception as e:
                    print(f"Failed to send bid emails: {e}")
                    
        except Exception as e:
            print(f"Failed to save bid to DB: {e}")
            
        return PlaceBidResponse(
            transaction_hash=tx_hash,
            auction_id=auction_id,
            bid_amount_eth=request.bid_amount_eth
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{auction_id}/end", response_model=str)
async def end_auction(auction_id: int, request: EndAuctionRequest, db: Session = Depends(get_db)):
    """
    End an auction
    
    - **auction_id**: ID of the auction to end
    - **from_address**: Address of the seller
    - **private_key**: Private key for signing
    
    This should only be called after the auction end time has passed.
    It finalizes the auction on-chain, transfers the NFT to the highest bidder,
    and distributes funds.
    """
    try:
        tx_hash = auction_service.end_auction(
            auction_id=auction_id,
            from_address=request.from_address,
            private_key=request.private_key
        )
        
        # Update DB
        try:
            auction = db.query(Auction).filter(Auction.auction_id == auction_id).first()
            if auction:
                auction.active = False
                auction.ended = True
                
                # Update NFT owner if sold
                nft = db.query(NFT).filter(NFT.id == auction.nft_id).first()
                winner_address = auction.highest_bidder_address
                
                if nft and winner_address and winner_address != '0x0000000000000000000000000000000000000000':
                    nft.owner_address = winner_address
                    nft.is_listed = False # NFT is no longer listed after sale
                    
                    # Send Auction Won Email
                    try:
                        winner = db.query(User).filter(User.address == winner_address).first()
                        nft_name = f"NFT #{nft.token_id}"
                        
                        if winner and winner.email:
                            email_service.send_auction_won_email(
                                to_email=winner.email,
                                username=winner.username or "User",
                                nft_name=nft_name,
                                winning_bid=auction.highest_bid_eth,
                                tx_hash=tx_hash
                            )
                    except Exception as e:
                        print(f"Failed to send auction won email: {e}")
                        
                db.commit()
        except Exception as e:
            print(f"Failed to update auction/NFT in DB: {e}")
            
        return tx_hash
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


@router.post("/{auction_id}/withdraw", response_model=str)
async def withdraw_bid(auction_id: int, request: WithdrawBidRequest, db: Session = Depends(get_db)):
    """
    Withdraw refunded bid
    
    - **auction_id**: ID of the auction
    - **from_address**: Bidder address
    - **private_key**: Private key for signing
    """
    try:
        tx_hash = auction_service.withdraw_bid(
            auction_id=auction_id,
            from_address=request.from_address,
            private_key=request.private_key
        )
        
        # Update DB - remove bid record
        try:
            bid = db.query(Bid).filter(
                Bid.auction_id == auction_id,
                Bid.bidder_address == request.from_address
            ).first()
            if bid:
                db.delete(bid)
                db.commit()
        except Exception as e:
            print(f"Failed to remove bid from DB: {e}")
            
        return tx_hash
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/blockchain-time")
async def get_blockchain_time():
    """
    Get current blockchain timestamp
    
    Returns the current block timestamp from the blockchain
    """
    try:
        from app.services.web3_service import web3_service
        latest_block = web3_service.w3.eth.get_block('latest')
        return {"timestamp": latest_block['timestamp']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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


@router.get("/user/{address}/participated", response_model=List[AuctionDetailsResponse])
async def get_user_auctions(address: str, db: Session = Depends(get_db)):
    """
    Get auctions the user has participated in (created or bid on)
    """
    try:
        # Get auctions created by user
        created_auctions = db.query(Auction).filter(Auction.seller_address == address).all()
        
        # Get auctions user bid on
        bids = db.query(Bid).filter(Bid.bidder_address == address).all()
        bid_auction_ids = [bid.auction_id for bid in bids]
        bid_auctions = db.query(Auction).filter(Auction.id.in_(bid_auction_ids)).all()
        
        # Combine and deduplicate
        all_auctions = list({a.id: a for a in (created_auctions + bid_auctions)}.values())
        
        # Convert to response format (fetch fresh data from chain for accuracy)
        response = []
        for auction in all_auctions:
            try:
                # We use the on-chain ID
                chain_data = auction_service.get_auction(auction.auction_id)
                response.append(AuctionDetailsResponse(**chain_data))
            except Exception as e:
                print(f"Error fetching auction {auction.auction_id}: {e}")
                continue
                
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
