export function renderUnresolvedMemberMention(
  rawKey: string,
  originalMention: string,
): string {
  // The editor stores member mentions by immutable user UUID. If that UUID is
  // absent from the viewer's filtered member list, rendering any placeholder
  // would reveal that content was hidden. Names and handles are not canonical
  // references and may legitimately refer to something other than a member.
  const isCanonicalMemberReference =
    /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(
      rawKey.trim(),
    )
  return isCanonicalMemberReference ? '' : originalMention
}
