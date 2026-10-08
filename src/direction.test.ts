import { describe, expect, it } from 'vitest'
import { aim, cellPosition, cssUrl, DIRECTIONS, sectorDirection } from './direction'

const look = (dx: number, dy: number, previous = -1) => sectorDirection(aim(dx, dy, previous))

describe('aim', () => {
  it('looks straight ahead inside the dead zone', () => {
    expect(look(10, -20)).toBe('center')
    expect(look(0, 0)).toBe('center')
  })

  it('points at all eight compass directions', () => {
    expect(look(200, 0)).toBe('right')
    expect(look(200, 200)).toBe('down-right')
    expect(look(0, 200)).toBe('down')
    expect(look(-200, 200)).toBe('down-left')
    expect(look(-200, 0)).toBe('left')
    expect(look(-200, -200)).toBe('up-left')
    expect(look(0, -200)).toBe('up')
    expect(look(200, -200)).toBe('up-right')
  })

  it('holds the current sector just past its edge', () => {
    // 25 degrees is past the right/down-right boundary at 22.5, but inside the hysteresis.
    const angle = (25 * Math.PI) / 180
    const dx = Math.cos(angle) * 200
    const dy = Math.sin(angle) * 200
    expect(look(dx, dy)).toBe('down-right')
    expect(look(dx, dy, 0)).toBe('right')
  })

  it('lets go once the pointer is well past the edge', () => {
    const angle = (35 * Math.PI) / 180
    expect(look(Math.cos(angle) * 200, Math.sin(angle) * 200, 0)).toBe('down-right')
  })

  it('wraps across the left-hand seam', () => {
    // Just either side of 180 degrees both stay 'left'.
    expect(look(-200, 5, 4)).toBe('left')
    expect(look(-200, -5, 4)).toBe('left')
  })
})

describe('cellPosition', () => {
  it('maps every cell of a 3x3 sheet to a 0/50/100% step', () => {
    expect(DIRECTIONS.map((_, index) => cellPosition(index))).toEqual([
      '0% 0%', '50% 0%', '100% 0%',
      '0% 50%', '50% 50%', '100% 50%',
      '0% 100%', '50% 100%', '100% 100%',
    ])
  })
})

describe('cssUrl', () => {
  it('quotes paths so spaces and brackets survive', () => {
    expect(cssUrl('/a b (1).webp')).toBe('url("/a b (1).webp")')
  })

  it('escapes quotes and backslashes', () => {
    expect(cssUrl('/say "hi"\\.webp')).toBe('url("/say \\"hi\\"\\\\.webp")')
  })
})
