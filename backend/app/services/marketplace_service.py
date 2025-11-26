from web3 import Web3
from .web3_service import web3_service
from typing import List, Dict, Any


class MarketplaceService:
    def __init__(self):
        self.contract = web3_service.marketplace_contract
        self.w3 = web3_service.w3
    
    def list_nft(
        self,
        nft_contract_address: str,
        token_id: int,
        price_eth: float,
        from_address: str,
        private_key: str
    ) -> Dict[str, Any]:
        """List an NFT for sale"""
        price_wei = self.w3.to_wei(price_eth, 'ether')
        
        transaction = self.contract.functions.listNFT(
            Web3.to_checksum_address(nft_contract_address),
            token_id,
            price_wei
        ).build_transaction({
            'from': Web3.to_checksum_address(from_address)
        })
        
        tx_hash = web3_service.send_transaction(transaction, private_key)
        
        # Get listing ID from event
        receipt = self.w3.eth.get_transaction_receipt(tx_hash)
        nft_listed_event = self.contract.events.NFTListed().process_receipt(receipt)
        listing_id = nft_listed_event[0]['args']['listingId'] if nft_listed_event else None
        
        return {
            "transaction_hash": tx_hash,
            "listing_id": listing_id,
            "token_id": token_id,
            "price_eth": price_eth
        }
    
    def buy_nft(
        self,
        listing_id: int,
        from_address: str,
        private_key: str
    ) -> Dict[str, Any]:
        """Buy a listed NFT"""
        # Get listing details to know the price
        listing = self.get_listing(listing_id)
        
        if not listing['active']:
            raise ValueError("Listing is not active")
        
        transaction = self.contract.functions.buyNFT(listing_id).build_transaction({
            'from': Web3.to_checksum_address(from_address),
            'value': int(listing['price_wei'])
        })
        
        tx_hash = web3_service.send_transaction(transaction, private_key)
        
        # Wait for receipt to get gas used
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        gas_used = receipt['gasUsed']
        effective_gas_price = receipt['effectiveGasPrice']
        gas_fee_eth = self.w3.from_wei(gas_used * effective_gas_price, 'ether')
        
        return {
            "transaction_hash": tx_hash,
            "gas_fee_eth": float(gas_fee_eth),
            "price_eth": listing['price_eth'],
            "seller_address": listing['seller'],
            "nft_contract": listing['nft_contract'],
            "token_id": listing['token_id']
        }

    def estimate_buy_gas(self, listing_id: int, from_address: str) -> float:
        """Estimate gas fee for buying an NFT"""
        listing = self.get_listing(listing_id)
        if not listing['active']:
            raise ValueError("Listing is not active")

        # Estimate gas
        gas_estimate = self.contract.functions.buyNFT(listing_id).estimate_gas({
            'from': Web3.to_checksum_address(from_address),
            'value': int(listing['price_wei'])
        })
        
        # Get current gas price
        gas_price = self.w3.eth.gas_price
        
        # Calculate fee in ETH
        fee_wei = gas_estimate * gas_price
        return float(self.w3.from_wei(fee_wei, 'ether'))
    
    def cancel_listing(
        self,
        listing_id: int,
        from_address: str,
        private_key: str
    ) -> str:
        """Cancel a listing"""
        transaction = self.contract.functions.cancelListing(listing_id).build_transaction({
            'from': Web3.to_checksum_address(from_address)
        })
        
        return web3_service.send_transaction(transaction, private_key)
    
    def get_listing(self, listing_id: int) -> Dict[str, Any]:
        """Get listing details"""
        listing = self.contract.functions.getListing(listing_id).call()
        
        return {
            "listing_id": listing_id,
            "seller": listing[0],
            "nft_contract": listing[1],
            "token_id": listing[2],
            "price_wei": listing[3],
            "price_eth": self.w3.from_wei(listing[3], 'ether'),
            "active": listing[4]
        }
    
    def get_platform_fee(self) -> int:
        """Get platform fee in basis points"""
        return self.contract.functions.platformFee().call()
    
    def get_current_listing_id(self) -> int:
        """Get the current listing ID counter"""
        return self.contract.functions.getCurrentListingId().call()
    
    def get_all_active_listings(self) -> List[Dict[str, Any]]:
        """Get all active listings (by querying all listing IDs)"""
        current_id = self.get_current_listing_id()
        active_listings = []
        
        for listing_id in range(1, current_id + 1):
            try:
                listing = self.get_listing(listing_id)
                if listing['active']:
                    active_listings.append(listing)
            except:
                continue
        
        return active_listings


# Global instance
marketplace_service = MarketplaceService()
