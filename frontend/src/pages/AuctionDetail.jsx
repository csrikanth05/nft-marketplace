import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import Button from '../components/UI/Button';
import DisplayName from '../components/UI/DisplayName';
import './AuctionDetail.css';

const IPFS_GATEWAY = 'https://ipfs.io/ipfs/';

export default function AuctionDetail({ account }) {
    const { id } = useParams();
    const navigate = useNavigate();
    const [auction, setAuction] = useState(null);
    const [nftData, setNftData] = useState(null);
    const [metadata, setMetadata] = useState(null);
    const [imageUrl, setImageUrl] = useState(null);
    const [loading, setLoading] = useState(true);
    const [bidAmount, setBidAmount] = useState('');
    const [privateKey, setPrivateKey] = useState('');
    const [actionLoading, setActionLoading] = useState(false);
    const [error, setError] = useState(null);
    const [status, setStatus] = useState('');
    const [timeLeft, setTimeLeft] = useState('');
    const [showCancelModal, setShowCancelModal] = useState(false);
    const [cancelPrivateKey, setCancelPrivateKey] = useState('');

    useEffect(() => {
        loadAuction();
    }, [id]);

    useEffect(() => {
        if (auction) {
            const timer = setInterval(() => {
                const now = Math.floor(Date.now() / 1000);
                const diff = auction.end_time - now;

                if (diff <= 0) {
                    setTimeLeft('Ended');
                    clearInterval(timer);
                } else {
                    const days = Math.floor(diff / 86400);
                    const hours = Math.floor((diff % 86400) / 3600);
                    const minutes = Math.floor((diff % 3600) / 60);
                    const seconds = diff % 60;

                    if (days > 0) {
                        setTimeLeft(`${days}d ${hours}h ${minutes}m`);
                    } else {
                        setTimeLeft(`${hours}h ${minutes}m ${seconds}s`);
                    }
                }
            }, 1000);
            return () => clearInterval(timer);
        }
    }, [auction]);

    const loadAuction = async () => {
        try {
            const response = await fetch(`http://localhost:8000/api/v1/auction/${id}`);
            if (!response.ok) throw new Error('Auction not found');
            const data = await response.json();
            setAuction(data);

            // Fetch NFT data from database
            try {
                const nftResponse = await fetch(`http://localhost:8000/api/v1/db/nfts/${data.token_id}`);
                const nft = await nftResponse.json();
                setNftData(nft);

                // Fetch metadata from IPFS
                if (nft.token_uri) {
                    const metadataUrl = nft.token_uri.replace('ipfs://', IPFS_GATEWAY);
                    const metadataResponse = await fetch(metadataUrl);
                    const metadataData = await metadataResponse.json();
                    setMetadata(metadataData);

                    // Get image URL
                    if (metadataData.image) {
                        const imgUrl = metadataData.image.replace('ipfs://', IPFS_GATEWAY);
                        setImageUrl(imgUrl);
                    }
                }
            } catch (err) {
                console.error('Error loading NFT metadata:', err);
            }
        } catch (err) {
            console.error(err);
            setError('Failed to load auction');
        } finally {
            setLoading(false);
        }
    };

    const handleBid = async (e) => {
        e.preventDefault();
        setActionLoading(true);
        setError(null);
        setStatus('Placing bid...');

        try {
            const response = await fetch(`http://localhost:8000/api/v1/auction/${id}/bid`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    bid_amount_eth: parseFloat(bidAmount),
                    from_address: account,
                    private_key: privateKey
                })
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || 'Failed to place bid');
            }

            setStatus('Bid placed successfully!');
            setBidAmount('');
            setPrivateKey('');
            loadAuction(); // Refresh data
        } catch (err) {
            setError(err.message);
            setStatus('');
        } finally {
            setActionLoading(false);
        }
    };

    const handleEndAuction = async () => {
        setActionLoading(true);
        setError(null);
        setStatus('Ending auction...');

        try {
            const response = await fetch(`http://localhost:8000/api/v1/auction/${id}/end`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    from_address: account,
                    private_key: privateKey
                })
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || 'Failed to end auction');
            }

            setStatus('Auction ended successfully! NFT transferred.');
            loadAuction();
        } catch (err) {
            setError(err.message);
            setStatus('');
        } finally {
            setActionLoading(false);
        }
    };

    const handleWithdrawBid = async () => {
        setActionLoading(true);
        setError(null);
        setStatus('Withdrawing bid...');

        try {
            const response = await fetch(`http://localhost:8000/api/v1/auction/${id}/withdraw`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    from_address: account,
                    private_key: privateKey
                })
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || 'Failed to withdraw bid');
            }

            setStatus('Bid withdrawn successfully!');
            setPrivateKey('');
            loadAuction();
        } catch (err) {
            setError(err.message);
            setStatus('');
        } finally {
            setActionLoading(false);
        }
    };

    const handleCancelAuction = async () => {
        if (!window.confirm('Are you sure you want to cancel this auction?')) {
            return;
        }

        setActionLoading(true);
        setError(null);
        setStatus('Cancelling auction...');

        try {
            const response = await fetch(`http://localhost:8000/api/v1/auction/${id}`, {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    from_address: account,
                    private_key: privateKey
                })
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || 'Failed to cancel auction');
            }

            setStatus('Auction cancelled successfully!');
            setTimeout(() => navigate('/auctions'), 2000);
        } catch (err) {
            setError(err.message);
            setStatus('');
        } finally {
            setActionLoading(false);
        }
    };

    if (loading) return <div className="spinner-container"><div className="spinner"></div></div>;
    if (!auction) return <div className="container error">Auction not found</div>;

    const isOwner = account && auction.seller.toLowerCase() === account.toLowerCase();
    const isHighestBidder = account && auction.highest_bidder.toLowerCase() === account.toLowerCase();
    const now = Math.floor(Date.now() / 1000);
    // Add a 60-second buffer to account for blockchain time differences
    const isEnded = auction.ended || (now >= auction.end_time + 60) || timeLeft === 'Ended';
    const currentPrice = auction.highest_bid_eth > 0 ? auction.highest_bid_eth : auction.reserve_price_eth;
    const minBid = auction.highest_bid_eth > 0 ? auction.highest_bid_eth * 1.05 : auction.reserve_price_eth;

    return (
        <div className="auction-detail-page">
            <div className="container">
                <h1 className="auction-title">
                    <Link to={`/nft/${auction.token_id}`} className="auction-title-link">
                        {metadata?.name || `NFT #${auction.token_id}`}
                    </Link>
                </h1>

                <div className="auction-layout">
                    <div className="auction-media">
                        {imageUrl ? (
                            <img src={imageUrl} alt={metadata?.name || `NFT #${auction.token_id}`} />
                        ) : (
                            <div className="nft-placeholder-large">
                                <span>NFT #{auction.token_id}</span>
                            </div>
                        )}
                    </div>

                    <div className="auction-content">
                        <div className="auction-status-card">
                            <div className="status-header">
                                <span className="label">{isEnded ? 'Auction Ended' : 'Auction Ends In'}</span>
                                <span className="timer">{timeLeft}</span>
                            </div>

                            <div className="current-bid">
                                <span className="label">Current Price</span>
                                <span className="price">{currentPrice} ETH</span>
                                {auction.highest_bidder !== '0x0000000000000000000000000000000000000000' && (
                                    <span className="bidder">
                                        by <DisplayName address={auction.highest_bidder} />
                                    </span>
                                )}
                            </div>

                            {!isEnded && account && !isOwner && (
                                <>
                                    <div className="info-message">
                                        💡 Your bid will be held in the smart contract. If outbid, you can withdraw your funds.
                                    </div>
                                    <form onSubmit={handleBid} className="bid-form">
                                        <div className="form-field">
                                            <label>Enter Bid (Min: {minBid.toFixed(4)} ETH)</label>
                                            <div className="input-group">
                                                <input
                                                    type="number"
                                                    step="0.0001"
                                                    min={minBid}
                                                    value={bidAmount}
                                                    onChange={(e) => setBidAmount(e.target.value)}
                                                    required
                                                    className="bid-input"
                                                />
                                                <span className="unit">ETH</span>
                                            </div>
                                        </div>

                                        <div className="form-field">
                                            <label>Private Key</label>
                                            <input
                                                type="password"
                                                placeholder="Enter your private key"
                                                value={privateKey}
                                                onChange={(e) => setPrivateKey(e.target.value)}
                                                required
                                                className="private-key-input"
                                            />
                                        </div>

                                        <Button type="submit" variant="primary" disabled={actionLoading} fullWidth>
                                            {actionLoading ? 'Processing...' : 'Place Bid'}
                                        </Button>
                                    </form>
                                </>
                            )}



                            {isEnded && (
                                <div className="auction-ended-actions">
                                    {isHighestBidder && !auction.ended && (
                                        <div className="winner-section">
                                            <p>🎉 You won this auction!</p>
                                            {now < auction.end_time && (
                                                <p className="info-message">⏳ Please wait a moment for the blockchain to confirm the auction has ended before finalizing.</p>
                                            )}
                                            <div className="form-field">
                                                <label>Private Key</label>
                                                <input
                                                    type="password"
                                                    placeholder="Private Key to Claim"
                                                    value={privateKey}
                                                    onChange={(e) => setPrivateKey(e.target.value)}
                                                    className="private-key-input"
                                                />
                                            </div>
                                            <Button onClick={handleEndAuction} variant="success" disabled={actionLoading}>
                                                {actionLoading ? 'Processing...' : 'Complete Purchase'}
                                            </Button>
                                        </div>
                                    )}
                                    {isOwner && !auction.ended && (
                                        <div className="owner-section">
                                            <p>Auction ended. Finalize to transfer NFT and receive funds.</p>
                                            {now < auction.end_time && (
                                                <p className="info-message">⏳ Please wait a moment for the blockchain to confirm the auction has ended before finalizing.</p>
                                            )}
                                            <div className="form-field">
                                                <label>Private Key</label>
                                                <input
                                                    type="password"
                                                    placeholder="Private Key"
                                                    value={privateKey}
                                                    onChange={(e) => setPrivateKey(e.target.value)}
                                                    className="private-key-input"
                                                />
                                            </div>
                                            <Button onClick={handleEndAuction} variant="primary" disabled={actionLoading}>
                                                Finalize Auction
                                            </Button>
                                        </div>
                                    )}
                                    {auction.ended && (
                                        <p className="completed-text">This auction has been finalized.</p>
                                    )}
                                </div>
                            )}

                            {error && <div className="error-message">{error}</div>}
                            {status && <div className="status-message">{status}</div>}
                        </div>

                        <div className="auction-details">
                            <h3>Details</h3>
                            <div className="detail-row">
                                <span>Created By</span>
                                <DisplayName address={auction.seller} />
                            </div>
                            <div className="detail-row">
                                <span>Owned By</span>
                                <DisplayName address={nftData?.owner_address || auction.seller} />
                            </div>
                            <div className="detail-row">
                                <span>Contract</span>
                                <span className="address">{auction.nft_contract}</span>
                            </div>
                            <div className="detail-row">
                                <span>Token ID</span>
                                <span>{auction.token_id}</span>
                            </div>
                        </div>

                        {!isEnded && isOwner && (
                            <Button onClick={() => setShowCancelModal(true)} variant="secondary" fullWidth>
                                Cancel Auction
                            </Button>
                        )}
                    </div>
                </div>

                {showCancelModal && (
                    <div className="modal-overlay" onClick={() => setShowCancelModal(false)}>
                        <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                            <h2>Cancel Auction</h2>
                            <p>Enter your private key to cancel this auction.</p>
                            <div className="form-field">
                                <label>Private Key</label>
                                <input
                                    type="password"
                                    placeholder="Enter your private key"
                                    value={cancelPrivateKey}
                                    onChange={(e) => setCancelPrivateKey(e.target.value)}
                                    className="private-key-input"
                                />
                            </div>
                            {error && <div className="error-message">{error}</div>}
                            {status && <div className="status-message">{status}</div>}
                            <div className="modal-actions">
                                <Button onClick={() => setShowCancelModal(false)} variant="secondary">
                                    Close
                                </Button>
                                <Button
                                    onClick={async () => {
                                        if (!cancelPrivateKey) {
                                            setError('Please enter your private key');
                                            return;
                                        }
                                        setActionLoading(true);
                                        setError(null);
                                        setStatus('Cancelling auction...');
                                        try {
                                            const response = await fetch(`http://localhost:8000/api/v1/auction/${id}`, {
                                                method: 'DELETE',
                                                headers: { 'Content-Type': 'application/json' },
                                                body: JSON.stringify({
                                                    from_address: account,
                                                    private_key: cancelPrivateKey
                                                })
                                            });
                                            if (!response.ok) {
                                                const data = await response.json();
                                                throw new Error(data.detail || 'Failed to cancel auction');
                                            }
                                            setStatus('Auction cancelled successfully!');
                                            setTimeout(() => navigate('/auctions'), 2000);
                                        } catch (err) {
                                            setError(err.message);
                                            setStatus('');
                                        } finally {
                                            setActionLoading(false);
                                        }
                                    }}
                                    variant="primary"
                                    disabled={actionLoading || !cancelPrivateKey}
                                >
                                    {actionLoading ? 'Processing...' : 'Confirm Cancel'}
                                </Button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
