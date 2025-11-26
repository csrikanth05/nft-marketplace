import { useState, useEffect } from 'react';
import Card from '../UI/Card';
import Button from '../UI/Button';
import './BuyNFTModal.css';

export default function BuyNFTModal({ nft, listing, account, onClose, onSuccess }) {
    const [buying, setBuying] = useState(false);
    const [privateKey, setPrivateKey] = useState('');
    const [status, setStatus] = useState('');
    const [showPrivateKey, setShowPrivateKey] = useState(false);
    const [gasFee, setGasFee] = useState(null);
    const [loadingGas, setLoadingGas] = useState(true);

    useEffect(() => {
        let mounted = true;
        const fetchGasEstimate = async () => {
            if (!listing || !account) return;
            try {
                const response = await fetch(`http://localhost:8000/api/v1/marketplace/estimate-gas/buy/${listing.listing_id}?from_address=${account}`);
                if (response.ok) {
                    const data = await response.json();
                    if (mounted) setGasFee(data.gas_fee_eth);
                }
            } catch (error) {
                console.error("Failed to estimate gas:", error);
            } finally {
                if (mounted) setLoadingGas(false);
            }
        };

        fetchGasEstimate();
        return () => { mounted = false; };
    }, [listing, account]);

    const handlePurchaseClick = () => {
        setShowPrivateKey(true);
    };

    const handleConfirmBuy = async () => {
        if (!account) {
            alert('Please connect your wallet');
            return;
        }

        if (!privateKey) {
            alert('Please enter your private key');
            return;
        }

        setBuying(true);
        setStatus('Initiating transaction...');

        try {
            setStatus('Processing purchase on blockchain...');
            const response = await fetch(`http://localhost:8000/api/v1/marketplace/buy/${listing.listing_id}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    from_address: account,
                    private_key: privateKey
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to buy NFT');
            }

            setStatus('Transaction successful! Updating ownership...');
            const data = await response.json();

            // Short delay to let user see success message
            setTimeout(() => {
                alert(`NFT purchased successfully! Transaction: ${data.transaction_hash}`);
                onSuccess();
            }, 500);

        } catch (error) {
            console.error('Error buying NFT:', error);
            alert('Failed to buy NFT: ' + error.message);
            setBuying(false);
            setStatus('');
        }
    };

    const totalPrice = listing?.price_eth && gasFee ? (parseFloat(listing.price_eth) + parseFloat(gasFee)).toFixed(6) : '...';

    return (
        <div className="modal-overlay" onClick={onClose}>
            <Card className="buy-nft-modal" onClick={(e) => e.stopPropagation()}>
                <h2>Purchase NFT</h2>

                <div className="nft-summary">
                    <div className="nft-image-small">
                        {nft?.image_url ? (
                            <img src={nft.image_url} alt={nft.name || 'NFT'} />
                        ) : (
                            <div className="placeholder">No Image</div>
                        )}
                    </div>
                    <div className="nft-info">
                        <h3>{nft?.name || 'Unknown NFT'}</h3>
                        <p className="token-id">Token ID: {nft?.token_id || '-'}</p>
                    </div>
                </div>

                <div className="price-breakdown">
                    <div className="price-row">
                        <span>Price</span>
                        <span className="price-value">{listing?.price_eth || 0} ETH</span>
                    </div>
                    <div className="price-row">
                        <span>Gas Fee (Est.)</span>
                        <span className="price-value">
                            {loadingGas ? 'Calculating...' : `${gasFee ? parseFloat(gasFee).toFixed(6) : '0'} ETH`}
                        </span>
                    </div>
                    <div className="divider"></div>
                    <div className="price-row total">
                        <span>Total</span>
                        <span className="price-value">{totalPrice} ETH</span>
                    </div>
                </div>

                {showPrivateKey && (
                    <div className="private-key-section">
                        <label htmlFor="private-key">Private Key (for signing)</label>
                        <input
                            id="private-key"
                            type="password"
                            value={privateKey}
                            onChange={(e) => setPrivateKey(e.target.value)}
                            placeholder="Enter your private key"
                            disabled={buying}
                            className="private-key-input"
                            autoFocus
                        />
                        <small>Your key is sent directly to the backend for signing and is not stored.</small>
                    </div>
                )}

                <p className="warning-text">
                    ⚠️ This transaction will transfer approx. {totalPrice} ETH from your wallet.
                </p>

                {status && <div className="status-message">{status}</div>}

                <div className="modal-actions">
                    <Button variant="ghost" onClick={onClose} disabled={buying} size="sm">
                        Cancel
                    </Button>
                    {!showPrivateKey ? (
                        <Button onClick={handlePurchaseClick} disabled={loadingGas} size="sm">
                            Purchase
                        </Button>
                    ) : (
                        <Button onClick={handleConfirmBuy} disabled={buying || loadingGas} size="sm">
                            {buying ? <span className="spinner-small"></span> : 'Confirm Purchase'}
                        </Button>
                    )}
                </div>
            </Card>
        </div>
    );
}
