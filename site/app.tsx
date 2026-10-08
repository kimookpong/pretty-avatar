import { useEffect, useMemo, useState } from 'react'
import { Pavatar } from '../src'
import type { Reaction } from '../src'
import { BASE_PATH, CAST, REPO, sheetUrl } from './cast'
import type { CastName } from './cast'
import { initialLang, saveLang, TEXT } from './i18n'
import type { Lang, Text } from './i18n'

function useCopy() {
  const [copied, setCopied] = useState<string | null>(null)
  useEffect(() => {
    if (!copied) return
    const timer = window.setTimeout(() => setCopied(null), 1400)
    return () => window.clearTimeout(timer)
  }, [copied])
  const copy = (id: string, text: string) => {
    navigator.clipboard?.writeText(text).then(() => setCopied(id), () => {})
  }
  return { copied, copy }
}

function Code(props: { id: string; code: string; t: Text; copy: ReturnType<typeof useCopy> }) {
  const { id, code, t, copy } = props
  return (
    <div className="code">
      <pre>
        <code>{code}</code>
      </pre>
      <button type="button" className="copy" onClick={() => copy.copy(id, code)}>
        {copy.copied === id ? t.copied : t.copy}
      </button>
    </div>
  )
}

function GitHubMark() {
  return (
    <svg viewBox="0 0 16 16" aria-hidden="true" width="16" height="16" fill="currentColor">
      <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8Z" />
    </svg>
  )
}

type Settings = {
  size: number
  tracking: boolean
  deadZone: number
  interactive: boolean
  sleepAfter: number
}

const DEFAULTS: Settings = { size: 140, tracking: true, deadZone: 70, interactive: true, sleepAfter: 20000 }

function snippet(name: string, settings: Settings) {
  const props = [`name="${name}"`]
  if (settings.size !== DEFAULTS.size) props.push(`size={${settings.size}}`)
  if (settings.tracking !== DEFAULTS.tracking) props.push(`tracking={${settings.tracking}}`)
  if (settings.deadZone !== DEFAULTS.deadZone) props.push(`deadZone={${settings.deadZone}}`)
  if (settings.interactive !== DEFAULTS.interactive) props.push(`interactive={${settings.interactive}}`)
  if (settings.sleepAfter !== DEFAULTS.sleepAfter) props.push(`sleepAfter={${settings.sleepAfter}}`)
  const tag = props.length > 2 ? `<Pavatar\n  ${props.join('\n  ')}\n/>` : `<Pavatar ${props.join(' ')} />`
  return `import { Pavatar } from 'pretty-avatar'\n\n${tag}`
}

function Hero(props: { picked: CastName; t: Text; onMake: () => void }) {
  const { picked, t, onMake } = props
  const fine = useMemo(() => window.matchMedia?.('(hover: hover) and (pointer: fine)').matches ?? true, [])
  return (
    <header className="hero">
      <Pavatar key={picked} name={picked} basePath={BASE_PATH} size={200} label={picked} className="hero-avatar" />
      <h1>/pretty-avatar</h1>
      <p className="lead">{t.tagline}</p>
      <div className="actions">
        <a className="button primary" href="#cast">
          {t.useOne(CAST.length)}
        </a>
        <button type="button" className="button" onClick={onMake}>
          {t.makeOwn}
        </button>
        <a className="button" href={REPO} target="_blank" rel="noreferrer">
          <GitHubMark /> GitHub
        </a>
      </div>
      <p className="hint">{fine ? t.hint : t.touchHint}</p>
    </header>
  )
}

function Playground(props: { picked: CastName; t: Text; copy: ReturnType<typeof useCopy> }) {
  const { picked, t, copy } = props
  const [settings, setSettings] = useState<Settings>(DEFAULTS)
  const [boop, setBoop] = useState<Reaction | null>(null)
  const set = <K extends keyof Settings>(key: K, value: Settings[K]) => setSettings((s) => ({ ...s, [key]: value }))

  return (
    <section className="section" aria-labelledby="playground">
      <h2 id="playground">{t.playground}</h2>
      <p className="section-lead">{t.playgroundLead}</p>
      <div className="playground">
        <div className="stage">
          <Pavatar
            key={`${picked}-${settings.interactive}`}
            name={picked}
            basePath={BASE_PATH}
            size={settings.size}
            tracking={settings.tracking}
            deadZone={settings.deadZone}
            interactive={settings.interactive}
            sleepAfter={settings.sleepAfter}
            onBoop={setBoop}
            label={picked}
          />
          <span className="boop">
            {t.lastBoop}: <b>{boop ?? '—'}</b>
          </span>
        </div>
        <div className="controls">
          <label>
            <span>
              {t.size} <output>{settings.size}px</output>
            </span>
            <input type="range" min={64} max={240} step={4} value={settings.size}
              onChange={(e) => set('size', Number(e.target.value))} />
          </label>
          <label>
            <span>
              {t.deadZone} <output>{settings.deadZone}px</output>
            </span>
            <input type="range" min={0} max={200} step={5} value={settings.deadZone}
              onChange={(e) => set('deadZone', Number(e.target.value))} />
          </label>
          <label>
            <span>
              {t.sleepAfter}{' '}
              <output>{settings.sleepAfter === 0 ? t.never : `${settings.sleepAfter / 1000}s`}</output>
            </span>
            <input type="range" min={0} max={30000} step={1000} value={settings.sleepAfter}
              onChange={(e) => set('sleepAfter', Number(e.target.value))} />
          </label>
          <div className="toggles">
            <label className="toggle">
              <input type="checkbox" checked={settings.tracking} onChange={(e) => set('tracking', e.target.checked)} />
              {t.tracking}
            </label>
            <label className="toggle">
              <input type="checkbox" checked={settings.interactive}
                onChange={(e) => set('interactive', e.target.checked)} />
              {t.interactive}
            </label>
          </div>
          <Code id="playground" code={snippet(picked, settings)} t={t} copy={copy} />
        </div>
      </div>
    </section>
  )
}

function Cast(props: { picked: CastName; lang: Lang; t: Text; onPick: (name: CastName) => void }) {
  const { picked, lang, t, onPick } = props
  return (
    <section className="section" id="cast" aria-labelledby="cast-title">
      <h2 id="cast-title">{t.cast}</h2>
      <p className="section-lead">{t.castLead}</p>
      <ul className="cast">
        {CAST.map((character) => (
          <li key={character.name} className={character.name === picked ? 'card picked' : 'card'}>
            <Pavatar name={character.name} basePath={BASE_PATH} size={112} label={character.name} />
            <div className="card-name">
              <code>{character.name}</code>
              <span>{character[lang]}</span>
            </div>
            <div className="card-actions">
              <button type="button" className="chip" onClick={() => onPick(character.name)}
                aria-pressed={character.name === picked}>
                {t.use}
              </button>
              <a className="chip" href={sheetUrl(character.name, 'directions')} download
                aria-label={`${t.download}: ${character.name}-directions.webp`} title={`${character.name}-directions.webp`}>
                ↓ 1
              </a>
              <a className="chip" href={sheetUrl(character.name, 'reactions')} download
                aria-label={`${t.download}: ${character.name}-reactions.webp`} title={`${character.name}-reactions.webp`}>
                ↓ 2
              </a>
            </div>
          </li>
        ))}
      </ul>
    </section>
  )
}

function How(props: { picked: CastName; t: Text }) {
  const { picked, t } = props
  return (
    <section className="section" aria-labelledby="how">
      <h2 id="how">{t.how}</h2>
      <p className="section-lead">{t.howLead}</p>
      <div className="sheets">
        <figure>
          <img src={sheetUrl(picked, 'directions')} alt="" width={240} height={240} loading="lazy" />
          <figcaption>{t.directionsSheet}</figcaption>
        </figure>
        <figure>
          <img src={sheetUrl(picked, 'reactions')} alt="" width={240} height={240} loading="lazy" />
          <figcaption>{t.reactionsSheet}</figcaption>
        </figure>
      </div>
      <dl className="details">
        {t.howDetails.map(([title, body]) => (
          <div key={title}>
            <dt>{title}</dt>
            <dd>{body}</dd>
          </div>
        ))}
      </dl>
    </section>
  )
}

function Install(props: { picked: CastName; t: Text; copy: ReturnType<typeof useCopy> }) {
  const { picked, t, copy } = props
  return (
    <section className="section" id="install" aria-labelledby="install-title">
      <h2 id="install-title">{t.install}</h2>
      <Code id="npm" code="npm i pretty-avatar" t={t} copy={copy} />
      <p className="section-lead">{t.installLead}</p>
      <Code id="use" code={`import { Pavatar } from 'pretty-avatar'\n\n<Pavatar name="${picked}" />`} t={t} copy={copy} />

      <h3 className="props-title">{t.props}</h3>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>prop</th>
              <th>default</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {t.propsRows.map(([prop, fallback, note]) => (
              <tr key={prop}>
                <td><code>{prop}</code></td>
                <td><code>{fallback}</code></td>
                <td>{note}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}

function Make(props: { t: Text; copy: ReturnType<typeof useCopy>; lang: Lang }) {
  const { t, copy, lang } = props
  const asks =
    lang === 'th'
      ? '/pretty-avatar ใส่แมว mochi ไว้บนหัวเว็บ\n/pretty-avatar สุนัขชิบะสีส้มใส่ผ้าพันคอสีแดง\n/pretty-avatar วาดให้เหมือนฉัน        [แนบรูป]\n/pretty-avatar นกฮูกสีน้ำตาล สไตล์ pastel'
      : '/pretty-avatar put mochi the cat on my page\n/pretty-avatar a chibi shiba with orange fur and a red scarf\n/pretty-avatar make one that looks like me   [attach a photo]\n/pretty-avatar a brown owl, in the pastel style'
  return (
    <section className="section" id="make" aria-labelledby="make-title">
      <h2 id="make-title">{t.makeTitle}</h2>
      <p className="section-lead">{t.makeLead}</p>
      <Code id="skill" code="npx skills add kimookpong/pretty-avatar --skill pretty-avatar --agent '*' --global --yes" t={t} copy={copy} />
      <p className="section-lead">{t.makeAsk}</p>
      <Code id="ask" code={asks} t={t} copy={copy} />
      <p className="note">{t.makeNote}</p>
      <a className="link" href={`${REPO}/blob/main/skills/pretty-avatar/reference/prompts.md`} target="_blank" rel="noreferrer">
        {t.promptsLink} →
      </a>
    </section>
  )
}

export function App() {
  const [lang, setLang] = useState<Lang>(initialLang)
  const [picked, setPicked] = useState<CastName>('mochi')
  const copy = useCopy()
  const t = TEXT[lang]

  useEffect(() => {
    document.documentElement.lang = lang
    saveLang(lang)
  }, [lang])

  const pick = (name: CastName) => {
    setPicked(name)
    window.scrollTo({ top: 0, behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' })
  }

  const make = () => document.getElementById('make')?.scrollIntoView({ behavior: 'smooth' })

  return (
    <>
      <nav className="topbar">
        <span className="brand">pretty-avatar</span>
        <button type="button" className="lang" onClick={() => setLang(lang === 'th' ? 'en' : 'th')}>
          {t.lang}
        </button>
      </nav>
      <main className="page">
        <Hero picked={picked} t={t} onMake={make} />
        <Playground picked={picked} t={t} copy={copy} />
        <Cast picked={picked} lang={lang} t={t} onPick={pick} />
        <How picked={picked} t={t} />
        <Install picked={picked} t={t} copy={copy} />
        <Make t={t} copy={copy} lang={lang} />
      </main>
      <footer className="footer">
        <p>
          {t.footer}{' '}
          <a href={REPO} target="_blank" rel="noreferrer">
            GitHub
          </a>
        </p>
      </footer>
    </>
  )
}
