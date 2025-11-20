from web3 import Web3
from web3.contract import Contract
import json
from pathlib import Path
from ..config import settings


class Web3Service:
    def __init__(self):
        # Increase timeout for Ganache transactions
        self.w3 = Web3(Web3.HTTPProvider(
            settings.BLOCKCHAIN_RPC_URL,
            request_kwargs={'timeout': 60}
        ))
        
        if not self.w3.is_connected():
            raise ConnectionError("Failed to connect to blockchain")
        
        # Load contract ABIs
        self.nft_contract = self._load_contract(
            settings.NFT_CONTRACT_ADDRESS,
            "NFTContract"
        )
        self.marketplace_contract = self._load_contract(
            settings.MARKETPLACE_CONTRACT_ADDRESS,
            "Marketplace"
        )
        self.auction_contract = self._load_contract(
            settings.AUCTION_CONTRACT_ADDRESS,
            "Auction"
        )
    
    def _load_contract(self, address: str, contract_name: str) -> Contract:
        """Load contract ABI and create contract instance"""
        # Path to compiled contract JSON
        contract_path = Path(__file__).parent.parent.parent.parent / "build" / "contracts" / f"{contract_name}.json"
        
        with open(contract_path, 'r') as f:
            contract_json = json.load(f)
            abi = contract_json['abi']
        
        return self.w3.eth.contract(
            address=Web3.to_checksum_address(address),
            abi=abi
        )
    
    def get_account_balance(self, address: str) -> float:
        """Get ETH balance of an address"""
        balance_wei = self.w3.eth.get_balance(Web3.to_checksum_address(address))
        return self.w3.from_wei(balance_wei, 'ether')
    
    def send_transaction(self, transaction: dict, private_key: str) -> str:
        """Sign and send a transaction"""
        # Build transaction
        transaction['nonce'] = self.w3.eth.get_transaction_count(transaction['from'])
        
        # Use fixed gas limit instead of estimation to avoid timeouts
        transaction['gas'] = 3000000
        
        # Don't set gasPrice - let Web3.py handle it automatically
        transaction['chainId'] = settings.CHAIN_ID
        
        # Sign transaction
        signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key)
        
        # Send transaction
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        # Return hash immediately without waiting for receipt
        return tx_hash.hex()


# Global instance
web3_service = Web3Service()
