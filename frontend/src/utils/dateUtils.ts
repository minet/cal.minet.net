/**
 * Utilities for handling date conversions between UTC and local timezone
 */

/** Convert UTC date to local Date object */
export const utcToLocal = (utcDate: string | Date): Date => {
  return new Date(utcDate)
}

type DatePattern = 'short' | 'medium' | 'long' | 'full' | 'dateOnly' | 'timeOnly'

const DATE_PATTERN_OPTIONS: Record<DatePattern, Intl.DateTimeFormatOptions> = {
  short: { dateStyle: 'short', timeStyle: 'short' },
  medium: { dateStyle: 'medium', timeStyle: 'short' },
  long: { dateStyle: 'long', timeStyle: 'medium' },
  full: { dateStyle: 'full', timeStyle: 'long' },
  dateOnly: { dateStyle: 'medium' },
  timeOnly: { timeStyle: 'short' },
}

/** Format a date in the user's local timezone */
export const formatLocalDate = (
  date: string | Date,
  options: Intl.DateTimeFormatOptions = {},
): string => {
  const componentProps: (keyof Intl.DateTimeFormatOptions)[] = [
    'weekday',
    'era',
    'year',
    'month',
    'day',
    'hour',
    'minute',
    'second',
    'timeZoneName',
  ]
  const hasComponentProps = componentProps.some((prop) => prop in options)

  const defaultOptions: Intl.DateTimeFormatOptions = hasComponentProps
    ? {}
    : { dateStyle: 'medium', timeStyle: 'short' }

  const finalOptions: Intl.DateTimeFormatOptions = { ...defaultOptions, ...options }

  return new Intl.DateTimeFormat('fr-FR', finalOptions).format(new Date(date))
}

/** Format date with a named pattern */
export const formatDate = (date: string | Date, pattern: DatePattern = 'medium'): string => {
  const options = DATE_PATTERN_OPTIONS[pattern]
  return formatLocalDate(date, options)
}

/** Convert local date to UTC ISO string */
export const localToUtc = (localDate: string | Date): string => {
  return new Date(localDate).toISOString()
}

/** Get relative time string (e.g., "dans 2 jours", "il y a 3 heures") */
export const getRelativeTime = (date: string | Date): string => {
  const rtf = new Intl.RelativeTimeFormat('fr-FR', { numeric: 'auto' })
  const now = new Date()
  const target = new Date(date)
  const diffMs = target.getTime() - now.getTime()
  const diffSec = Math.round(diffMs / 1000)
  const diffMin = Math.round(diffSec / 60)
  const diffHour = Math.round(diffMin / 60)
  const diffDay = Math.round(diffHour / 24)

  if (Math.abs(diffDay) >= 1) return rtf.format(diffDay, 'day')
  if (Math.abs(diffHour) >= 1) return rtf.format(diffHour, 'hour')
  if (Math.abs(diffMin) >= 1) return rtf.format(diffMin, 'minute')
  return rtf.format(diffSec, 'second')
}

/** Check if a date is in the past */
export const isPast = (date: string | Date): boolean => {
  return new Date(date) < new Date()
}

/** Check if a date is in the future */
export const isFuture = (date: string | Date): boolean => {
  return new Date(date) > new Date()
}
