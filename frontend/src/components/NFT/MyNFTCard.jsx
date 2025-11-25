import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Card from '../UI/Card';
import Button from '../UI/Button';
import DisplayName from '../UI/DisplayName';
import './MyNFTCard.css';

// Use faster IPFS gateways
const IPFS_GATEWAYS = [
    'https://ipfs.io/ipfs/',
    'https://gateway.pinata.cloud/ipfs/',
    'https://cloudflare-ipfs.com/ipfs/'
];

export default function MyNFTCard({ nft, onList }) {
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
        <Card hover className="my-nft-card">
            <Link to={`/nft/${nft.token_id}`} className="nft-card-link">
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
            </Link>

            <div className="nft-info">
                <h4>{metadata?.name || nft.name || `NFT #${nft.token_id}`}</h4>
                <p className="nft-owner" title={nft.owner_address}>
                    Owner: <DisplayName address={nft.owner_address} />
                </p>

                {nft.is_listed ? (
                    <div className="listed-badge">
                        <span>Listed for {nft.price_eth} ETH</span>
                    </div>
                ) : (
                    <Button
                        variant="primary"
                        size="sm"
                        onClick={() => onList(nft)}
                        className="list-button"
                    >
                        List for Sale
                    </Button>
                )}
            </div>
        </Card>
    );
}
