// Parse sizes from build-time env var (Vite)
const SIZES = (import.meta.env.VITE_MEDIA_SIZES || '320,640,960,1280')
  .split(',').map(Number).sort((a, b) => a - b)

/**
 * Resolve the best URL for a stored file given a display width.
 * Falls back to the original URL if no variants are available.
 * @param {Object|null} storedFile  - StoredFileRead object from the API
 * @param {number} displayWidth     - Target display width in CSS pixels
 * @param {string} [format='webp']  - Preferred format ('webp' or 'webm')
 * @returns {string|null}
 */
export function resolveMediaUrl(storedFile, displayWidth, format = 'webp') {
  if (!storedFile) return null
  const variants = (storedFile.variants || []).filter(v => v.format === format)
  if (!variants.length) return storedFile.url

  // Account for device pixel ratio
  const target = displayWidth * (window.devicePixelRatio || 1)
  const sorted = [...variants].sort((a, b) => a.width - b.width)
  const best = sorted.find(v => v.width >= target) ?? sorted[sorted.length - 1]
  return best.url
}

/**
 * Build a srcset string from stored file variants (for <img srcset>).
 * @param {Object|null} storedFile
 * @returns {string}
 */
export function buildSrcset(storedFile) {
  if (!storedFile?.variants?.length) return ''
  return storedFile.variants
    .filter(v => v.format === 'webp')
    .map(v => `${v.url} ${v.width}w`)
    .join(', ')
}
