import { act, cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { Pavatar } from './pavatar'

function matchMedia(fine: boolean) {
  window.matchMedia = ((query: string) => ({
    matches: query.includes('pointer: fine') ? fine : false,
    media: query,
    addEventListener: () => {},
    removeEventListener: () => {},
  })) as unknown as typeof window.matchMedia
}

function centreAt(x: number, y: number) {
  vi.spyOn(HTMLElement.prototype, 'getBoundingClientRect').mockReturnValue({
    left: x - 70, top: y - 70, width: 140, height: 140, right: x + 70, bottom: y + 70, x: x - 70, y: y - 70,
    toJSON: () => ({}),
  })
}

const move = (init: MouseEventInit) => new MouseEvent('pointermove', init)
const avatar = () => screen.getByRole('button', { name: 'Boop the cat' })

beforeEach(() => {
  vi.useFakeTimers()
  matchMedia(true)
  centreAt(500, 500)
})

afterEach(() => {
  cleanup()
  vi.useRealTimers()
  vi.restoreAllMocks()
})

describe('Pavatar', () => {
  it('turns its head toward the pointer', () => {
    render(<Pavatar directions="/d.webp" reactions="/r.webp" label="cat" />)
    expect(avatar().dataset.direction).toBe('center')
    act(() => {
      window.dispatchEvent(move({ clientX: 900, clientY: 500 }))
    })
    expect(avatar().dataset.direction).toBe('right')
    act(() => {
      window.dispatchEvent(move({ clientX: 500, clientY: 100 }))
    })
    expect(avatar().dataset.direction).toBe('up')
  })

  it('does not track without a fine pointer', () => {
    matchMedia(false)
    render(<Pavatar directions="/d.webp" reactions="/r.webp" label="cat" />)
    act(() => {
      window.dispatchEvent(move({ clientX: 900, clientY: 500 }))
    })
    expect(avatar().dataset.direction).toBe('center')
  })

  it('blinks, shows a payoff, then settles when clicked', () => {
    const onBoop = vi.fn()
    render(<Pavatar directions="/d.webp" reactions="/r.webp" label="cat" onBoop={onBoop} />)
    fireEvent.click(avatar())
    expect(avatar().dataset.reaction).toBe('blink')
    expect(onBoop).toHaveBeenCalledWith('heart')
    act(() => vi.advanceTimersByTime(200))
    expect(avatar().dataset.reaction).toBe('heart')
    act(() => vi.advanceTimersByTime(600))
    expect(avatar().dataset.reaction).toBeUndefined()
  })

  it('gets dizzy when poked quickly', () => {
    render(<Pavatar directions="/d.webp" reactions="/r.webp" label="cat" />)
    for (let i = 0; i < 4; i++) {
      fireEvent.click(avatar())
      act(() => vi.advanceTimersByTime(100))
    }
    expect(avatar().dataset.reaction).toBe('dizzy')
  })

  it('falls asleep when the pointer stops moving', () => {
    render(<Pavatar directions="/d.webp" reactions="/r.webp" label="cat" sleepAfter={1000} />)
    act(() => vi.advanceTimersByTime(1100))
    expect(avatar().dataset.reaction).toBe('sleepy')
    act(() => {
      window.dispatchEvent(move({ clientX: 510, clientY: 510 }))
    })
    expect(avatar().dataset.reaction).toBeUndefined()
  })
})

describe('Pavatar props', () => {
  it('resolves name and basePath to the two sheets', () => {
    render(<Pavatar name="mochi" basePath="/static/avatars/" label="cat" />)
    const [directions, reactions] = avatar().querySelectorAll<HTMLElement>('span span')
    expect(directions.style.backgroundImage).toContain('/static/avatars/mochi-directions.webp')
    expect(reactions.style.backgroundImage).toContain('/static/avatars/mochi-reactions.webp')
  })

  it('defaults basePath to /avatars', () => {
    render(<Pavatar name="kuma" label="cat" />)
    expect(avatar().querySelector<HTMLElement>('span span')!.style.backgroundImage).toContain('/avatars/kuma-directions.webp')
  })

  it('stays still with tracking off', () => {
    render(<Pavatar name="kuma" label="cat" tracking={false} />)
    act(() => {
      window.dispatchEvent(move({ clientX: 900, clientY: 500 }))
    })
    expect(avatar().dataset.direction).toBe('center')
  })

  it('honours a custom dead zone', () => {
    render(<Pavatar name="kuma" label="cat" deadZone={500} />)
    act(() => {
      window.dispatchEvent(move({ clientX: 900, clientY: 500 }))
    })
    expect(avatar().dataset.direction).toBe('center')
  })

  it('renders a plain image when not interactive', () => {
    render(<Pavatar name="kuma" label="cat" interactive={false} />)
    expect(screen.queryByRole('button')).toBeNull()
    expect(screen.getByRole('img', { name: 'cat' })).toBeTruthy()
  })
})
