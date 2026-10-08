'use client'

// Generated from src/ by scripts/sync-skill.mjs -- edit those, not this.

import { useEffect, useRef, useState } from 'react'
import type { CSSProperties, RefObject } from 'react'

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


const PAYOFFS: Reaction[] = ['heart', 'sparkle', 'starstruck', 'grin', 'bashful']
const BLINK_MS = 120
const REACTION_MS = 560
const SQUASH_MS = 420
const DIZZY_AFTER = 4
const DIZZY_WINDOW = 1600
const DIZZY_MS = 1100

const SQUASH: Keyframe[] = [
  { transform: 'scale(1, 1)', easing: 'ease-in' },
  { transform: 'scale(1.10, 0.86)', offset: 0.18, easing: 'ease-out' },
  { transform: 'scale(0.95, 1.08)', offset: 0.45, easing: 'ease-in-out' },
  { transform: 'scale(1.03, 0.97)', offset: 0.72, easing: 'ease-in-out' },
  { transform: 'scale(1, 1)' },
]

const FINE_POINTER = '(hover: hover) and (pointer: fine)'
const REDUCED_MOTION = '(prefers-reduced-motion: reduce)'

const layer: CSSProperties = {
  position: 'absolute',
  inset: 0,
  backgroundSize: '300% 300%',
  backgroundRepeat: 'no-repeat',
}

type Sheets =
  | {
      /** The 3x3 sheet of head directions: a served path or an imported image. */
      directions: string
      /** The 3x3 sheet of expressions. */
      reactions: string
      name?: never
      basePath?: never
    }
  | {
      /** Shorthand for `${basePath}/${name}-directions.webp` and `-reactions.webp`. */
      name: string
      /** Where the sheets are served from. Default '/avatars'. */
      basePath?: string
      directions?: never
      reactions?: never
    }

export type PavatarProps = Sheets & {
  /** Width and height in px. Default 140. */
  size?: number
  /** What a screen reader calls it. Default 'avatar'. */
  label?: string
  /** Turn the head toward the pointer. Default true. */
  tracking?: boolean
  /** Within this many px of the centre it looks straight ahead. Default 70. */
  deadZone?: number
  /** React to clicks and taps. When false it renders as a plain image. Default true. */
  interactive?: boolean
  /** Fall asleep after this many ms without the pointer moving. 0 never sleeps. Default 20000. */
  sleepAfter?: number
  /** Called on every click, with the expression it is about to show. */
  onBoop?: (reaction: Reaction) => void
  className?: string
  style?: CSSProperties
}

function resolve(props: PavatarProps) {
  if (props.name !== undefined) {
    const base = (props.basePath ?? '/avatars').replace(/\/+$/, '')
    return { directions: `${base}/${props.name}-directions.webp`, reactions: `${base}/${props.name}-reactions.webp` }
  }
  return { directions: props.directions, reactions: props.reactions }
}

export function Pavatar(props: PavatarProps) {
  const {
    size = 140,
    label = 'avatar',
    tracking = true,
    deadZone = DEFAULT_AIM.deadZone,
    interactive = true,
    sleepAfter = 20000,
    onBoop,
    className,
    style,
  } = props
  const { directions, reactions } = resolve(props)

  const rootRef = useRef<HTMLElement>(null)
  const squashRef = useRef<HTMLSpanElement>(null)
  const timersRef = useRef<number[]>([])
  const boopsRef = useRef({ count: 0, at: 0 })
  const [direction, setDirection] = useState<Direction>('center')
  const [reaction, setReaction] = useState<Reaction | null>(null)
  const [asleep, setAsleep] = useState(false)

  // Head tracking. Follows the media query live, so plugging a mouse into a tablet
  // turns it on without a reload.
  useEffect(() => {
    if (!tracking) {
      return
    }
    const fine = window.matchMedia(FINE_POINTER)
    const options = { ...DEFAULT_AIM, deadZone }
    let sector: Sector = -1
    let pointer: { x: number; y: number } | null = null
    let sleepTimer = 0

    const look = () => {
      const root = rootRef.current
      if (!root || !pointer) {
        return
      }
      const box = root.getBoundingClientRect()
      sector = aim(pointer.x - (box.left + box.width / 2), pointer.y - (box.top + box.height / 2), sector, options)
      setDirection(sectorDirection(sector))
    }

    const doze = () => {
      window.clearTimeout(sleepTimer)
      setAsleep(false)
      if (sleepAfter > 0) {
        sleepTimer = window.setTimeout(() => setAsleep(true), sleepAfter)
      }
    }

    const onPointerMove = (event: PointerEvent) => {
      pointer = { x: event.clientX, y: event.clientY }
      look()
      doze()
    }

    const attach = () => {
      window.addEventListener('pointermove', onPointerMove, { passive: true })
      window.addEventListener('scroll', look, { passive: true })
      window.addEventListener('resize', look, { passive: true })
      doze()
    }

    const detach = () => {
      window.removeEventListener('pointermove', onPointerMove)
      window.removeEventListener('scroll', look)
      window.removeEventListener('resize', look)
      window.clearTimeout(sleepTimer)
      sector = -1
      setDirection('center')
      setAsleep(false)
    }

    const onChange = () => {
      detach()
      if (fine.matches) {
        attach()
      }
    }

    if (fine.matches) {
      attach()
    }
    fine.addEventListener?.('change', onChange)
    return () => {
      fine.removeEventListener?.('change', onChange)
      detach()
    }
  }, [tracking, deadZone, sleepAfter])

  useEffect(() => {
    return () => timersRef.current.forEach(window.clearTimeout)
  }, [])

  const boop = () => {
    timersRef.current.forEach(window.clearTimeout)
    timersRef.current = []
    setAsleep(false)

    const later = (ms: number, next: Reaction | null) => {
      timersRef.current.push(window.setTimeout(() => setReaction(next), ms))
    }

    const now = Date.now()
    const boops = boopsRef.current
    boops.count = now - boops.at < DIZZY_WINDOW ? boops.count + 1 : 1
    boops.at = now

    let shown: Reaction
    if (boops.count >= DIZZY_AFTER) {
      boops.count = 0
      shown = 'dizzy'
      setReaction(shown)
      later(DIZZY_MS, null)
    } else {
      shown = PAYOFFS[(boops.count - 1) % PAYOFFS.length]
      setReaction('blink')
      later(BLINK_MS, shown)
      later(REACTION_MS, null)
    }
    onBoop?.(shown)

    if (!window.matchMedia(REDUCED_MOTION).matches) {
      // Easing lives on each keyframe and the effect stays linear: an easing on the
      // effect would remap every offset and front-load the whole bounce.
      squashRef.current?.animate?.(SQUASH, { duration: SQUASH_MS, easing: 'linear' })
    }
  }

  const face: Reaction | null = reaction ?? (asleep ? 'sleepy' : null)

  // Inline styles, so the component drops into any project without a CSS setup.
  const box: CSSProperties = {
    position: 'relative',
    display: 'block',
    flexShrink: 0,
    width: size,
    height: size,
    padding: 0,
    border: 0,
    background: 'transparent',
    userSelect: 'none',
    ...style,
  }

  const art = (
    <span
      ref={squashRef}
      style={{ position: 'relative', display: 'block', width: '100%', height: '100%', transformOrigin: '50% 80%' }}
    >
      <span
        aria-hidden
        style={{
          ...layer,
          backgroundImage: cssUrl(directions),
          backgroundPosition: cellPosition(DIRECTIONS.indexOf(direction)),
          opacity: face ? 0 : 1,
        }}
      />
      {/* Always mounted, so the sheet is fetched up front and never on the first click. */}
      <span
        aria-hidden
        style={{
          ...layer,
          backgroundImage: cssUrl(reactions),
          backgroundPosition: cellPosition(REACTIONS.indexOf(face ?? 'blink')),
          opacity: face ? 1 : 0,
        }}
      />
    </span>
  )

  const data = { 'data-direction': direction, 'data-reaction': face ?? undefined }

  if (!interactive) {
    return (
      <span ref={rootRef} role="img" aria-label={label} className={className} style={box} {...data}>
        {art}
      </span>
    )
  }

  return (
    <button
      ref={rootRef as RefObject<HTMLButtonElement>}
      type="button"
      onClick={boop}
      aria-label={`Boop the ${label}`}
      className={className}
      style={{ ...box, appearance: 'none', cursor: 'pointer', WebkitTapHighlightColor: 'transparent' }}
      {...data}
    >
      {art}
    </button>
  )
}
