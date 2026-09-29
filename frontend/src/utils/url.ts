const ALLOWED_SCHEMES = new Set(['http', 'https', 'mailto', 'tel'])

export function safeUrl(url: string | null | undefined): string | undefined {
  if (!url) return undefined
  const compact = url.replace(/[\u0000- \u007f]/g, '')
  const match = /^([a-zA-Z][a-zA-Z0-9+.-]*):/.exec(compact)
  if (match && !ALLOWED_SCHEMES.has(match[1].toLowerCase())) return undefined
  return url.trim()
}
