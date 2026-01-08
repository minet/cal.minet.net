// Convert Hex to OKLCH (approximate for picking)

// References: https://bottosson.github.io/posts/oklab/
// Implementation adapted for JS.

function fast_srgb8_to_linear(v) {
    if (v <= 0.04045) return v / 12.92;
    return Math.pow((v + 0.055) / 1.055, 2.4);
}

function linear_to_oklab(r, g, b) {
    let l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b;
    let m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b;
    let s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b;

    let l_ = Math.cbrt(l);
    let m_ = Math.cbrt(m);
    let s_ = Math.cbrt(s);

    return {
        L: 0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
        a: 1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
        b: 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_
    };
}

function oklab_to_oklch(L, a, b) {
    let C = Math.sqrt(a * a + b * b);
    let h = Math.atan2(b, a) * 180 / Math.PI;
    if (h < 0) h += 360;
    return { L, C, h };
}

export function hexToOklch(hex) {
    // Expand shorthand form (e.g. "03F") to full form (e.g. "0033FF")
    var shorthandRegex = /^#?([a-f\d])([a-f\d])([a-f\d])$/i;
    hex = hex.replace(shorthandRegex, function (m, r, g, b) {
        return r + r + g + g + b + b;
    });

    var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    if (!result) return null;

    let r = parseInt(result[1], 16) / 255;
    let g = parseInt(result[2], 16) / 255;
    let b = parseInt(result[3], 16) / 255;

    r = fast_srgb8_to_linear(r);
    g = fast_srgb8_to_linear(g);
    b = fast_srgb8_to_linear(b);

    const lab = linear_to_oklab(r, g, b);
    return oklab_to_oklch(lab.L, lab.a, lab.b);
}

// Reverse conversion for editing (approximated)
function oklch_to_oklab(L, C, h) {
    let h_rad = h * Math.PI / 180;
    return {
        L: L,
        a: C * Math.cos(h_rad),
        b: C * Math.sin(h_rad)
    };
}

function oklab_to_linear(L, a, b) {
    let l_ = L + 0.3963377774 * a + 0.2158037573 * b;
    let m_ = L - 0.1055613458 * a - 0.0638541728 * b;
    let s_ = L - 0.0894841775 * a - 1.2914855480 * b;

    let l = l_ * l_ * l_;
    let m = m_ * m_ * m_;
    let s = s_ * s_ * s_;

    return {
        r: +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
        g: -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
        b: -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s
    };
}

function linear_srgb_to_srgb8(v) {
    let val = v <= 0.0031308 ? 12.92 * v : 1.055 * Math.pow(v, 1 / 2.4) - 0.055;
    return Math.max(0, Math.min(1, val));
}

function componentToHex(c) {
    var hex = Math.round(c * 255).toString(16);
    return hex.length == 1 ? "0" + hex : hex;
}

export function oklchToHex(l, c, h) {
    // If undefined/null, return black or default
    if (l === undefined || c === undefined || h === undefined) return "#000000";

    const lab = oklch_to_oklab(l, c, h);
    const lin = oklab_to_linear(lab.L, lab.a, lab.b);

    const r = linear_srgb_to_srgb8(lin.r);
    const g = linear_srgb_to_srgb8(lin.g);
    const b = linear_srgb_to_srgb8(lin.b);

    return "#" + componentToHex(r) + componentToHex(g) + componentToHex(b);
}

export function getOrgColor(chroma, hue, luminance = 0.6) {
    if (chroma === null || chroma === undefined || hue === null || hue === undefined) {
        console.error("chroma or hue is null or undefined");
        // Fallback or gray
        return `oklch(${luminance} 0 0)`;
    }
    return `oklch(${luminance} ${chroma} ${hue})`;
}

export function getDefaultOrgColor(name) {
    if (!name) return 'oklch(0.6 0.1 250)';

    // Simple hash function
    let hash = 0;
    for (let i = 0; i < name.length; i++) {
        hash = name.charCodeAt(i) + ((hash << 5) - hash);
    }

    // Generate hue from hash (0-360)
    const hue = Math.abs(hash % 360);
    // Fixed chroma and luminance for consistency
    const chroma = 0.15;
    const luminance = 0.65;

    return `oklch(${luminance} ${chroma} ${hue})`;
}

export function getOrgTextColor(chroma, hue, backgroundLuminance) {
    // If luminance is high, text should be dark.
    // If luminance is low, text should be bright (white).
    // Using 0.6 as a threshold is common for OKLCH perceptual lightness.
    if (backgroundLuminance === null || backgroundLuminance === undefined) {
        // Assume default background luminance if not provided
        backgroundLuminance = 0.6;
    }

    // We can also just ignore chroma/hue for text color usually, 

    if (backgroundLuminance > 0.65) {
        return '#1f2937'; // gray-800
    } else {
        return '#ffffff'; // white
    }
}
