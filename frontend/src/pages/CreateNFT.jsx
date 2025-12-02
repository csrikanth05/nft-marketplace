import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '../components/UI/Card';
import Button from '../components/UI/Button';
import MintNFTModal from '../components/NFT/MintNFTModal';
import { uploadNFTBundle, mintNFT } from '../services/api';
import './CreateNFT.css';

export default function CreateNFT({ account }) {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        name: '',
        description: '',
        category: '',
        collection: '',
        externalUrl: '',
        royaltyFee: 500,
    });
    const [image, setImage] = useState(null);
    const [preview, setPreview] = useState(null);
    const [properties, setProperties] = useState([{ trait_type: '', value: '' }]);
    const [loading, setLoading] = useState(false);
    const [showMintModal, setShowMintModal] = useState(false);
    const [tokenUri, setTokenUri] = useState(null);

    const handleImageChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            setImage(file);
            setPreview(URL.createObjectURL(file));
        }
    };

    const addProperty = () => {
        setProperties([...properties, { trait_type: '', value: '' }]);
    };

    const removeProperty = (index) => {
        setProperties(properties.filter((_, i) => i !== index));
    };

    const updateProperty = (index, field, value) => {
        const updated = [...properties];
        updated[index][field] = value;
        setProperties(updated);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!account) {
            alert('Please connect your wallet first');
            return;
        }
        if (!image) {
            alert('Please select an image');
            return;
        }

        setLoading(true);
        try {
            // Filter out empty properties
            const validProperties = properties.filter(p => p.trait_type && p.value);

            // Prepare form data for upload
            const uploadFormData = new FormData();
            uploadFormData.append('file', image);
            uploadFormData.append('name', formData.name);
            uploadFormData.append('description', formData.description);
            if (formData.category) uploadFormData.append('category', formData.category);
            if (formData.collection) uploadFormData.append('collection', formData.collection);
            if (formData.externalUrl) uploadFormData.append('external_url', formData.externalUrl);
            if (validProperties.length > 0) {
                uploadFormData.append('attributes', JSON.stringify(validProperties));
            }

            // Upload to IPFS
            const ipfsResponse = await fetch('http://localhost:8000/api/v1/ipfs/upload-nft', {
                method: 'POST',
                body: uploadFormData
            });

            if (!ipfsResponse.ok) {
                throw new Error('Failed to upload to IPFS');
            }

            const ipfsData = await ipfsResponse.json();
            setTokenUri(ipfsData.token_uri);

            // Show mint modal
            setLoading(false);
            setShowMintModal(true);
        } catch (error) {
            console.error('Error uploading NFT:', error);
            alert('Failed to upload NFT: ' + (error.response?.data?.detail || error.message));
            setLoading(false);
        }
    };

    const handleMint = async (privateKey) => {
        await mintNFT({
            to_address: account,
            token_uri: tokenUri,
            royalty_receiver: account,
            royalty_fee: parseInt(formData.royaltyFee),
            from_address: account,
            private_key: privateKey,
        });

        // Navigate will be handled by the modal after showing success
        setTimeout(() => {
            navigate('/my-nfts');
        }, 1000);
    };

    return (
        <div className="create-nft-page">
            <div className="container">
                <div className="create-nft-grid">
                    <Card className="preview-card">
                        <h3>Preview</h3>
                        <div className="image-preview">
                            {preview ? (
                                (() => {
                                    const fileName = image ? image.name.toLowerCase() : '';
                                    if (fileName.endsWith('.glb') || fileName.endsWith('.gltf')) {
                                        return (
                                            <model-viewer
                                                src={preview}
                                                alt="Preview"
                                                auto-rotate
                                                camera-controls
                                                shadow-intensity="1"
                                                style={{ width: '100%', height: '100%', minHeight: '300px' }}
                                            ></model-viewer>
                                        );
                                    } else if (fileName.endsWith('.mp4') || fileName.endsWith('.webm') || fileName.endsWith('.ogg')) {
                                        return (
                                            <video
                                                src={preview}
                                                controls
                                                muted
                                                loop
                                                style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                                                onTimeUpdate={(e) => {
                                                    if (e.target.currentTime >= 5) {
                                                        e.target.pause();
                                                        e.target.currentTime = 0;
                                                    }
                                                }}
                                            />
                                        );
                                    } else if (fileName.endsWith('.mp3') || fileName.endsWith('.wav')) {
                                        return (
                                            <div className="audio-preview-container" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '300px', background: '#f5f5f5' }}>
                                                <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>🎵</div>
                                                <audio
                                                    src={preview}
                                                    controls
                                                    style={{ width: '90%' }}
                                                    onTimeUpdate={(e) => {
                                                        if (e.target.currentTime >= 10) {
                                                            e.target.pause();
                                                            e.target.currentTime = 0;
                                                        }
                                                    }}
                                                />
                                            </div>
                                        );
                                    } else {
                                        return <img src={preview} alt="Preview" />;
                                    }
                                })()
                            ) : (
                                <div className="preview-placeholder">Upload an image to see preview</div>
                            )}
                        </div>
                    </Card>

                    <Card>
                        <form onSubmit={handleSubmit} className="create-nft-form">
                            <div className="form-group">
                                <label>NFT File *</label>
                                <input
                                    type="file"
                                    accept="image/*,video/*,audio/*,.glb,.gltf"
                                    onChange={handleImageChange}
                                    required
                                />
                                <small>Supported: Images, Videos, Audio, 3D Models (GLB/GLTF)</small>
                            </div>

                            <div className="form-group">
                                <label>Name *</label>
                                <input
                                    type="text"
                                    value={formData.name}
                                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                    placeholder="Enter NFT name"
                                    required
                                />
                            </div>

                            <div className="form-group">
                                <label>Description *</label>
                                <textarea
                                    value={formData.description}
                                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                    placeholder="Describe your NFT"
                                    rows="4"
                                    required
                                />
                            </div>

                            <div className="form-row">
                                <div className="form-group">
                                    <label>Category</label>
                                    <select
                                        value={formData.category}
                                        onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                                    >
                                        <option value="">Select category</option>
                                        <option value="Art">Art</option>
                                        <option value="Music">Music</option>
                                        <option value="Photography">Photography</option>
                                        <option value="Gaming">Gaming</option>
                                        <option value="Sports">Sports</option>
                                        <option value="Collectibles">Collectibles</option>
                                        <option value="Futuristic">Futuristic</option>
                                        <option value="Utility">Utility</option>
                                        <option value="Other">Other</option>
                                    </select>
                                </div>

                                <div className="form-group">
                                    <label>Collection</label>
                                    <input
                                        type="text"
                                        value={formData.collection}
                                        onChange={(e) => setFormData({ ...formData, collection: e.target.value })}
                                        placeholder="Collection name (optional)"
                                    />
                                </div>
                            </div>

                            <div className="form-group">
                                <label>External Link</label>
                                <input
                                    type="url"
                                    value={formData.externalUrl}
                                    onChange={(e) => setFormData({ ...formData, externalUrl: e.target.value })}
                                    placeholder="https://yourwebsite.com (optional)"
                                />
                                <small>Link to your website or social media</small>
                            </div>

                            <div className="form-group">
                                <label>Properties</label>
                                <small>Add custom attributes to your NFT</small>
                                {properties.map((prop, index) => (
                                    <div key={index} className="property-row">
                                        <input
                                            type="text"
                                            value={prop.trait_type}
                                            onChange={(e) => updateProperty(index, 'trait_type', e.target.value)}
                                            placeholder="Property name (e.g., Color)"
                                        />
                                        <input
                                            type="text"
                                            value={prop.value}
                                            onChange={(e) => updateProperty(index, 'value', e.target.value)}
                                            placeholder="Value (e.g., Blue)"
                                        />
                                        {properties.length > 1 && (
                                            <button
                                                type="button"
                                                onClick={() => removeProperty(index)}
                                                className="remove-btn"
                                            >
                                                ×
                                            </button>
                                        )}
                                    </div>
                                ))}
                                <button type="button" onClick={addProperty} className="add-property-btn">
                                    + Add Property
                                </button>
                            </div>

                            <div className="form-group">
                                <label>Royalty Fee (basis points)</label>
                                <input
                                    type="number"
                                    value={formData.royaltyFee}
                                    onChange={(e) => setFormData({ ...formData, royaltyFee: e.target.value })}
                                    placeholder="500 = 5%"
                                    min="0"
                                    max="10000"
                                />
                                <small>500 = 5%, 1000 = 10%</small>
                            </div>

                            <Button type="submit" disabled={loading} size="md">
                                {loading ? 'Creating...' : 'Create NFT'}
                            </Button>
                        </form>
                    </Card>
                </div>
            </div>

            <MintNFTModal
                isOpen={showMintModal}
                onClose={() => setShowMintModal(false)}
                onMint={handleMint}
                loading={loading}
            />
        </div>
    );
}
