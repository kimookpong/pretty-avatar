import { GENERATED_CAST } from './generated-cast'

// `accent` is the character's own shirt colour; the whole page takes it on when the
// character is picked. `ink` is a darker shade of it that passes contrast on the paper.
const SIGNED = [
  { name: 'mochi', category: 'animal', en: 'cat', th: 'แมว', accent: '#5aa7b4', ink: '#2f6f7a' },
  { name: 'kuma', category: 'animal', en: 'bear', th: 'หมี', accent: '#e0a92e', ink: '#8a5f0c' },
  { name: 'usagi', category: 'animal', en: 'bunny', th: 'กระต่าย', accent: '#9a82cf', ink: '#5f4a99' },
  { name: 'kaeru', category: 'animal', en: 'frog', th: 'กบ', accent: '#e07070', ink: '#a23d3d' },
  { name: 'pan', category: 'animal', en: 'panda', th: 'แพนด้า', accent: '#6fb27a', ink: '#3b7a47' },
  { name: 'piyo', category: 'animal', en: 'chick', th: 'ลูกเจี๊ยบ', accent: '#6d9be0', ink: '#2f5fa8' },
] as const

// Characters without a hand-picked colour borrow one from the six above, in turn.
const UNSIGNED = [
  { name: 'hakim', category: 'human', en: 'Hakim', th: 'ฮาคิม' },
  { name: 'person-robot', category: 'human', en: 'robot', th: 'หุ่นยนต์' },
  ...GENERATED_CAST,
] as const

type Signed = (typeof SIGNED)[number]
type Unsigned = (typeof UNSIGNED)[number]

export type Character = {
  name: Signed['name'] | Unsigned['name']
  category: 'animal' | 'human'
  en: string
  th: string
  accent: string
  ink: string
}
export type CastName = Character['name']

export const CAST: readonly Character[] = [
  ...SIGNED,
  ...UNSIGNED.map((character, index) => {
    const { accent, ink } = SIGNED[index % SIGNED.length]
    return { ...character, accent, ink }
  }),
]

export const BASE_PATH = `${import.meta.env.BASE_URL}avatars`

export const REPO = 'https://github.com/kimookpong/pretty-avatar'

export const SKILL_COMMAND = "npx skills add kimookpong/pretty-avatar --skill pretty-avatar --agent '*' --global --yes"

// Agents the skills CLI was seen installing into; it supports ~80 in all.
export const AGENTS = ['Claude Code', 'Codex', 'Windsurf', 'Cline', 'Roo Code', 'Kiro', 'Qwen Code', 'Goose', 'Amp', 'Continue']

export function sheetUrl(name: string, kind: 'directions' | 'reactions') {
  return `${BASE_PATH}/${name}-${kind}.webp`
}
