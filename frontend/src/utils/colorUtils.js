
export function getEventGradient(mainOrg, guestOrgs = []) {
    const orgs = [mainOrg, ...(guestOrgs || [])].filter(Boolean);
    if (orgs.length === 0) return '#f9fafb'; // gray-50

    const colors = orgs.map(o => {
        return o.color_secondary || '#f3f4f6'; // Fallback to gray-100
    });

    if (colors.length === 1) return colors[0];

    return `linear-gradient(135deg, ${colors.join(', ')})`;
}

export function getOrgTextColor(org) {
    // Simple logic : if primary color is provided, maybe return it, otherwise black
    // Actually, usually we want text on top of the background.
    // But since we have explicit light/dark colors, we might just use them directly in components.
    // For now, let's keep a helper that returns the primary color for text usage?
    // Or maybe just return color_dark for text?
    return org?.color_dark || '#111827';
}

