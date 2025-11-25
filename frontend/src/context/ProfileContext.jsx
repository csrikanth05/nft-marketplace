import { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const ProfileContext = createContext();

export const useProfile = () => {
    const context = useContext(ProfileContext);
    if (!context) {
        throw new Error('useProfile must be used within ProfileProvider');
    }
    return context;
};

export const ProfileProvider = ({ children, account }) => {
    const [profile, setProfile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [showSetupModal, setShowSetupModal] = useState(false);

    useEffect(() => {
        if (account) {
            loadProfile(account);
        } else {
            setProfile(null);
        }
    }, [account]);

    const loadProfile = async (address) => {
        setLoading(true);
        try {
            const response = await axios.get(`http://localhost:8000/api/v1/users/${address}/profile`);
            setProfile(response.data);

            // Show setup modal if no username set
            if (!response.data.username) {
                setShowSetupModal(true);
            }
        } catch (error) {
            console.error('Error loading profile:', error);
        } finally {
            setLoading(false);
        }
    };

    const updateProfile = async (username) => {
        if (!account) return;

        try {
            const response = await axios.post(
                `http://localhost:8000/api/v1/users/profile?address=${account}`,
                { username }
            );
            setProfile(response.data);
            setShowSetupModal(false);
            return true;
        } catch (error) {
            console.error('Error updating profile:', error);
            return false;
        }
    };

    const getDisplayName = (address) => {
        if (!address) return '';

        // If it's the current user's address, use their profile
        if (address.toLowerCase() === account?.toLowerCase() && profile?.username) {
            return profile.username;
        }

        // Otherwise show shortened address
        return `${address.slice(0, 6)}...${address.slice(-4)}`;
    };

    return (
        <ProfileContext.Provider
            value={{
                profile,
                loading,
                showSetupModal,
                setShowSetupModal,
                updateProfile,
                getDisplayName
            }}
        >
            {children}
        </ProfileContext.Provider>
    );
};
