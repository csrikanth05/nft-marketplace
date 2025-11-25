import { useState, useEffect } from 'react';
import MyNFTCard from '../components/NFT/MyNFTCard';
import ListNFTModal from '../components/NFT/ListNFTModal';
import { getUserNFTs } from '../services/api';
import './MyNFTs.css';

export default function MyNFTs({ account }) {
    const [nfts, setNfts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedNFT, setSelectedNFT] = useState(null);

    useEffect(() => {
        if (account) {
            loadMyNFTs();
        } else {
            setLoading(false);
        }
    }, [account]);

    const loadMyNFTs = async () => {
        try {
            const response = await getUserNFTs(account.toLowerCase());
            console.log('My NFTs response:', response.data);
            setNfts(response.data);
        } catch (error) {
            console.error('Error loading NFTs:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleListNFT = (nft) => {
        setSelectedNFT(nft);
    };

    const handleListSuccess = () => {
        // Reload NFTs to get updated listing status
        loadMyNFTs();
    };

    if (!account) {
        return (
            <div className="my-nfts-page">
                <div className="container">
                    <div className="empty-state">
                        <h2>Connect Your Wallet</h2>
                        <p>Please connect your wallet to view your NFTs</p>
                    </div>
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
                ) : nfts.length === 0 ? (
                    <div className="empty-state">
                        <p>You don't have any NFTs yet</p>
                    </div>
                ) : (
                    <div className="my-nfts-grid">
                        {nfts.map((nft) => (
                            <MyNFTCard
                                key={nft.token_id}
                                nft={nft}
                                onList={handleListNFT}
                            />
                        ))}
                    </div>
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
