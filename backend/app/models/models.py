from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, BigInteger, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, unique=True, index=True)
    username = Column(String, nullable=True)
    avatar = Column(String, nullable=True)  # Avatar identifier (emoji)
    email = Column(String, nullable=True)
    email_verified = Column(Boolean, default=False)
    
    nfts = relationship("NFT", back_populates="owner_user")
    listings = relationship("Listing", back_populates="seller_user")
    auctions = relationship("Auction", back_populates="seller_user")
    bids = relationship("Bid", back_populates="bidder_user")
    collections = relationship("Collection", back_populates="owner_user")


class NFT(Base):
    __tablename__ = "nfts"

    id = Column(Integer, primary_key=True, index=True)
    token_id = Column(Integer, index=True)
    contract_address = Column(String, index=True)
    owner_address = Column(String, ForeignKey("users.address"))
    creator_address = Column(String)
    token_uri = Column(String)
    is_listed = Column(Boolean, default=False)
    
    owner_user = relationship("User", back_populates="nfts")
    active_listing = relationship("Listing", uselist=False, back_populates="nft", 
                                primaryjoin="and_(NFT.id==Listing.nft_id, Listing.active==True)")
    active_auction = relationship("Auction", uselist=False, back_populates="nft",
                                primaryjoin="and_(NFT.id==Auction.nft_id, Auction.active==True)")
    collection_memberships = relationship("CollectionNFT", back_populates="nft", cascade="all, delete-orphan")


class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(Integer, index=True)  # On-chain listing ID
    nft_id = Column(Integer, ForeignKey("nfts.id"))
    seller_address = Column(String, ForeignKey("users.address"))
    price_wei = Column(String)  # Stored as string to handle large numbers
    price_eth = Column(Float)
    active = Column(Boolean, default=True)
    sold = Column(Boolean, default=False)
    cancelled = Column(Boolean, default=False)
    
    nft = relationship("NFT", back_populates="active_listing")
    seller_user = relationship("User", back_populates="listings")


class Auction(Base):
    __tablename__ = "auctions"

    id = Column(Integer, primary_key=True, index=True)
    auction_id = Column(Integer, index=True)  # On-chain auction ID
    nft_id = Column(Integer, ForeignKey("nfts.id"))
    seller_address = Column(String, ForeignKey("users.address"))
    start_time = Column(BigInteger)
    end_time = Column(BigInteger)
    reserve_price_wei = Column(String)
    reserve_price_eth = Column(Float)
    highest_bid_wei = Column(String, default="0")
    highest_bid_eth = Column(Float, default=0.0)
    highest_bidder_address = Column(String, nullable=True)
    active = Column(Boolean, default=True)
    ended = Column(Boolean, default=False)
    cancelled = Column(Boolean, default=False)
    
    nft = relationship("NFT", back_populates="active_auction")
    seller_user = relationship("User", back_populates="auctions")
    bids = relationship("Bid", back_populates="auction")


class Bid(Base):
    __tablename__ = "bids"

    id = Column(Integer, primary_key=True, index=True)
    auction_id = Column(Integer, ForeignKey("auctions.id"))
    bidder_address = Column(String, ForeignKey("users.address"))
    amount_wei = Column(String)
    amount_eth = Column(Float)
    timestamp = Column(BigInteger)
    
    auction = relationship("Auction", back_populates="bids")
    bidder_user = relationship("User", back_populates="bids")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_hash = Column(String, index=True)
    nft_id = Column(Integer, ForeignKey("nfts.id"))
    buyer_address = Column(String, ForeignKey("users.address"))
    seller_address = Column(String, ForeignKey("users.address"))
    price_eth = Column(Float)
    gas_fee_eth = Column(Float, nullable=True)
    timestamp = Column(BigInteger)
    transaction_type = Column(String)  # 'buy', 'sell', 'mint'
    
    nft = relationship("NFT")
    buyer = relationship("User", foreign_keys=[buyer_address])
    seller = relationship("User", foreign_keys=[seller_address])


class Collection(Base):
    __tablename__ = "collections"

    id = Column(Integer, primary_key=True, index=True)
    owner_address = Column(String, ForeignKey("users.address"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String, nullable=True)
    banner_image = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    owner_user = relationship("User", back_populates="collections")
    collection_nfts = relationship("CollectionNFT", back_populates="collection", cascade="all, delete-orphan")


class CollectionNFT(Base):
    __tablename__ = "collection_nfts"

    id = Column(Integer, primary_key=True, index=True)
    collection_id = Column(Integer, ForeignKey("collections.id"), nullable=False)
    nft_id = Column(Integer, ForeignKey("nfts.id"), nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow)
    
    collection = relationship("Collection", back_populates="collection_nfts")
    nft = relationship("NFT", back_populates="collection_memberships")


class EventProcessed(Base):
    __tablename__ = "events_processed"

    id = Column(Integer, primary_key=True, index=True)
    contract_name = Column(String, unique=True)
    last_processed_block = Column(Integer, default=0)
