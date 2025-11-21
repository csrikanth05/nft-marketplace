from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Blockchain Configuration
    BLOCKCHAIN_RPC_URL: str = "http://127.0.0.1:7545"
    CHAIN_ID: int = 1337
    
    # Contract Addresses
    NFT_CONTRACT_ADDRESS: str
    MARKETPLACE_CONTRACT_ADDRESS: str
    AUCTION_CONTRACT_ADDRESS: str
    
    # Database
    DATABASE_URL: str = "sqlite:///./nft_marketplace.db"
    
    # JWT Authentication
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "NFT Marketplace API"
    DEBUG: bool = True
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8000"
    
    # IPFS / Pinata
    PINATA_JWT: str = ""
    PINATA_GATEWAY: str = "https://gateway.pinata.cloud/ipfs/"
    
    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
