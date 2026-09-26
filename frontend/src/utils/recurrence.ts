/**
 * Utilities to expand a recurring weekly event into individual occurrences.
 *
 * Occurrences are always computed from local wall-clock date/time components
 * (year/month/day/hour/minute), never by adding a fixed millisecond duration.
 * This is what makes DST transitions transparent: e.g. an event at 20:00
 * Europe/Paris time stays at 20:00 local time across a spring-forward or
 * fall-back change, even though the UTC offset (and therefore the UTC
 * instant) shifts by an hour.
 */

/** Hard safety cap on how many events a single recurrence can create. */
export const MAX_RECURRING_OCCURRENCES = 104

export interface RecurringOccurrence {
  /** Local start date/time for this occurrence */
  start: Date
  /** Local end date/time for this occurrence */
  end: Date
  /** YYYY-MM-DD key of the occurrence's start date, used for skip-lists */
  key: string
}

export interface ComputeRecurringOccurrencesOptions {
  /** Local start date/time of the first (reference) occurrence */
  startDate: Date
  /** Local end date/time of the first (reference) occurrence */
  endDate: Date
  /** Days of week to repeat on, 0 = Sunday ... 6 = Saturday */
  weekdays: number[]
  /** Inclusive local date boundary; occurrences on or before this date are kept */
  until?: Date | null
  /** Maximum number of occurrences to generate */
  count?: number | null
  /** Safety cap, defaults to MAX_RECURRING_OCCURRENCES */
  maxOccurrences?: number
}

const stripTime = (d: Date): Date => new Date(d.getFullYear(), d.getMonth(), d.getDate())

export const dateKey = (d: Date): string => {
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

export function computeRecurringOccurrences(
  opts: ComputeRecurringOccurrencesOptions,
): RecurringOccurrence[] {
  const { startDate, endDate, weekdays, until = null, count = null, maxOccurrences = MAX_RECURRING_OCCURRENCES } = opts

  if (!weekdays.length || isNaN(startDate.getTime()) || isNaN(endDate.getTime())) {
    return []
  }

  const durationDays = Math.round(
    (stripTime(endDate).getTime() - stripTime(startDate).getTime()) / 86_400_000,
  )
  const startHour = startDate.getHours()
  const startMinute = startDate.getMinutes()
  const endHour = endDate.getHours()
  const endMinute = endDate.getMinutes()

  const limit = count ? Math.min(count, maxOccurrences) : maxOccurrences
  const untilDay = until ? stripTime(until).getTime() : null

  // Scan day by day from the first occurrence's date. Bounded independently
  // of `until`/`count` so a bad combination can never loop forever.
  const hardStopDays = 366 * 3
  const occurrences: RecurringOccurrence[] = []
  const cursor = stripTime(startDate)

  for (let i = 0; i < hardStopDays && occurrences.length < limit; i++) {
    if (untilDay !== null && cursor.getTime() > untilDay) break

    if (weekdays.includes(cursor.getDay())) {
      const occStart = new Date(cursor.getFullYear(), cursor.getMonth(), cursor.getDate(), startHour, startMinute)
      const endCursor = new Date(cursor.getFullYear(), cursor.getMonth(), cursor.getDate())
      endCursor.setDate(endCursor.getDate() + durationDays)
      const occEnd = new Date(endCursor.getFullYear(), endCursor.getMonth(), endCursor.getDate(), endHour, endMinute)
      occurrences.push({ start: occStart, end: occEnd, key: dateKey(cursor) })
    }

    cursor.setDate(cursor.getDate() + 1)
  }

  return occurrences
}
