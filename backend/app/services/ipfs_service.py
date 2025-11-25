import requests
import json
import io
from typing import Dict, Any, Optional, List
from ..config import settings


class IPFSService:
    """Service for interacting with IPFS via Pinata"""
    
    def __init__(self):
        self.pinata_jwt = settings.PINATA_JWT
        self.pinata_api_url = "https://api.pinata.cloud"
        self.gateway_url = "https://gateway.pinata.cloud/ipfs/"
        
        if not self.pinata_jwt:
            raise ValueError("PINATA_JWT not configured in environment variables")
        
        self.headers = {
            "Authorization": f"Bearer {self.pinata_jwt}"
        }
    
    def upload_file(self, file_content: bytes, filename: str) -> Dict[str, str]:
        """Upload a file to IPFS via Pinata"""
        files = {
            'file': (filename, io.BytesIO(file_content))
        }
        
        response = requests.post(
            f'{self.pinata_api_url}/pinning/pinFileToIPFS',
            files=files,
            headers=self.headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Pinata upload failed: {response.text}")
        
        result = response.json()
        ipfs_hash = result['IpfsHash']
        
        return {
            'ipfs_hash': ipfs_hash,
            'ipfs_url': self.get_ipfs_url(ipfs_hash),
            'ipfs_uri': self.get_ipfs_uri(ipfs_hash)
        }
    
    def upload_nft_metadata(
        self,
        name: str,
        description: str,
        image_ipfs_hash: str,
        attributes: Optional[List[Dict[str, str]]] = None,
        category: Optional[str] = None,
        external_url: Optional[str] = None,
        collection: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Upload NFT metadata JSON to IPFS.
        
        Creates a standard NFT metadata JSON following OpenSea standards.
        """
        metadata = {
            "name": name,
            "description": description,
            "image": f"ipfs://{image_ipfs_hash}"
        }
        
        # Add optional fields
        if attributes:
            metadata["attributes"] = attributes
        if category:
            metadata["category"] = category
        if external_url:
            metadata["external_url"] = external_url
        if collection:
            metadata["collection"] = collection
        
        # Convert to JSON
        metadata_json = json.dumps(metadata, indent=2)
        
        # Upload to Pinata
        files = {
            'file': ('metadata.json', metadata_json, 'application/json')
        }
        
        pinata_options = json.dumps({
            'cidVersion': 1
        })
        
        data = {
            'pinataOptions': pinata_options,
            'pinataMetadata': json.dumps({
                'name': f'{name}_metadata.json'
            })
        }
        
        response = requests.post(
            f'{self.pinata_api_url}/pinning/pinFileToIPFS',
            files=files,
            data=data,
            headers=self.headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Pinata upload failed: {response.text}")
        
        result = response.json()
        ipfs_hash = result['IpfsHash']
        
        return {
            'ipfs_hash': ipfs_hash,
            'ipfs_url': self.get_ipfs_url(ipfs_hash),
            'ipfs_uri': self.get_ipfs_uri(ipfs_hash)
        }
    
    def get_ipfs_url(self, ipfs_hash: str) -> str:
        """Convert IPFS hash to gateway URL"""
        return f"{self.gateway_url}{ipfs_hash}"
    
    def get_ipfs_uri(self, ipfs_hash: str) -> str:
        """Convert IPFS hash to ipfs:// URI"""
        return f"ipfs://{ipfs_hash}"


# Global instance
ipfs_service = IPFSService()
