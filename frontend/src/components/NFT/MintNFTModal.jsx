import { useState } from 'react';
import './MintNFTModal.css';

export default function MintNFTModal({ isOpen, onClose, onMint, loading }) {
    const [privateKey, setPrivateKey] = useState('');
    const [status, setStatus] = useState('input'); // 'input', 'minting', 'success'
    const [error, setError] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setStatus('minting');

        try {
            await onMint(privateKey);
            setStatus('success');

            // Redirect after 1 second
            setTimeout(() => {
                handleClose();
            }, 1000);
        } catch (err) {
            setError(err.message || 'Failed to mint NFT');
            setStatus('input');
        }
    };

    const handleClose = () => {
        setPrivateKey('');
        setStatus('input');
        setError(null);
        onClose();
    };

    if (!isOpen) return null;

    return (
        <div className="modal-overlay" onClick={handleClose}>
            <div className="modal-content mint-modal" onClick={(e) => e.stopPropagation()}>
                {status === 'input' && (
                    <>
                        <div className="modal-header">
                            <h2>🔐 Mint NFT</h2>
                            <button className="close-button" onClick={handleClose}>×</button>
                        </div>

                        <form onSubmit={handleSubmit} className="mint-form">
                            <p className="modal-description">
                                Enter your private key to sign the minting transaction
                            </p>

                            <div className="form-group">
                                <label htmlFor="privateKey">Private Key *</label>
                                <input
                                    type="password"
                                    id="privateKey"
                                    value={privateKey}
                                    onChange={(e) => setPrivateKey(e.target.value)}
                                    placeholder="Enter your private key"
                                    required
                                    autoFocus
                                />
                                <small className="form-hint">
                                    ⚠️ Your private key is never stored and only used to sign this transaction
                                </small>
                            </div>

                            {error && (
                                <div className="error-message">
                                    {error}
                                </div>
                            )}

                            <div className="modal-actions">
                                <button
                                    type="button"
                                    onClick={handleClose}
                                    className="btn btn-secondary"
                                    disabled={loading}
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    className="btn btn-primary"
                                    disabled={!privateKey || loading}
                                >
                                    {loading ? 'Minting...' : 'Mint NFT'}
                                </button>
                            </div>
                        </form>
                    </>
                )}

                {status === 'minting' && (
                    <div className="minting-status">
                        <div className="spinner-large"></div>
                        <h2>Minting NFT...</h2>
                        <p>Please wait while your NFT is being minted on the blockchain</p>
                    </div>
                )}

                {status === 'success' && (
                    <div className="success-status">
                        <div className="success-icon">✅</div>
                        <h2>NFT Minted Successfully!</h2>
                        <p>Redirecting to your NFTs...</p>
                    </div>
                )}
            </div>
        </div>
    );
}
