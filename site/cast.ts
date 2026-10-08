export const CAST = [
  { name: 'mochi', en: 'cat', th: 'แมว' },
  { name: 'kuma', en: 'bear', th: 'หมี' },
  { name: 'usagi', en: 'bunny', th: 'กระต่าย' },
  { name: 'kaeru', en: 'frog', th: 'กบ' },
  { name: 'pan', en: 'panda', th: 'แพนด้า' },
  { name: 'piyo', en: 'chick', th: 'ลูกเจี๊ยบ' },
] as const

export type CastName = (typeof CAST)[number]['name']

export const BASE_PATH = `${import.meta.env.BASE_URL}avatars`

export const REPO = 'https://github.com/kimookpong/pretty-avatar'

export function sheetUrl(name: string, kind: 'directions' | 'reactions') {
  return `${BASE_PATH}/${name}-${kind}.webp`
}
