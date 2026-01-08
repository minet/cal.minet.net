/**
 * Utilities for handling date conversions between UTC and local timezone
 */

/**
 * Convert UTC date to local Date object
 * @param {string|Date} utcDate - UTC date string or Date object
 * @returns {Date} Local Date object
 */
export const utcToLocal = (utcDate) => {
    return new Date(utcDate)
}

/**
 * Format a date in the user's local timezone
 * @param {string|Date} date - Date to format
 * @param {object} options - Intl.DateTimeFormat options
 * @returns {string} Formatted date string
 */
export const formatLocalDate = (date, options = {}) => {
    // Check if options contain any specific date/time components that conflict with dateStyle/timeStyle
    const componentProps = ['weekday', 'era', 'year', 'month', 'day', 'hour', 'minute', 'second', 'timeZoneName']
    const hasComponentProps = componentProps.some(prop => prop in options)

    const defaultOptions = hasComponentProps ? {} : {
        dateStyle: 'medium',
        timeStyle: 'short'
    }

    const finalOptions = {
        ...defaultOptions,
        ...options
    }

    return new Intl.DateTimeFormat('fr-FR', finalOptions).format(new Date(date))
}

/**
 * Format date with custom pattern
 * @param {string|Date} date - Date to format
 * @param {string} pattern - 'short'|'medium'|'long'|'full' or custom options
 * @returns {string} Formatted date string
 */
export const formatDate = (date, pattern = 'medium') => {
    const patterns = {
        short: { dateStyle: 'short', timeStyle: 'short' },
        medium: { dateStyle: 'medium', timeStyle: 'short' },
        long: { dateStyle: 'long', timeStyle: 'medium' },
        full: { dateStyle: 'full', timeStyle: 'long' },
        dateOnly: { dateStyle: 'medium' },
        timeOnly: { timeStyle: 'short' }
    }

    const options = patterns[pattern] || patterns.medium
    return formatLocalDate(date, options)
}

/**
 * Convert local date to UTC ISO string
 * @param {string|Date} localDate - Local date
 * @returns {string} UTC ISO string
 */
export const localToUtc = (localDate) => {
    return new Date(localDate).toISOString()
}

/**
 * Get relative time string (e.g., "dans 2 jours", "il y a 3 heures")
 * @param {string|Date} date - Date to compare
 * @returns {string} Relative time string
 */
export const getRelativeTime = (date) => {
    const rtf = new Intl.RelativeTimeFormat('fr-FR', { numeric: 'auto' })
    const now = new Date()
    const target = new Date(date)
    const diffMs = target - now
    const diffSec = Math.round(diffMs / 1000)
    const diffMin = Math.round(diffSec / 60)
    const diffHour = Math.round(diffMin / 60)
    const diffDay = Math.round(diffHour / 24)

    if (Math.abs(diffDay) >= 1) {
        return rtf.format(diffDay, 'day')
    } else if (Math.abs(diffHour) >= 1) {
        return rtf.format(diffHour, 'hour')
    } else if (Math.abs(diffMin) >= 1) {
        return rtf.format(diffMin, 'minute')
    } else {
        return rtf.format(diffSec, 'second')
    }
}

/**
 * Check if a date is in the past
 * @param {string|Date} date - Date to check
 * @returns {boolean}
 */
export const isPast = (date) => {
    return new Date(date) < new Date()
}

/**
 * Check if a date is in the future
 * @param {string|Date} date - Date to check
 * @returns {boolean}
 */
export const isFuture = (date) => {
    return new Date(date) > new Date()
}
