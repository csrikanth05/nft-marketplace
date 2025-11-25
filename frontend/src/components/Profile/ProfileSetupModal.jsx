import { useState, useEffect } from 'react';
import { useProfile } from '../../context/ProfileContext';
import Card from '../UI/Card';
import Button from '../UI/Button';
import './ProfileSetupModal.css';

const AVATAR_OPTIONS = ['😀', '🎨', '🚀', '💎', '🦄', '🎭'];

export default function ProfileSetupModal() {
    const { showSetupModal, setShowSetupModal, updateProfile } = useProfile();
    const [username, setUsername] = useState('');
    const [selectedAvatar, setSelectedAvatar] = useState(AVATAR_OPTIONS[0]);
    const [email, setEmail] = useState('');
    const [saving, setSaving] = useState(false);

    // Lock body scroll when modal is open
    useEffect(() => {
        if (showSetupModal) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = 'unset';
        }

        return () => {
            document.body.style.overflow = 'unset';
        };
    }, [showSetupModal]);

    if (!showSetupModal) return null;

    const handleSave = async () => {
        if (!username.trim()) {
            alert('Please enter a display name');
            return;
        }

        if (email && !isValidEmail(email)) {
            alert('Please enter a valid email address');
            return;
        }

        setSaving(true);
        const success = await updateProfile(username, selectedAvatar, email);
        setSaving(false);

        if (success) {
            setUsername('');
            setEmail('');
        } else {
            alert('Failed to save profile. Please try again.');
        }
    };

    const isValidEmail = (email) => {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    };

    const handleSkip = () => {
        setShowSetupModal(false);
    };

    return (
        <div className="modal-overlay">
            <Card className="profile-setup-modal">
                <h2>Welcome! 👋</h2>
                <p>Set up your profile to personalize your experience</p>

                <div className="form-group">
                    <label>Choose Your Avatar</label>
                    <div className="avatar-grid">
                        {AVATAR_OPTIONS.map((avatar) => (
                            <button
                                key={avatar}
                                type="button"
                                className={`avatar-option ${selectedAvatar === avatar ? 'selected' : ''}`}
                                onClick={() => setSelectedAvatar(avatar)}
                            >
                                {avatar}
                            </button>
                        ))}
                    </div>
                </div>

                <div className="form-group">
                    <label>Display Name *</label>
                    <input
                        type="text"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        placeholder="Enter your display name"
                        maxLength={30}
                        autoFocus
                    />
                    <small>{username.length}/30 characters</small>
                </div>

                <div className="form-group">
                    <label>Email (Optional)</label>
                    <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="your.email@example.com"
                    />
                    <small>Receive notifications about your NFT transactions</small>
                </div>

                <div className="modal-actions">
                    <Button variant="ghost" onClick={handleSkip}>
                        Skip for now
                    </Button>
                    <Button onClick={handleSave} disabled={saving}>
                        {saving ? 'Submitting...' : 'Submit'}
                    </Button>
                </div>
            </Card>
        </div>
    );
}
