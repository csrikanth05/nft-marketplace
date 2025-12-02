import { Link } from 'react-router-dom';
import './CollectionCard.css';

export default function CollectionCard({ collection }) {
    const { id, name, description, category, banner_image, nft_count } = collection;

    return (
        <Link to={`/collection/${id}`} className="collection-card">
            <div className="collection-banner">
                {banner_image ? (
                    <img src={banner_image} alt={name} />
                ) : (
                    <div className="collection-banner-placeholder">
                        <span>📁</span>
                    </div>
                )}
            </div>

            <div className="collection-info">
                <h3 className="collection-name">{name}</h3>

                {category && (
                    <span className="collection-category">{category}</span>
                )}

                {description && (
                    <p className="collection-description">
                        {description.length > 100
                            ? `${description.substring(0, 100)}...`
                            : description
                        }
                    </p>
                )}

                <div className="collection-stats">
                    <div className="stat">
                        <span className="stat-value">{nft_count}</span>
                        <span className="stat-label">NFT{nft_count !== 1 ? 's' : ''}</span>
                    </div>
                </div>
            </div>
        </Link>
    );
}
