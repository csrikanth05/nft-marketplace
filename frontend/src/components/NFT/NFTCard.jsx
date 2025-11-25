import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Card from '../UI/Card';
import DisplayName from '../UI/DisplayName';
import './NFTCard.css';

// Use faster IPFS gateways
const IPFS_GATEWAYS = [
    'https://ipfs.io/ipfs/',
    'https://gateway.pinata.cloud/ipfs/',
    'https://cloudflare-ipfs.com/ipfs/'
];

export default function NFTCard({ nft }) {
    const [imageUrl, setImageUrl] = useState(null);
    const [metadata, setMetadata] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Fetch metadata from token_uri to get the actual image
        if (nft.token_uri) {
            const metadataUrl = nft.token_uri.replace('ipfs://', IPFS_GATEWAYS[0]);

            fetch(metadataUrl)
                .then(res => res.json())
                .then(data => {
                    setMetadata(data);
                    if (data.image) {
                        const imgUrl = data.image.replace('ipfs://', IPFS_GATEWAYS[0]);
                        setImageUrl(imgUrl);
                    }
                    setLoading(false);
                })
                .catch(err => {
                    console.error('Error fetching metadata:', err);
                    setLoading(false);
                });
        }
    }, [nft.token_uri]);

    return (
        <Link to={`/nft/${nft.token_id}`} className="nft-card-link">
            <Card hover className="nft-card">
                <div className="nft-image">
                    {loading ? (
                        <div className="nft-placeholder">
                            <div className="spinner-small"></div>
                        </div>
                    ) : imageUrl ? (
                        <img
                            src={imageUrl}
                            alt={metadata?.name || `NFT #${nft.token_id}`}
                            loading="lazy"
                        />
                    ) : (
                        <div className="nft-placeholder">No Image</div>
                    )}
                </div>
                <div className="nft-info">
                    <h4>{metadata?.name || nft.name || `NFT #${nft.token_id}`}</h4>
                    <p className="nft-owner" title={nft.owner_address}>
                        Owner: <DisplayName address={nft.owner_address} />
                    </p>
                    {nft.price_eth && (
                        <div className="nft-price">
                            <span className="price-label">Price</span>
                            <span className="price-value">{nft.price_eth} ETH</span>
                        </div>
                    )}
                </div>
            </Card>
        </Link>
    );
}
