import { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Button from '../UI/Button';
import DisplayName from '../UI/DisplayName';
import { useProfile } from '../../context/ProfileContext';
import './Header.css';

export default function Header({ account, connectWallet, disconnectWallet }) {
    const { profile } = useProfile();
    const [showDropdown, setShowDropdown] = useState(false);
    const dropdownRef = useRef(null);

    // Close dropdown when clicking outside
    useEffect(() => {
        const handleClickOutside = (event) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setShowDropdown(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const handleDisconnect = () => {
        setShowDropdown(false);
        disconnectWallet();
    };

    return (
        <header className="header">
            <div className="container header-content">
                <nav className="nav">
                    <Link to="/">Marketplace</Link>
                    <Link to="/auctions">Auctions</Link>
                </nav>

                <div className="header-actions">
                    {account ? (
                        <div className="user-menu" ref={dropdownRef}>
                            <button
                                className="hamburger-button"
                                onClick={() => setShowDropdown(!showDropdown)}
                                aria-label="User menu"
                            >
                                <div className="hamburger-icon">
                                    <span></span>
                                    <span></span>
                                    <span></span>
                                </div>
                            </button>

                            {showDropdown && (
                                <div className="dropdown-menu">
                                    <div className="dropdown-header">
                                        <span className="user-icon">{profile?.avatar || '👤'}</span>
                                        <div className="user-info">
                                            <DisplayName address={account} />
                                            <span className="user-address" title={account}>
                                                {account.slice(0, 6)}...{account.slice(-4)}
                                            </span>
                                        </div>
                                    </div>
                                    <div className="dropdown-divider"></div>
                                    <Link
                                        to="/profile"
                                        className="dropdown-item"
                                        onClick={() => setShowDropdown(false)}
                                    >
                                        <span className="dropdown-icon">📝</span>
                                        Profile
                                    </Link>
                                    <Link
                                        to="/my-nfts"
                                        className="dropdown-item"
                                        onClick={() => setShowDropdown(false)}
                                    >
                                        <span className="dropdown-icon">🖼️</span>
                                        My NFTs
                                    </Link>
                                    <div className="dropdown-divider"></div>
                                    <button
                                        className="dropdown-item disconnect-btn"
                                        onClick={handleDisconnect}
                                    >
                                        <span className="dropdown-icon">🚪</span>
                                        Disconnect
                                    </button>
                                </div>
                            )}
                        </div>
                    ) : (
                        <Button onClick={connectWallet} size="sm">
                            Connect Wallet
                        </Button>
                    )}
                </div>
            </div>
        </header>
    );
}
