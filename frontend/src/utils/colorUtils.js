
export function getEventGradient(mainOrg, guestOrgs = []) {
    const orgs = [mainOrg, ...(guestOrgs || [])].filter(Boolean);
    if (orgs.length === 0) return '#f9fafb42';

    const colors = orgs.map(o => {
        return o.color_primary || '#f3f4f64d';
    });

    if (colors.length === 1) return colors[0];

    return `linear-gradient(135deg, ${colors.join(', ')})`;
}

export function getOrgTextColor(org) {
    return org?.color_dark || '#111827';
}

