import { useState } from 'react';
import { useProfile } from '../../context/ProfileContext';
import Card from '../UI/Card';
import Button from '../UI/Button';
import './ProfileSetupModal.css';

export default function ProfileSetupModal() {
    const { showSetupModal, setShowSetupModal, updateProfile } = useProfile();
    const [username, setUsername] = useState('');
    const [saving, setSaving] = useState(false);

    if (!showSetupModal) return null;

    const handleSave = async () => {
        if (!username.trim()) {
            alert('Please enter a display name');
            return;
        }

        setSaving(true);
        const success = await updateProfile(username);
        setSaving(false);

        if (success) {
            setUsername('');
        } else {
            alert('Failed to save profile. Please try again.');
        }
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
                    <label>Display Name</label>
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

                <div className="modal-actions">
                    <Button variant="ghost" onClick={handleSkip}>
                        Skip for now
                    </Button>
                    <Button onClick={handleSave} disabled={saving}>
                        {saving ? 'Saving...' : 'Save Profile'}
                    </Button>
                </div>
            </Card>
        </div>
    );
}
