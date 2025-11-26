import { useProfile } from '../context/ProfileContext';
import Card from '../components/UI/Card';
import Button from '../components/UI/Button';
import TransactionHistory from '../components/Profile/TransactionHistory';
import './Profile.css';

export default function Profile({ account }) {
    const { profile, setShowSetupModal } = useProfile();

    if (!account) {
        return (
            <div className="profile-page">
                <div className="container">
                    <h2>Please connect your wallet to view your profile</h2>
                </div>
            </div>
        );
    }

    return (
        <div className="profile-page">
            <div className="container">
                <h1>My Profile</h1>

                <Card className="profile-card">
                    <div className="profile-header">
                        <div className="profile-avatar-large">
                            {profile?.avatar || '👤'}
                        </div>
                        <div className="profile-info">
                            <h2>{profile?.username || 'Anonymous'}</h2>
                            <p className="profile-address" title={account}>
                                {account}
                            </p>
                        </div>
                    </div>

                    <div className="profile-divider"></div>

                    <div className="profile-details">
                        <div className="detail-row">
                            <span className="detail-label">Display Name</span>
                            <span className="detail-value">{profile?.username || '-'}</span>
                        </div>

                        <div className="detail-row">
                            <span className="detail-label">Avatar</span>
                            <span className="detail-value avatar-display">{profile?.avatar || '👤'}</span>
                        </div>

                        <div className="detail-row">
                            <span className="detail-label">Email</span>
                            <span className="detail-value">{profile?.email || 'Not provided'}</span>
                        </div>

                        <div className="detail-row">
                            <span className="detail-label">Wallet Address</span>
                            <span className="detail-value monospace">{account}</span>
                        </div>
                    </div>

                    <div className="profile-actions">
                        <Button onClick={() => setShowSetupModal(true)}>
                            Edit Profile
                        </Button>
                    </div>
                </Card>

                <TransactionHistory address={account} />
            </div>
        </div>
    );
}
