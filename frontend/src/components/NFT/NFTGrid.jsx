import NFTCard from './NFTCard';
import './NFTGrid.css';

export default function NFTGrid({ nfts, loading }) {
    if (loading) {
        return <div className="spinner"></div>;
    }

    if (!nfts || nfts.length === 0) {
        return (
            <div className="empty-state">
                <p>No NFTs found</p>
            </div>
        );
    }

    return (
        <div className="nft-grid">
            {nfts.map((nft) => (
                <NFTCard key={nft.token_id} nft={nft} />
            ))}
        </div>
    );
}
