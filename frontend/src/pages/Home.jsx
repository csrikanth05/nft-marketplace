import { useState, useEffect } from 'react';
import NFTGrid from '../components/NFT/NFTGrid';
import { getListings } from '../services/api';
import './Home.css';

export default function Home() {
    const [nfts, setNfts] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadNFTs();
    }, []);

    const loadNFTs = async () => {
        try {
            const response = await getListings(true);
            // Transform listings to include price on NFT object
            const nftsWithPrices = response.data.map(listing => ({
                ...listing.nft,
                price_eth: listing.price_eth,
                listing_id: listing.listing_id
            }));
            setNfts(nftsWithPrices);
        } catch (error) {
            console.error('Error loading NFTs:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="home-page">
            <div className="container">
                <div className="hero">
                    <h1>Discover, Collect, and Sell NFTs</h1>
                    <p>Explore the world's premier NFT marketplace</p>
                </div>

                <NFTGrid nfts={nfts} loading={loading} />
            </div>
        </div>
    );
}
