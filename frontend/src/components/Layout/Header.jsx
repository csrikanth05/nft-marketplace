import { Link } from 'react-router-dom';
import Button from '../UI/Button';
import DisplayName from '../UI/DisplayName';
import './Header.css';

export default function Header({ account, connectWallet }) {
    return (
        <header className="header">
            <div className="container header-content">
                <Link to="/" className="logo">
                    <h2>NFT Marketplace</h2>
                </Link>

                <nav className="nav">
                    <Link to="/">Marketplace</Link>
                    <Link to="/create">Create NFT</Link>
                    <Link to="/my-nfts">My NFTs</Link>
                    <Link to="/auctions">Auctions</Link>
                </nav>

                <div className="header-actions">
                    {account ? (
                        <div className="wallet-info" title={account}>
                            <span className="wallet-address">
                                <DisplayName address={account} showFull />
                            </span>
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
