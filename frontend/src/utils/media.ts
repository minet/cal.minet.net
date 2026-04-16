import type { StoredFileRead } from '../api/types'

// Parse sizes from build-time env var (Vite)
const SIZES = (import.meta.env.VITE_MEDIA_SIZES ?? '320,640,960,1280')
  .split(',')
  .map(Number)
  .sort((a: number, b: number) => a - b)

// Suppress "unused variable" — SIZES is available for future use
void SIZES

/**
 * Resolve the best URL for a stored file given a display width.
 * Falls back to the original URL if no variants are available.
 */
export function resolveMediaUrl(
  storedFile: StoredFileRead | null | undefined,
  displayWidth: number,
  format = 'webp',
): string | null {
  if (!storedFile) return null
  const variants = (storedFile.variants ?? []).filter((v) => v.format === format)
  if (!variants.length) return storedFile.url

  const target = displayWidth * (window.devicePixelRatio || 1)
  const sorted = [...variants].sort((a, b) => a.width - b.width)
  const best = sorted.find((v) => v.width >= target) ?? sorted[sorted.length - 1]
  return best?.url ?? storedFile.url
}

/**
 * Build a srcset string from stored file variants (for <img srcset>).
 */
export function buildSrcset(storedFile: StoredFileRead | null | undefined): string {
  if (!storedFile?.variants?.length) return ''
  return storedFile.variants
    .filter((v) => v.format === 'webp')
    .map((v) => `${v.url} ${v.width}w`)
    .join(', ')
}
