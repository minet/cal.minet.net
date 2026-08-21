/**
 * Converts the first description line to the compact, readable form used in
 * organization lists. The full Markdown is rendered on the organization page.
 */
export function descriptionPreview(description: string | null | undefined): string {
  const firstLine = description?.split(/\r?\n/, 1)[0] ?? ''
  const memberLabel = (key: string) =>
    /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(key.trim())
      ? 'Membre'
      : key

  return firstLine
    .replace(/!?\[([^\]]*)\]\([^)]+\)/g, '$1')
    .replace(/@\[([^\]]+)\]/g, (_match, key: string) => memberLabel(key))
    .replace(/(^|[\s([{])@([a-zA-Z0-9._-]+(?:@[a-zA-Z0-9._-]+)?)/g, '$1$2')
    .trim()
}
