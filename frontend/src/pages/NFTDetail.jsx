import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useProfile } from '../context/ProfileContext';
import Card from '../components/UI/Card';
import Button from '../components/UI/Button';
import DisplayName from '../components/UI/DisplayName';
import ListNFTModal from '../components/NFT/ListNFTModal';
import './NFTDetail.css';

const IPFS_GATEWAY = 'https://ipfs.io/ipfs/';

export default function NFTDetail({ account }) {
    const { tokenId } = useParams();
    const navigate = useNavigate();
    const { getDisplayName } = useProfile();

    const [nft, setNft] = useState(null);
    const [metadata, setMetadata] = useState(null);
    const [imageUrl, setImageUrl] = useState(null);
    const [loading, setLoading] = useState(true);
    const [showListModal, setShowListModal] = useState(false);
    const [creationDate, setCreationDate] = useState(null);

    useEffect(() => {
        loadNFTDetails();
    }, [tokenId]);

    const loadNFTDetails = async () => {
        try {
            // Fetch NFT from database
            const response = await fetch(`http://localhost:8000/api/v1/db/nfts/${tokenId}`);
            const nftData = await response.json();
            setNft(nftData);

            // Set creation date if available
            if (nftData.created_at) {
                setCreationDate(new Date(nftData.created_at));
            }

            // If NFT is listed, fetch the listing details to get the price
            if (nftData.is_listed) {
                try {
                    const listingsResponse = await fetch('http://localhost:8000/api/v1/db/listings?active_only=true');
                    const listings = await listingsResponse.json();
                    const listing = listings.find(l => l.nft && l.nft.token_id === parseInt(tokenId));
                    if (listing) {
                        // Add listing data to NFT
                        setNft(prev => ({
                            ...prev,
                            price_eth: listing.price_eth,
                            listing_id: listing.listing_id
                        }));
                    }
                } catch (err) {
                    console.error('Error fetching listing:', err);
                }
            }

            // Fetch metadata from IPFS
            if (nftData.token_uri) {
                const metadataUrl = nftData.token_uri.replace('ipfs://', IPFS_GATEWAY);
                const metadataResponse = await fetch(metadataUrl);
                const metadataData = await metadataResponse.json();
                setMetadata(metadataData);

                // Get image URL
                if (metadataData.image) {
                    const imgUrl = metadataData.image.replace('ipfs://', IPFS_GATEWAY);
                    setImageUrl(imgUrl);
                }
            }
        } catch (error) {
            console.error('Error loading NFT details:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleBuyNFT = async () => {
        if (!account) {
            alert('Please connect your wallet to buy NFTs');
            return;
        }

        const privateKey = prompt('Enter your private key to buy NFT:');
        if (!privateKey) return;

        try {
            const response = await fetch(`http://localhost:8000/api/v1/marketplace/buy/${nft.listing_id}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    from_address: account,
                    private_key: privateKey
                })
            });

            if (response.ok) {
                alert('NFT purchased successfully!');
                navigate('/my-nfts');
            } else {
                const error = await response.json();
                alert('Failed to buy NFT: ' + (error.detail || 'Unknown error'));
            }
        } catch (error) {
            console.error('Error buying NFT:', error);
            alert('Failed to buy NFT: ' + error.message);
        }
    };

    const formatDate = (date) => {
        if (!date) return 'Unknown';
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    };

    if (loading) {
        return (
            <div className="nft-detail-page">
                <div className="container">
                    <div className="spinner"></div>
                </div>
            </div>
        );
    }

    if (!nft) {
        return (
            <div className="nft-detail-page">
                <div className="container">
                    <h2>NFT Not Found</h2>
                    <Button onClick={() => navigate('/')}>Back to Marketplace</Button>
                </div>
            </div>
        );
    }

    const isOwner = account && nft.owner_address.toLowerCase() === account.toLowerCase();

    return (
        <div className="nft-detail-page">
            <div className="container">
                <button className="back-button" onClick={() => navigate(-1)}>
                    ← Back
                </button>

                <div className="nft-detail-grid">
                    {/* Left: Image */}
                    <div className="nft-image-section">
                        <Card className="nft-image-card">
                            {imageUrl ? (
                                <img src={imageUrl} alt={metadata?.name || `NFT #${tokenId}`} />
                            ) : (
                                <div className="image-placeholder">No Image</div>
                            )}
                        </Card>

                        <div className="nft-links">
                            {nft.token_uri && (
                                <a
                                    href={nft.token_uri.replace('ipfs://', IPFS_GATEWAY)}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="ipfs-link"
                                >
                                    View Metadata on IPFS →
                                </a>
                            )}
                        </div>
                    </div>

                    {/* Right: Details */}
                    <div className="nft-info-section">
                        {/* Header with Name and List Button */}
                        <div className="nft-header">
                            <div className="header-left">
                                {metadata?.collection && (
                                    <span className="collection-name">{metadata.collection}</span>
                                )}
                                <h1>{metadata?.name || `NFT #${tokenId}`}</h1>
                            </div>
                            {isOwner && !nft.is_listed && (
                                <Button onClick={() => setShowListModal(true)}>
                                    List for Sale
                                </Button>
                            )}
                        </div>

                        {/* Ownership */}
                        <Card className="ownership-card">
                            <div className="ownership-info">
                                <div className="owner-item">
                                    <span className="label">Owned by</span>
                                    <span className="value" title={nft.owner_address}>
                                        <DisplayName address={nft.owner_address} />
                                    </span>
                                </div>
                                <div className="owner-item">
                                    <span className="label">Created by</span>
                                    <span className="value" title={nft.creator_address}>
                                        <DisplayName address={nft.creator_address} />
                                    </span>
                                </div>
                            </div>
                        </Card>

                        {/* Price & Actions */}
                        {nft.is_listed && (
                            <Card className="price-card">
                                <div className="current-price">
                                    <span className="price-label">Current Price</span>
                                    <span className="price-value-small">{nft.price_eth} ETH</span>
                                </div>
                                {!isOwner && (
                                    <Button size="lg" onClick={handleBuyNFT}>
                                        Buy Now
                                    </Button>
                                )}
                                {isOwner && (
                                    <div className="owner-notice">
                                        You own this NFT (Listed for sale)
                                    </div>
                                )}
                            </Card>
                        )}

                        {/* Description */}
                        <Card className="description-card">
                            <h3>Description</h3>
                            <p>{metadata?.description || '-'}</p>
                        </Card>

                        {/* Properties */}
                        {metadata?.attributes && metadata.attributes.length > 0 && (
                            <Card className="properties-card">
                                <h3>Properties</h3>
                                <div className="properties-grid">
                                    {metadata.attributes.map((attr, index) => (
                                        <div key={index} className="property-item">
                                            <span className="property-type">{attr.trait_type || 'Property'}</span>
                                            <span className="property-value">{attr.value || '-'}</span>
                                        </div>
                                    ))}
                                </div>
                            </Card>
                        )}

                        {/* Details */}
                        <Card className="details-card">
                            <h3>Details</h3>
                            <div className="detail-item">
                                <span className="detail-label">Contract Address</span>
                                <span className="detail-value">0x7D89...4Ba</span>
                            </div>
                            <div className="detail-item">
                                <span className="detail-label">Token ID</span>
                                <span className="detail-value">{tokenId}</span>
                            </div>
                            <div className="detail-item">
                                <span className="detail-label">Token Standard</span>
                                <span className="detail-value">ERC-721</span>
                            </div>
                            <div className="detail-item">
                                <span className="detail-label">Blockchain</span>
                                <span className="detail-value">Ethereum (Ganache)</span>
                            </div>
                            <div className="detail-item">
                                <span className="detail-label">Category</span>
                                <span className="detail-value">{metadata?.category || '-'}</span>
                            </div>
                            <div className="detail-item">
                                <span className="detail-label">Collection</span>
                                <span className="detail-value">{metadata?.collection || '-'}</span>
                            </div>
                            <div className="detail-item">
                                <span className="detail-label">Royalty Fee</span>
                                <span className="detail-value">{nft.royalty_fee ? `${nft.royalty_fee / 100}%` : '-'}</span>
                            </div>
                            {metadata?.external_url ? (
                                <div className="detail-item">
                                    <span className="detail-label">External Link</span>
                                    <a
                                        href={metadata.external_url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="detail-link"
                                    >
                                        Visit →
                                    </a>
                                </div>
                            ) : (
                                <div className="detail-item">
                                    <span className="detail-label">External Link</span>
                                    <span className="detail-value">-</span>
                                </div>
                            )}
                        </Card>
                    </div>
                </div>
            </div>

            {showListModal && (
                <ListNFTModal
                    nft={{ ...nft, token_id: parseInt(tokenId), name: metadata?.name }}
                    account={account}
                    onClose={() => setShowListModal(false)}
                    onSuccess={() => {
                        setShowListModal(false);
                        loadNFTDetails();
                    }}
                />
            )}
        </div>
    );
}
