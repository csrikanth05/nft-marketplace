import { useState } from 'react';
import Card from '../UI/Card';
import Button from '../UI/Button';
import './ListNFTModal.css';

export default function ListNFTModal({ nft, account, onClose, onSuccess }) {
    const [price, setPrice] = useState('');
    const [listing, setListing] = useState(false);

    const handleList = async () => {
        if (!price || parseFloat(price) <= 0) {
            alert('Please enter a valid price');
            return;
        }

        const privateKey = prompt('Enter your private key to list NFT:');
        if (!privateKey) return;

        setListing(true);
        try {
            const NFT_CONTRACT = '0x7D89BCf357cD820A6A88D1ac9266e47f704734Ba';
            const MARKETPLACE_CONTRACT = '0xBF4e7AeB704F2249b48ACec5037A6a43525B13a6';

            // Step 1: Approve marketplace to transfer NFT
            alert('Step 1/2: Approving marketplace to transfer your NFT...');
            const approveResponse = await fetch('http://localhost:8000/api/v1/nfts/approve', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    to_address: MARKETPLACE_CONTRACT,
                    token_id: nft.token_id,
                    from_address: account,
                    private_key: privateKey
                })
            });

            if (!approveResponse.ok) {
                const error = await approveResponse.json();
                throw new Error('Approval failed: ' + (error.detail || 'Unknown error'));
            }

            // Step 2: List NFT on marketplace
            alert('Step 2/2: Listing NFT on marketplace...');
            const response = await fetch('http://localhost:8000/api/v1/marketplace/list', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    nft_contract_address: NFT_CONTRACT,
                    token_id: nft.token_id,
                    price_eth: parseFloat(price),
                    from_address: account,
                    private_key: privateKey
                })
            });

            if (response.ok) {
                alert('✅ NFT listed successfully on marketplace!');
                onSuccess();
                onClose();
            } else {
                const error = await response.json();
                alert('Failed to list NFT: ' + (error.detail || 'Unknown error'));
            }
        } catch (error) {
            console.error('Error listing NFT:', error);
            alert('Failed to list NFT: ' + error.message);
        } finally {
            setListing(false);
        }
    };

    return (
        <div className="modal-overlay">
            <Card className="list-nft-modal">
                <h2>List NFT for Sale</h2>
                <p className="nft-name">{nft.name || `NFT #${nft.token_id}`}</p>

                <div className="form-group">
                    <label>Price (ETH)</label>
                    <input
                        type="number"
                        value={price}
                        onChange={(e) => setPrice(e.target.value)}
                        placeholder="0.00"
                        step="0.01"
                        min="0"
                        autoFocus
                    />
                    <small>Set the price in ETH for your NFT</small>
                </div>

                <div className="modal-actions">
                    <Button variant="ghost" onClick={onClose}>
                        Cancel
                    </Button>
                    <Button onClick={handleList} disabled={listing}>
                        {listing ? 'Listing...' : 'List NFT'}
                    </Button>
                </div>
            </Card>
        </div>
    );
}
