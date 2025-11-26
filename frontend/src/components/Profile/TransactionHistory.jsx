import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Card from '../UI/Card';
import './TransactionHistory.css';

export default function TransactionHistory({ address }) {
    const [transactions, setTransactions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchTransactions = async () => {
            if (!address) return;

            try {
                const response = await fetch(`http://localhost:8000/api/v1/users/${address}/transactions`);
                if (!response.ok) {
                    throw new Error('Failed to fetch transactions');
                }
                const data = await response.json();
                setTransactions(data);
            } catch (err) {
                console.error("Error fetching transactions:", err);
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchTransactions();
    }, [address]);

    const copyToClipboard = (text) => {
        navigator.clipboard.writeText(text);
        // Could add a toast notification here
    };

    const formatDate = (timestamp) => {
        return new Date(timestamp * 1000).toLocaleDateString() + ' ' +
            new Date(timestamp * 1000).toLocaleTimeString();
    };

    const getTransactionTypeLabel = (type) => {
        switch (type) {
            case 'buy': return 'Bought';
            case 'sell': return 'Sold';
            case 'mint': return 'Minted';
            default: return type;
        }
    };

    if (loading) return <div className="loading-tx">Loading history...</div>;
    if (error) return <div className="error-tx">Error: {error}</div>;
    if (transactions.length === 0) return <div className="no-tx">No transaction history found.</div>;

    return (
        <div className="transaction-history">
            <h3>Transaction History</h3>
            <div className="table-container">
                <table className="tx-table">
                    <thead>
                        <tr>
                            <th>Type</th>
                            <th>NFT</th>
                            <th>Price</th>
                            <th>Gas Fee</th>
                            <th>Date</th>
                            <th>Tx Hash</th>
                        </tr>
                    </thead>
                    <tbody>
                        {transactions.map((tx) => (
                            <tr key={tx.id} className={`tx-row ${tx.transaction_type}`}>
                                <td>
                                    <span className={`tx-badge ${tx.transaction_type}`}>
                                        {getTransactionTypeLabel(tx.transaction_type)}
                                    </span>
                                </td>
                                <td>
                                    <Link to={`/nft/${tx.nft_id}`} className="nft-link">
                                        {tx.nft_name}
                                    </Link>
                                </td>
                                <td className="price-col">{tx.price_eth} ETH</td>
                                <td className="gas-col">{tx.gas_fee_eth ? `${tx.gas_fee_eth.toFixed(6)} ETH` : '-'}</td>
                                <td className="date-col">{formatDate(tx.timestamp)}</td>
                                <td className="hash-col">
                                    <span title={tx.transaction_hash}>
                                        {tx.transaction_hash.slice(0, 6)}...{tx.transaction_hash.slice(-4)}
                                    </span>
                                    <button
                                        className="copy-btn"
                                        onClick={() => copyToClipboard(tx.transaction_hash)}
                                        title="Copy Transaction Hash"
                                    >
                                        📋
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
