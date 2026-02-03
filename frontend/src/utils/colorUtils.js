
export function getEventGradient(mainOrg, guestOrgs = []) {
    const orgs = [mainOrg, ...(guestOrgs || [])].filter(Boolean);
    if (orgs.length === 0) return '#f9fafb42';

    const colors = orgs.map(o => {
        return o.color_primary || '#f3f4f64d';
    });

    if (orgs.some(o => o.slug === 'in-act')) {
        return 'linear-gradient(135deg, rgb(237, 34, 36), rgb(243, 91, 34), rgb(249, 150, 33), rgb(245, 193, 30), rgb(241, 235, 27) 27%, rgb(241, 235, 27), rgb(241, 235, 27) 33%, rgb(99, 199, 32), rgb(12, 155, 73), rgb(33, 135, 141), rgb(57, 84, 165), rgb(97, 55, 155), rgb(147, 40, 142))';
    }
    if (colors.length === 1) return colors[0];

    return `linear-gradient(135deg, ${colors.join(', ')})`;
}

export function getEventGradientLight(mainOrg, guestOrgs = []) {
    const orgs = [mainOrg, ...(guestOrgs || [])].filter(Boolean);
    if (orgs.length === 0) return '#f9fafbea';

    const colors = orgs.map(o => {
        return o.color_secondary || '#f9fafbea';
    });

    if (orgs.some(o => o.slug === 'in-act')) {
        return 'linear-gradient(135deg, #ffadad, #ffd6a5, #fdffb6, #caffbf, #9bf6ff, #a0c4ff, #bdb2ff)';

    }
    if (colors.length === 1) return colors[0];

    return `linear-gradient(135deg, ${colors.join(', ')})`;
}


export function getOrgTextColor(org) {
    return org?.color_dark || '#111827';
}

// Helper functions for color manipulation

export function hexToRgb(hex) {
    var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
    } : null;
}

export function rgbToHsl(r, g, b) {
    r /= 255;
    g /= 255;
    b /= 255;
    var max = Math.max(r, g, b), min = Math.min(r, g, b);
    var h, s, l = (max + min) / 2;

    if (max == min) {
        h = s = 0; // achromatic
    } else {
        var d = max - min;
        s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
        switch (max) {
            case r: h = (g - b) / d + (g < b ? 6 : 0); break;
            case g: h = (b - r) / d + 2; break;
            case b: h = (r - g) / d + 4; break;
        }
        h /= 6;
    }

    return { h, s, l };
}

export function hslToRgb(h, s, l) {
    var r, g, b;

    if (s == 0) {
        r = g = b = l; // achromatic
    } else {
        var hue2rgb = function (p, q, t) {
            if (t < 0) t += 1;
            if (t > 1) t -= 1;
            if (t < 1 / 6) return p + (q - p) * 6 * t;
            if (t < 1 / 2) return q;
            if (t < 2 / 3) return p + (q - p) * (2 / 3 - t) * 6;
            return p;
        }

        var q = l < 0.5 ? l * (1 + s) : l + s - l * s;
        var p = 2 * l - q;
        r = hue2rgb(p, q, h + 1 / 3);
        g = hue2rgb(p, q, h);
        b = hue2rgb(p, q, h - 1 / 3);
    }

    return { r: Math.round(r * 255), g: Math.round(g * 255), b: Math.round(b * 255) };
}

export function rgbToHex(r, g, b) {
    return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
}

export function getSaturation(hex) {
    const rgb = hexToRgb(hex);
    if (!rgb) return 0;
    const hsl = rgbToHsl(rgb.r, rgb.g, rgb.b);
    return hsl.s;
}

export function generateColorVariant(hex, lightness) {
    const rgb = hexToRgb(hex);
    if (!rgb) return hex;
    const hsl = rgbToHsl(rgb.r, rgb.g, rgb.b);

    // Set the new lightness
    const newRgb = hslToRgb(hsl.h, hsl.s, lightness);
    return rgbToHex(newRgb.r, newRgb.g, newRgb.b);
}
