from web3 import Web3
from .web3_service import web3_service
from typing import List, Dict, Any


class NFTService:
    def __init__(self):
        self.contract = web3_service.nft_contract
        self.w3 = web3_service.w3
    
    def mint_nft(
        self,
        to_address: str,
        token_uri: str,
        royalty_receiver: str,
        royalty_fee: int,
        from_address: str,
        private_key: str
    ) -> Dict[str, Any]:
        """Mint a new NFT"""
        # Build transaction
        transaction = self.contract.functions.mintNFT(
            Web3.to_checksum_address(to_address),
            token_uri,
            Web3.to_checksum_address(royalty_receiver),
            royalty_fee
        ).build_transaction({
            'from': Web3.to_checksum_address(from_address)
        })
        
        # Send transaction
        tx_hash = web3_service.send_transaction(transaction, private_key)
        
        # Get receipt to extract token ID from events
        receipt = self.w3.eth.get_transaction_receipt(tx_hash)
        
        # Parse NFTMinted event
        nft_minted_event = self.contract.events.NFTMinted().process_receipt(receipt)
        token_id = nft_minted_event[0]['args']['tokenId'] if nft_minted_event else None
        
        return {
            "transaction_hash": tx_hash,
            "token_id": token_id,
            "to_address": to_address,
            "token_uri": token_uri
        }
    
    def get_nft_details(self, token_id: int) -> Dict[str, Any]:
        """Get NFT details"""
        try:
            owner = self.contract.functions.ownerOf(token_id).call()
            token_uri = self.contract.functions.tokenURI(token_id).call()
            creator = self.contract.functions.creatorOf(token_id).call()
            
            # Get royalty info (for 1 ETH sale)
            sale_price = self.w3.to_wei(1, 'ether')
            royalty_info = self.contract.functions.royaltyInfo(token_id, sale_price).call()
            
            return {
                "token_id": token_id,
                "owner": owner,
                "creator": creator,
                "token_uri": token_uri,
                "royalty_receiver": royalty_info[0],
                "royalty_amount": self.w3.from_wei(royalty_info[1], 'ether')
            }
        except Exception as e:
            raise ValueError(f"Token {token_id} does not exist or error occurred: {str(e)}")
    
    def get_tokens_by_owner(self, owner_address: str) -> List[int]:
        """Get all token IDs owned by an address"""
        tokens = self.contract.functions.tokensOfOwner(
            Web3.to_checksum_address(owner_address)
        ).call()
        return [int(token) for token in tokens]
    
    def transfer_nft(
        self,
        from_address: str,
        to_address: str,
        token_id: int,
        private_key: str
    ) -> str:
        """Transfer NFT to another address"""
        transaction = self.contract.functions.transferFrom(
            Web3.to_checksum_address(from_address),
            Web3.to_checksum_address(to_address),
            token_id
        ).build_transaction({
            'from': Web3.to_checksum_address(from_address)
        })
        
        return web3_service.send_transaction(transaction, private_key)
    
    def burn_nft(
        self,
        token_id: int,
        from_address: str,
        private_key: str
    ) -> str:
        """Burn an NFT"""
        transaction = self.contract.functions.burn(token_id).build_transaction({
            'from': Web3.to_checksum_address(from_address)
        })
        
        return web3_service.send_transaction(transaction, private_key)
    
    def get_total_supply(self) -> int:
        """Get total number of minted NFTs"""
        return self.contract.functions.getCurrentTokenId().call()


# Global instance
nft_service = NFTService()
