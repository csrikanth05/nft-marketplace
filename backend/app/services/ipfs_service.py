import requests
import json
import io
from typing import Dict, Any, Optional
from ..config import settings


class IPFSService:
    """Service for interacting with IPFS via Pinata"""
    
    def __init__(self):
        self.pinata_jwt = settings.PINATA_JWT
        self.gateway_url = settings.PINATA_GATEWAY
        self.pin_url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
        self.pin_json_url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
        
        if not self.pinata_jwt:
            raise ValueError("PINATA_JWT not configured in environment variables")
    
    def _get_headers(self, content_type: Optional[str] = None) -> Dict[str, str]:
        """Get headers for Pinata API requests"""
        headers = {
            "Authorization": f"Bearer {self.pinata_jwt}"
        }
        if content_type:
            headers["Content-Type"] = content_type
        return headers
    
    def upload_file(self, file_content: bytes, filename: str) -> Dict[str, str]:
        """
        Upload a file to IPFS via Pinata
        
        Args:
            file_content: File content as bytes
            filename: Name of the file
            
        Returns:
            Dict with 'ipfs_hash' and 'ipfs_url'
        """
        files = {
            'file': (filename, io.BytesIO(file_content))
        }
        
        response = requests.post(
            self.pin_url,
            files=files,
            headers=self._get_headers()
        )
        
        if response.status_code != 200:
            raise Exception(f"Pinata upload failed: {response.text}")
        
        result = response.json()
        ipfs_hash = result['IpfsHash']
        
        return {
            'ipfs_hash': ipfs_hash,
            'ipfs_url': f"{self.gateway_url}{ipfs_hash}",
            'ipfs_uri': f"ipfs://{ipfs_hash}"
        }
    
    def upload_json(self, data: Dict[str, Any], name: Optional[str] = None) -> Dict[str, str]:
        """
        Upload JSON data to IPFS via Pinata
        
        Args:
            data: Dictionary to upload as JSON
            name: Optional name for the pinned content
            
        Returns:
            Dict with 'ipfs_hash' and 'ipfs_url'
        """
        payload = {
            "pinataContent": data
        }
        
        if name:
            payload["pinataMetadata"] = {"name": name}
        
        response = requests.post(
            self.pin_json_url,
            json=payload,
            headers=self._get_headers("application/json")
        )
        
        if response.status_code != 200:
            raise Exception(f"Pinata JSON upload failed: {response.text}")
        
        result = response.json()
        ipfs_hash = result['IpfsHash']
        
        return {
            'ipfs_hash': ipfs_hash,
            'ipfs_url': f"{self.gateway_url}{ipfs_hash}",
            'ipfs_uri': f"ipfs://{ipfs_hash}"
        }
    
    def upload_nft_metadata(
        self,
        name: str,
        description: str,
        image_ipfs_hash: str,
        attributes: Optional[list] = None
    ) -> Dict[str, str]:
        """
        Upload NFT metadata following ERC-721 standard
        
        Args:
            name: NFT name
            description: NFT description
            image_ipfs_hash: IPFS hash of the NFT image
            attributes: Optional list of trait attributes
            
        Returns:
            Dict with 'ipfs_hash' and 'ipfs_url' for the metadata
        """
        metadata = {
            "name": name,
            "description": description,
            "image": f"ipfs://{image_ipfs_hash}"
        }
        
        if attributes:
            metadata["attributes"] = attributes
        
        return self.upload_json(metadata, name=f"{name}_metadata")
    
    def get_ipfs_url(self, ipfs_hash: str) -> str:
        """Convert IPFS hash to gateway URL"""
        return f"{self.gateway_url}{ipfs_hash}"
    
    def get_ipfs_uri(self, ipfs_hash: str) -> str:
        """Convert IPFS hash to ipfs:// URI"""
        return f"ipfs://{ipfs_hash}"


# Global instance
ipfs_service = IPFSService()
