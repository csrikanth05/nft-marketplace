import { useState, useEffect } from 'react';
import { useProfile } from '../../context/ProfileContext';
import axios from 'axios';

export default function DisplayName({ address, showFull = false }) {
    const { getDisplayName, profile, account } = useProfile();
    const [name, setName] = useState(null);

    useEffect(() => {
        if (!address) return;

        // If it's the current user, use context
        if (address.toLowerCase() === account?.toLowerCase() && profile?.username) {
            setName(profile.username);
            return;
        }

        // Otherwise fetch profile
        const fetchProfile = async () => {
            try {
                const response = await axios.get(`http://localhost:8000/api/v1/users/${address}/profile`);
                if (response.data && response.data.username) {
                    setName(response.data.username);
                } else {
                    setName(null);
                }
            } catch (error) {
                // Ignore 404s or errors, just fall back to address
                setName(null);
            }
        };

        fetchProfile();
    }, [address, account, profile]);

    if (!address) return null;

    const display = name || `${address.slice(0, 6)}...${address.slice(-4)}`;

    if (showFull) {
        return (
            <span title={address}>
                {display}
            </span>
        );
    }

    return <span title={address}>{display}</span>;
}
