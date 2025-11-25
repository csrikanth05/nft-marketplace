import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import MyNFTCard from '../components/NFT/MyNFTCard';
import ListNFTModal from '../components/NFT/ListNFTModal';
import Card from '../components/UI/Card';
import './MyNFTs.css';

export default function MyNFTs({ account }) {
    const navigate = useNavigate();
    const [nfts, setNfts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedNFT, setSelectedNFT] = useState(null);

    useEffect(() => {
        if (account) {
            loadNFTs();
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

    const handleListSuccess = () => {
        setSelectedNFT(null);
        loadNFTs();
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
                <h1>My NFTs</h1>

                {loading ? (
                    <div className="spinner"></div>
                ) : (
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

                {nfts.length === 0 && !loading && (
                    <p className="empty-message">You don't own any NFTs yet. Start by minting one!</p>
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
        </div>
    );
}
