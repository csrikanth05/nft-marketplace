import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// NFT APIs
export const getNFTs = () => api.get('/db/nfts');
export const getNFTById = (tokenId) => api.get(`/db/nfts/${tokenId}`);
export const getUserNFTs = (address) => api.get(`/db/users/${address}/nfts`);

// Marketplace APIs
export const getListings = (activeOnly = true) => api.get(`/db/listings?active_only=${activeOnly}`);
export const getListingById = (listingId) => api.get(`/db/listings/${listingId}`);

// Auction APIs
export const getAuctions = (activeOnly = true) => api.get(`/db/auctions?active_only=${activeOnly}`);
export const getAuctionById = (auctionId) => api.get(`/db/auctions/${auctionId}`);

// IPFS APIs
export const uploadImage = (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/ipfs/upload-image', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
    });
};

export const uploadNFTBundle = (file, name, description) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('name', name);
    formData.append('description', description);
    return api.post('/ipfs/upload-nft', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
    });
};

// Blockchain Write APIs (require wallet)
export const mintNFT = (data) => api.post('/nfts/mint', data);
export const listNFT = (data) => api.post('/marketplace/list', data);
export const buyNFT = (data) => api.post('/marketplace/buy', data);

export default api;
