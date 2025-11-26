import { useState } from 'react';
import Button from '../UI/Button';
import './CreateAuctionModal.css';

export default function CreateAuctionModal({ nft, account, onClose, onSuccess }) {
    const [formData, setFormData] = useState({
        startPrice: '',
        duration: '86400', // Default 24 hours
        privateKey: ''
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [status, setStatus] = useState('');

    const DURATION_OPTIONS = [
        { label: '1 Hour', value: '3600' },
        { label: '6 Hours', value: '21600' },
        { label: '12 Hours', value: '43200' },
        { label: '24 Hours', value: '86400' },
        { label: '3 Days', value: '259200' },
        { label: '1 Week', value: '604800' },
        { label: '2 Weeks', value: '1209600' }
    ];

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setStatus('Creating auction...');

        try {
            // Get current blockchain time
            const timeResponse = await fetch('http://localhost:8000/api/v1/auction/blockchain-time');
            const { timestamp: blockchainTime } = await timeResponse.json();

            // Set start time to blockchain time + 3 seconds
            const startTime = blockchainTime + 3;
            const endTime = startTime + parseInt(formData.duration);

            const response = await fetch('http://localhost:8000/api/v1/auction/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    nft_contract_address: nft.contract_address,
                    token_id: nft.token_id,
                    start_time: startTime,
                    end_time: endTime,
                    reserve_price_eth: parseFloat(formData.startPrice),
                    from_address: account,
                    private_key: formData.privateKey
                })
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || 'Failed to create auction');
            }

            setStatus('Auction created successfully!');
            setTimeout(() => {
                onSuccess();
                onClose();
            }, 1500);
        } catch (err) {
            console.error('Auction creation error:', err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="modal-overlay">
            <div className="create-auction-modal">
                <div className="modal-header">
                    <h2>Create Auction</h2>
                    <button className="close-button" onClick={onClose}>&times;</button>
                </div>

                <div className="nft-preview">
                    <div className="preview-info">
                        <h3>{nft.name || `NFT #${nft.token_id}`}</h3>
                        <span className="token-id">Token ID: {nft.token_id}</span>
                    </div>
                </div>

                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label>Reserve Price (ETH)</label>
                        <input
                            type="number"
                            step="0.0001"
                            min="0"
                            required
                            value={formData.startPrice}
                            onChange={(e) => setFormData({ ...formData, startPrice: e.target.value })}
                            placeholder="0.00"
                        />
                        <small>Minimum bid to start the auction</small>
                    </div>

                    <div className="form-group">
                        <label>Duration</label>
                        <select
                            value={formData.duration}
                            onChange={(e) => setFormData({ ...formData, duration: e.target.value })}
                        >
                            {DURATION_OPTIONS.map(opt => (
                                <option key={opt.value} value={opt.value}>
                                    {opt.label}
                                </option>
                            ))}
                        </select>
                    </div>

                    <div className="form-group">
                        <label>Private Key</label>
                        <input
                            type="password"
                            required
                            value={formData.privateKey}
                            onChange={(e) => setFormData({ ...formData, privateKey: e.target.value })}
                            placeholder="Enter your private key to sign transaction"
                            className="private-key-input"
                        />
                        <small className="warning-text">
                            Never share your private key. Used locally for signing only.
                        </small>
                    </div>

                    {error && <div className="error-message">{error}</div>}
                    {status && <div className="status-message">{status}</div>}

                    <div className="modal-actions">
                        <Button variant="secondary" onClick={onClose} disabled={loading}>
                            Cancel
                        </Button>
                        <Button type="submit" variant="primary" disabled={loading}>
                            {loading ? (
                                <>
                                    <span className="spinner-small"></span>
                                    Creating...
                                </>
                            ) : 'Start Auction'}
                        </Button>
                    </div>
                </form>
            </div>
        </div>
    );
}
