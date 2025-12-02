import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import MyNFTCard from '../components/NFT/MyNFTCard';
import ListNFTModal from '../components/NFT/ListNFTModal';
import CreateCollectionModal from '../components/Collection/CreateCollectionModal';
import CollectionCard from '../components/Collection/CollectionCard';
import Card from '../components/UI/Card';
import './MyNFTs.css';

export default function MyNFTs({ account }) {
    const navigate = useNavigate();
    const [activeTab, setActiveTab] = useState('nfts'); // 'nfts' or 'collections'
    const [nfts, setNfts] = useState([]);
    const [collections, setCollections] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedNFT, setSelectedNFT] = useState(null);
    const [showCreateCollection, setShowCreateCollection] = useState(false);

    useEffect(() => {
        if (account) {
            loadNFTs();
            loadCollections();
        }
    }, [account]);

    const loadNFTs = async () => {
        try {
            const response = await fetch(`http://localhost:8000/api/v1/db/users/${account}/nfts`);
            const data = await response.json();
            setNfts(data);
        } catch (error) {
            console.error('Error loading NFTs:', error);
        } finally {
            setLoading(false);
        }
    };

    const loadCollections = async () => {
        try {
            const response = await fetch(`http://localhost:8000/api/v1/collection/user/${account}`);
            const data = await response.json();
            setCollections(data);
        } catch (error) {
            console.error('Error loading collections:', error);
        }
    };

    const handleListSuccess = () => {
        setSelectedNFT(null);
        loadNFTs();
    };

    const handleCollectionCreated = () => {
        loadCollections();
    };

    if (!account) {
        return (
            <div className="my-nfts-page">
                <div className="container">
                    <h2>Please connect your wallet to view your NFTs</h2>
                </div>
            </div>
        );
    }

    return (
        <div className="my-nfts-page">
            <div className="container">
                <div className="page-header">
                    <h1>My NFTs</h1>
                    <div className="tabs">
                        <button
                            className={`tab ${activeTab === 'nfts' ? 'active' : ''}`}
                            onClick={() => setActiveTab('nfts')}
                        >
                            NFTs ({nfts.length})
                        </button>
                        <button
                            className={`tab ${activeTab === 'collections' ? 'active' : ''}`}
                            onClick={() => setActiveTab('collections')}
                        >
                            Collections ({collections.length})
                        </button>
                    </div>
                </div>

                {loading ? (
                    <div className="spinner"></div>
                ) : (
                    <>
                        {activeTab === 'nfts' && (
                            <div className="nft-grid">
                                {/* Mint NFT Card */}
                                <Card hover className="mint-nft-card" onClick={() => navigate('/create')}>
                                    <div className="mint-icon">✨</div>
                                    <h3>Mint a new NFT</h3>
                                    <p>Create and mint your own NFT</p>
                                    <div className="mint-arrow">→</div>
                                </Card>

                                {/* User's NFTs */}
                                {nfts.map((nft) => (
                                    <MyNFTCard
                                        key={nft.id}
                                        nft={nft}
                                        account={account}
                                        onListClick={() => setSelectedNFT(nft)}
                                    />
                                ))}
                            </div>
                        )}

                        {activeTab === 'collections' && (
                            <div className="collections-section">
                                <div className="collections-header">
                                    <button
                                        className="btn btn-primary"
                                        onClick={() => setShowCreateCollection(true)}
                                    >
                                        + Create Collection
                                    </button>
                                </div>

                                <div className="nft-grid">
                                    {collections.map((collection) => (
                                        <CollectionCard
                                            key={collection.id}
                                            collection={collection}
                                        />
                                    ))}
                                </div>

                                {collections.length === 0 && (
                                    <p className="empty-message">
                                        You haven't created any collections yet. Create one to organize your NFTs!
                                    </p>
                                )}
                            </div>
                        )}

                        {activeTab === 'nfts' && nfts.length === 0 && (
                            <p className="empty-message">You don't own any NFTs yet. Start by minting one!</p>
                        )}
                    </>
                )}
            </div>

            {selectedNFT && (
                <ListNFTModal
                    nft={selectedNFT}
                    account={account}
                    onClose={() => setSelectedNFT(null)}
                    onSuccess={handleListSuccess}
                />
            )}

            {showCreateCollection && (
                <CreateCollectionModal
                    isOpen={showCreateCollection}
                    onClose={() => setShowCreateCollection(false)}
                    account={account}
                    onCollectionCreated={handleCollectionCreated}
                />
            )}
        </div>
    );
}
