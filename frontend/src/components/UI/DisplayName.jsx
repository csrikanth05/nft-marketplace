import { useProfile } from '../../context/ProfileContext';

export default function DisplayName({ address, showFull = false }) {
    const { getDisplayName } = useProfile();

    if (!address) return null;

    const displayName = getDisplayName(address);

    if (showFull) {
        return (
            <span title={address}>
                {displayName}
            </span>
        );
    }

    return <span>{displayName}</span>;
}
