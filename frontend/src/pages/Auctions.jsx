import { useState, useEffect } from 'react';
import NFTGrid from '../components/NFT/NFTGrid';
import { getAuctions } from '../services/api';
import './Auctions.css';

export default function Auctions() {
    const [auctions, setAuctions] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadAuctions();
    }, []);

    const loadAuctions = async () => {
        try {
            const response = await getAuctions(true);
            // Transform auctions to NFT format for display
            const auctionNFTs = response.data.map(auction => ({
                ...auction.nft,
                price_eth: auction.highest_bid_eth || auction.reserve_price_eth,
                auction_id: auction.auction_id,
            }));
            setAuctions(auctionNFTs);
        } catch (error) {
            console.error('Error loading auctions:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auctions-page">
            <div className="container">
                <h1>Active Auctions</h1>
                <NFTGrid nfts={auctions} loading={loading} />
            </div>
        </div>
    );
}
