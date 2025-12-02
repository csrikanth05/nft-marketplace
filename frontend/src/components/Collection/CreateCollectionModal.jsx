import { useState } from 'react';
import './CreateCollectionModal.css';

export default function CreateCollectionModal({ isOpen, onClose, account, onCollectionCreated }) {
    const [formData, setFormData] = useState({
        name: '',
        description: '',
        category: '',
        banner_image: ''
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const categories = [
        'Art',
        'Photography',
        'Gaming',
        'Music',
        'Sports',
        'Collectibles',
        'Futuristic',
        'Virtual Worlds',
        'Other'
    ];

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            const response = await fetch(
                `http://localhost:8000/api/v1/collection/create?owner_address=${account}`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                }
            );

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to create collection');
            }

            const collection = await response.json();

            // Reset form
            setFormData({
                name: '',
                description: '',
                category: '',
                banner_image: ''
            });

            // Notify parent component
            if (onCollectionCreated) {
                onCollectionCreated(collection);
            }

            onClose();
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content create-collection-modal" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h2>Create Collection</h2>
                    <button className="close-button" onClick={onClose}>×</button>
                </div>

                <form onSubmit={handleSubmit} className="collection-form">
                    <div className="form-group">
                        <label htmlFor="name">Collection Name *</label>
                        <input
                            type="text"
                            id="name"
                            name="name"
                            value={formData.name}
                            onChange={handleChange}
                            placeholder="Enter collection name"
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="description">Description</label>
                        <textarea
                            id="description"
                            name="description"
                            value={formData.description}
                            onChange={handleChange}
                            placeholder="Describe your collection"
                            rows="4"
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="category">Category</label>
                        <select
                            id="category"
                            name="category"
                            value={formData.category}
                            onChange={handleChange}
                        >
                            <option value="">Select a category</option>
                            {categories.map(cat => (
                                <option key={cat} value={cat}>{cat}</option>
                            ))}
                        </select>
                    </div>

                    <div className="form-group">
                        <label htmlFor="banner_image">Banner Image URL</label>
                        <input
                            type="url"
                            id="banner_image"
                            name="banner_image"
                            value={formData.banner_image}
                            onChange={handleChange}
                            placeholder="https://example.com/banner.jpg"
                        />
                        <small className="form-hint">Optional: Provide a URL to a banner image for your collection</small>
                    </div>

                    {error && (
                        <div className="error-message">
                            {error}
                        </div>
                    )}

                    <div className="modal-actions">
                        <button
                            type="button"
                            onClick={onClose}
                            className="btn btn-secondary"
                            disabled={loading}
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            className="btn btn-primary"
                            disabled={loading || !formData.name}
                        >
                            {loading ? 'Creating...' : 'Create Collection'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
