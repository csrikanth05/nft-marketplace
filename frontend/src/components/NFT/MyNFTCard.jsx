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
    const [error, setError] = useState(false);
    const [retryCount, setRetryCount] = useState(0);

    // Expanded list of IPFS gateways for better reliability
    const IPFS_GATEWAYS = [
        'https://ipfs.io/ipfs/',
        'https://gateway.pinata.cloud/ipfs/',
        'https://cloudflare-ipfs.com/ipfs/',
        'https://dweb.link/ipfs/',
        'https://nftstorage.link/ipfs/'
    ];

    useEffect(() => {
        loadMetadata();
    }, [nft.token_uri, retryCount]);

    useEffect(() => {
        let retryTimer;
        if (error) {
            // Retry every 5 seconds if there's an error
            retryTimer = setTimeout(() => {
                setRetryCount(prev => prev + 1);
            }, 5000);
        }
        return () => {
            if (retryTimer) clearTimeout(retryTimer);
        };
    }, [error]);

    const loadMetadata = () => {
        setLoading(true);
        setError(false);

        if (nft.token_uri) {
            // Rotate gateways based on retry count
            const gatewayIndex = retryCount % IPFS_GATEWAYS.length;
            const currentGateway = IPFS_GATEWAYS[gatewayIndex];

            // console.log(`Attempting load with gateway: ${currentGateway} (Retry: ${retryCount})`);

            const metadataUrl = nft.token_uri.replace('ipfs://', currentGateway);

            fetch(metadataUrl)
                .then(res => {
                    if (!res.ok) throw new Error('Failed to fetch metadata');
                    return res.json();
                })
                .then(data => {
                    setMetadata(data);
                    if (data.image) {
                        // Add cache buster if retrying to force new request
                        const cacheBuster = retryCount > 0 ? `?retry=${retryCount}` : '';
                        const imgUrl = data.image.replace('ipfs://', currentGateway) + cacheBuster;
                        setImageUrl(imgUrl);
                    }
                    setLoading(false);
                })
                .catch(err => {
                    // console.error('Error fetching metadata:', err);
                    setError(true);
                    setLoading(false);
                });
        } else {
            setLoading(false);
        }
    };

    const handleMediaError = () => {
        setError(true);
        setLoading(false);
    };

    const renderMedia = () => {
        if (loading) {
            return (
                <div className="nft-placeholder">
                    <div className="spinner-small"></div>
                </div>
            );
        }

        if (error) {
            return (
                <div className="nft-placeholder error-placeholder">
                    <span>Failed to load</span>
                </div>
            );
        }

        if (!imageUrl) {
            return <div className="nft-placeholder">No Image</div>;
        }

        const url = imageUrl.toLowerCase();

        if (url.endsWith('.glb') || url.endsWith('.gltf')) {
            return (
                <model-viewer
                    src={imageUrl}
                    alt={metadata?.name || `NFT #${nft.token_id}`}
                    auto-rotate
                    camera-controls
                    ar
                    crossorigin="anonymous"
                    shadow-intensity="1"
                    style={{ width: '100%', height: '100%', backgroundColor: '#f5f5f5' }}
                    onError={handleMediaError}
                ></model-viewer>
            );
        } else if (url.endsWith('.mp4') || url.endsWith('.webm') || url.endsWith('.ogg')) {
            return (
                <video
                    src={imageUrl}
                    controls
                    muted
                    loop
                    style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                    onError={handleMediaError}
                    onTimeUpdate={(e) => {
                        if (e.target.currentTime >= 5) {
                            e.target.pause();
                            e.target.currentTime = 0;
                        }
                    }}
                />
            );
        } else if (url.endsWith('.mp3') || url.endsWith('.wav')) {
            return (
                <div className="audio-preview">
                    <div className="audio-icon">🎵</div>
                    <audio
                        src={imageUrl}
                        controls
                        style={{ width: '90%' }}
                        onError={handleMediaError}
                        onTimeUpdate={(e) => {
                            if (e.target.currentTime >= 10) {
                                e.target.pause();
                                e.target.currentTime = 0;
                            }
                        }}
                    />
                </div>
            );
        } else {
            return (
                <img
                    src={imageUrl}
                    alt={metadata?.name || `NFT #${nft.token_id}`}
                    loading="lazy"
                    onError={handleMediaError}
                />
            );
        }
    };

    return (
        <Card hover className="my-nft-card">
            <Link to={`/nft/${nft.token_id}`} className="nft-card-link">
                <div className="nft-image">
                    {renderMedia()}
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
