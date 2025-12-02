import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import MyNFTCard from '../components/NFT/MyNFTCard';
import './CollectionDetail.css';

export default function CollectionDetail({ account }) {
    const { collectionId } = useParams();
    const navigate = useNavigate();
    const [collection, setCollection] = useState(null);
    const [userNFTs, setUserNFTs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showAddNFT, setShowAddNFT] = useState(false);
    const [removing, setRemoving] = useState(null);

    useEffect(() => {
        if (account) {
            loadCollection();
            loadUserNFTs();
        }
    }, [collectionId, account]);

    const loadCollection = async () => {
        try {
            const response = await fetch(`http://localhost:8000/api/v1/collection/${collectionId}`);
            const data = await response.json();
            setCollection(data);
        } catch (error) {
            console.error('Error loading collection:', error);
        } finally {
            setLoading(false);
        }
    };

    const loadUserNFTs = async () => {
        try {
            const response = await fetch(`http://localhost:8000/api/v1/db/users/${account}/nfts`);
            const data = await response.json();
            setUserNFTs(data);
        } catch (error) {
            console.error('Error loading user NFTs:', error);
        }
    };

    const handleAddNFT = async (nftId) => {
        try {
            const response = await fetch(
                `http://localhost:8000/api/v1/collection/${collectionId}/add-nft?owner_address=${account}`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ nft_id: nftId })
                }
            );

            if (!response.ok) {
                const error = await response.json();
                alert(error.detail || 'Failed to add NFT to collection');
                return;
            }

            loadCollection();
            setShowAddNFT(false);
        } catch (error) {
            console.error('Error adding NFT:', error);
            alert('Failed to add NFT to collection');
        }
    };

    const handleRemoveNFT = async (nftId) => {
        if (!confirm('Are you sure you want to remove this NFT from the collection?')) {
            return;
        }

        setRemoving(nftId);
        try {
            const response = await fetch(
                `http://localhost:8000/api/v1/collection/${collectionId}/remove-nft/${nftId}?owner_address=${account}`,
                {
                    method: 'DELETE'
                }
            );

            if (!response.ok) {
                const error = await response.json();
                alert(error.detail || 'Failed to remove NFT from collection');
                return;
            }

            loadCollection();
        } catch (error) {
            console.error('Error removing NFT:', error);
            alert('Failed to remove NFT from collection');
        } finally {
            setRemoving(null);
        }
    };

    if (loading) {
        return (
            <div className="collection-detail-page">
                <div className="container">
                    <div className="spinner"></div>
                </div>
            </div>
        );
    }

    if (!collection) {
        return (
            <div className="collection-detail-page">
                <div className="container">
                    <h2>Collection not found</h2>
                </div>
            </div>
        );
    }

    // Filter out NFTs already in collection
    const availableNFTs = userNFTs.filter(
        nft => !collection.nfts.some(cn => cn.id === nft.id)
    );

    const isOwner = collection.owner_address === account;

    return (
        <div className="collection-detail-page">
            <div className="container">
                <button className="back-button" onClick={() => navigate('/my-nfts')}>
                    ← Back to My NFTs
                </button>

                {collection.banner_image && (
                    <div className="collection-banner-large">
                        <img src={collection.banner_image} alt={collection.name} />
                    </div>
                )}

                <div className="collection-header">
                    <div className="collection-info-header">
                        <h1>{collection.name}</h1>
                        {collection.category && (
                            <span className="category-badge">{collection.category}</span>
                        )}
                    </div>

                    {collection.description && (
                        <p className="collection-description">{collection.description}</p>
                    )}

                    <div className="collection-stats-header">
                        <div className="stat">
                            <span className="stat-value">{collection.nft_count}</span>
                            <span className="stat-label">NFT{collection.nft_count !== 1 ? 's' : ''}</span>
                        </div>
                    </div>

                    {isOwner && (
                        <button
                            className="btn btn-primary"
                            onClick={() => setShowAddNFT(!showAddNFT)}
                        >
                            {showAddNFT ? 'Cancel' : '+ Add NFT'}
                        </button>
                    )}
                </div>

                {showAddNFT && isOwner && (
                    <div className="add-nft-section">
                        <h3>Select NFT to Add</h3>
                        {availableNFTs.length > 0 ? (
                            <div className="nft-grid">
                                {availableNFTs.map(nft => (
                                    <div key={nft.id} className="selectable-nft-card">
                                        <MyNFTCard nft={nft} account={account} />
                                        <button
                                            className="btn btn-primary btn-add"
                                            onClick={() => handleAddNFT(nft.id)}
                                        >
                                            Add to Collection
                                        </button>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <p className="empty-message">All your NFTs are already in this collection!</p>
                        )}
                    </div>
                )}

                <div className="collection-nfts">
                    <h2>NFTs in this Collection</h2>
                    {collection.nfts && collection.nfts.length > 0 ? (
                        <div className="nft-grid">
                            {collection.nfts.map(nft => (
                                <div key={nft.id} className="collection-nft-item">
                                    <MyNFTCard nft={nft} account={account} />
                                    {isOwner && (
                                        <button
                                            className="btn btn-danger btn-remove"
                                            onClick={() => handleRemoveNFT(nft.id)}
                                            disabled={removing === nft.id}
                                        >
                                            {removing === nft.id ? 'Removing...' : 'Remove'}
                                        </button>
                                    )}
                                </div>
                            ))}
                        </div>
                    ) : (
                        <p className="empty-message">This collection is empty. Add some NFTs to get started!</p>
                    )}
                </div>
            </div>
        </div>
    );
}
