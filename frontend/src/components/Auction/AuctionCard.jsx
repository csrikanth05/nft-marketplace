import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Card from '../UI/Card';
import './AuctionCard.css';

const IPFS_GATEWAY = 'https://ipfs.io/ipfs/';

export default function AuctionCard({ auction }) {
    const [timeLeft, setTimeLeft] = useState('');
    const [imageUrl, setImageUrl] = useState(null);
    const [metadata, setMetadata] = useState(null);

    useEffect(() => {
        const updateTimer = () => {
            const now = Math.floor(Date.now() / 1000);
            const end = auction.end_time;
            const diff = end - now;

            if (diff <= 0) {
                setTimeLeft('Ended');
                return;
            }

            const days = Math.floor(diff / 86400);
            const hours = Math.floor((diff % 86400) / 3600);
            const minutes = Math.floor((diff % 3600) / 60);

            if (days > 0) {
                setTimeLeft(`${days}d ${hours}h left`);
            } else if (hours > 0) {
                setTimeLeft(`${hours}h ${minutes}m left`);
            } else {
                setTimeLeft(`${minutes}m left`);
            }
        };

        updateTimer();
        const interval = setInterval(updateTimer, 60000); // Update every minute

        return () => clearInterval(interval);
    }, [auction.end_time]);

    useEffect(() => {
        // Fetch NFT metadata from backend
        const loadNFTImage = async () => {
            try {
                const nftResponse = await fetch(`http://localhost:8000/api/v1/db/nfts/${auction.token_id}`);
                const nft = await nftResponse.json();

                if (nft.token_uri) {
                    const metadataUrl = nft.token_uri.replace('ipfs://', IPFS_GATEWAY);
                    const metadataResponse = await fetch(metadataUrl);
                    const metadataData = await metadataResponse.json();
                    setMetadata(metadataData);

                    if (metadataData.image) {
                        const imgUrl = metadataData.image.replace('ipfs://', IPFS_GATEWAY);
                        setImageUrl(imgUrl);
                    }
                }
            } catch (err) {
                console.error('Error loading NFT image:', err);
            }
        };

        loadNFTImage();
    }, [auction.token_id]);

    return (
        <Link to={`/auction/${auction.auction_id}`} className="auction-card-link">
            <Card hover className="auction-card">
                <div className="auction-image">
                    {imageUrl ? (
                        <img src={imageUrl} alt={metadata?.name || `NFT #${auction.token_id}`} />
                    ) : (
                        <div className="placeholder">
                            <span>NFT #{auction.token_id}</span>
                        </div>
                    )}
                    <div className="auction-badge">
                        {auction.ended ? 'Ended' : 'Active'}
                    </div>
                </div>

                <div className="auction-info">
                    <h4>{metadata?.name || `NFT #${auction.token_id}`}</h4>

                    <div className="auction-stats">
                        <div className="stat">
                            <span className="label">Current Bid</span>
                            <span className="value">
                                {auction.highest_bid_eth > 0
                                    ? `${auction.highest_bid_eth} ETH`
                                    : `${auction.reserve_price_eth} ETH`}
                            </span>
                        </div>
                        <div className="stat">
                            <span className="label">Time Left</span>
                            <span className="value time">{timeLeft}</span>
                        </div>
                    </div>
                </div>
            </Card>
        </Link>
    );
}
