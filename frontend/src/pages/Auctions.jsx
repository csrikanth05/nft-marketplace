import { useState, useEffect } from 'react';
import AuctionCard from '../components/Auction/AuctionCard';
import './Auctions.css';

export default function Auctions({ account }) {
    const [activeAuctions, setActiveAuctions] = useState([]);
    const [userAuctions, setUserAuctions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('all'); // 'all' or 'my'

    useEffect(() => {
        loadAuctions();
    }, [account]);

    const loadAuctions = async () => {
        setLoading(true);
        try {
            // Load active auctions
            const activeRes = await fetch('http://localhost:8000/api/v1/auction/active/all');
            const activeData = await activeRes.json();
            setActiveAuctions(activeData);

            // Load user auctions if connected
            if (account) {
                const userRes = await fetch(`http://localhost:8000/api/v1/auction/user/${account}/participated`);
                const userData = await userRes.json();
                setUserAuctions(userData);
            }
        } catch (error) {
            console.error('Error loading auctions:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auctions-page">
            <div className="container">
                <div className="page-header">
                    <h1>Auctions</h1>
                    <div className="tabs">
                        <button
                            className={`tab ${activeTab === 'all' ? 'active' : ''}`}
                            onClick={() => setActiveTab('all')}
                        >
                            Active Auctions
                        </button>
                        {account && (
                            <button
                                className={`tab ${activeTab === 'my' ? 'active' : ''}`}
                                onClick={() => setActiveTab('my')}
                            >
                                My Auctions
                            </button>
                        )}
                    </div>
                </div>

                {loading ? (
                    <div className="spinner-container">
                        <div className="spinner"></div>
                    </div>
                ) : (
                    <div className="auctions-grid">
                        {activeTab === 'all' ? (
                            activeAuctions.length > 0 ? (
                                activeAuctions.map(auction => (
                                    <AuctionCard key={auction.auction_id} auction={auction} />
                                ))
                            ) : (
                                <p className="empty-message">No active auctions at the moment.</p>
                            )
                        ) : (
                            userAuctions.length > 0 ? (
                                userAuctions.map(auction => (
                                    <AuctionCard key={auction.auction_id} auction={auction} />
                                ))
                            ) : (
                                <p className="empty-message">You haven't participated in any auctions yet.</p>
                            )
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
