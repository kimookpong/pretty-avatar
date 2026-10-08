// Writes skills/pretty-avatar/Pavatar.tsx: the component and its helpers as one
// self-contained file, for projects that copy it in rather than installing the package.
//
//   node scripts/sync-skill.mjs           write it
//   node scripts/sync-skill.mjs --check   fail if it is out of date
import { readFileSync, writeFileSync } from 'node:fs'

const root = new URL('..', import.meta.url)
const read = (path) => readFileSync(new URL(path, root), 'utf8')
const target = new URL('skills/pretty-avatar/Pavatar.tsx', root)

const helpers = read('src/direction.ts')
const component = read('src/pavatar.tsx')
  .replace(/^import .* from '\.\/direction\.js'\n/gm, '')
  .replace(/^'use client'\n\n/, '')

const bundled = `'use client'

// Generated from src/ by scripts/sync-skill.mjs -- edit those, not this.

${component.replace(/^((?:import .*\n)+)/, `$1\n${helpers}\n`)}`

if (process.argv.includes('--check')) {
  let current = ''
  try {
    current = readFileSync(target, 'utf8')
  } catch {}
  if (current !== bundled) {
    console.error('skills/pretty-avatar/Pavatar.tsx is stale. Run: npm run sync:skill')
    process.exit(1)
  }
} else {
  writeFileSync(target, bundled)
}
