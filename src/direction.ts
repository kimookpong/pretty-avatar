// The sheet order of both 3x3 sprite sheets, left to right, top to bottom.
export const DIRECTIONS = [
  'up-left',
  'up',
  'up-right',
  'left',
  'center',
  'right',
  'down-left',
  'down',
  'down-right',
] as const

export const REACTIONS = [
  'blink',
  'heart',
  'sparkle',
  'surprised',
  'starstruck',
  'bashful',
  'sleepy',
  'dizzy',
  'grin',
] as const

export type Direction = (typeof DIRECTIONS)[number]
export type Reaction = (typeof REACTIONS)[number]

// Clockwise from the right, matching atan2 when y grows downwards as it does on screen.
const RING: Direction[] = ['right', 'down-right', 'down', 'down-left', 'left', 'up-left', 'up', 'up-right']
const SECTOR = (Math.PI * 2) / RING.length

export type AimOptions = {
  /** Within this many px of the avatar's centre it looks straight ahead. */
  deadZone: number
  /** Radians past a sector's edge the pointer must go before the head turns. */
  hysteresis: number
}

export const DEFAULT_AIM: AimOptions = { deadZone: 70, hysteresis: 0.12 }

/** -1 means looking straight ahead. */
export type Sector = number

function wrap(angle: number) {
  return Math.atan2(Math.sin(angle), Math.cos(angle))
}

/**
 * Which way to look for a pointer at (dx, dy) from the avatar's centre.
 *
 * The previous sector is held until the pointer is clearly past its edge, so a cursor
 * resting on a boundary does not make the head flicker between two cells.
 */
export function aim(dx: number, dy: number, previous: Sector, options: AimOptions = DEFAULT_AIM): Sector {
  if (Math.hypot(dx, dy) < options.deadZone) {
    return -1
  }
  const angle = Math.atan2(dy, dx)
  if (previous !== -1 && Math.abs(wrap(angle - previous * SECTOR)) < SECTOR / 2 + options.hysteresis) {
    return previous
  }
  return (Math.round(angle / SECTOR) + RING.length) % RING.length
}

export function sectorDirection(sector: Sector): Direction {
  return sector === -1 ? 'center' : RING[sector]
}

/** background-position for a cell of a 3x3 sheet drawn at background-size 300%. */
export function cellPosition(index: number) {
  return `${(index % 3) * 50}% ${Math.floor(index / 3) * 50}%`
}

/** A CSS url(), quoted so a path with spaces, brackets or quotes stays one value. */
export function cssUrl(src: string) {
  return `url("${src.replace(/["\\\n]/g, (c) => (c === '\n' ? '\\a ' : `\\${c}`))}")`
}
