import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ProfileProvider } from './context/ProfileContext';
import Header from './components/Layout/Header';
import ProfileSetupModal from './components/Profile/ProfileSetupModal';
import Home from './pages/Home';
import CreateNFT from './pages/CreateNFT';
import MyNFTs from './pages/MyNFTs';
import Auctions from './pages/Auctions';
import NFTDetail from './pages/NFTDetail';
import './App.css';

function App() {
    const [account, setAccount] = useState(null);

    useEffect(() => {
        checkWalletConnection();
    }, []);

    const checkWalletConnection = async () => {
        if (window.ethereum) {
            try {
                const accounts = await window.ethereum.request({ method: 'eth_accounts' });
                if (accounts.length > 0) {
                    setAccount(accounts[0]);
                }
            } catch (error) {
                console.error('Error checking wallet connection:', error);
            }
        }
    };

    const connectWallet = async () => {
        if (!window.ethereum) {
            alert('Please install MetaMask to use this application');
            return;
        }

        try {
            const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
            setAccount(accounts[0]);
        } catch (error) {
            console.error('Error connecting wallet:', error);
            alert('Failed to connect wallet');
        }
    };

    return (
        <Router>
            <ProfileProvider account={account}>
                <div className="app">
                    <Header account={account} connectWallet={connectWallet} />
                    <ProfileSetupModal />
                    <main className="main-content">
                        <Routes>
                            <Route path="/" element={<Home />} />
                            <Route path="/create" element={<CreateNFT account={account} />} />
                            <Route path="/my-nfts" element={<MyNFTs account={account} />} />
                            <Route path="/auctions" element={<Auctions />} />
                            <Route path="/nft/:tokenId" element={<NFTDetail account={account} />} />
                        </Routes>
                    </main>
                </div>
            </ProfileProvider>
        </Router>
    );
}

export default App;
