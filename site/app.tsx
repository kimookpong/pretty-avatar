import { useEffect, useRef, useState } from 'react'
import type { CSSProperties, ReactNode, RefObject } from 'react'
import { DIRECTIONS, Pavatar, REACTIONS } from '../src'
import type { Direction, Reaction } from '../src'
import { AGENTS, BASE_PATH, CAST, REPO, sheetUrl, SKILL_COMMAND } from './cast'
import type { CastName, Character } from './cast'
import { initialLang, saveLang, TEXT } from './i18n'
import type { Lang, Text } from './i18n'

const FINE = typeof window !== 'undefined' && window.matchMedia?.('(hover: hover) and (pointer: fine)').matches

/** What a <Pavatar> inside `ref` is showing, read off its data attributes as they change. */
function useAvatarState(ref: RefObject<HTMLElement | null>) {
  const [state, setState] = useState<{ direction: Direction; reaction: Reaction | null }>({
    direction: 'center',
    reaction: null,
  })
  useEffect(() => {
    const root = ref.current
    if (!root) return
    let target: HTMLElement | null = null
    const read = () => {
      if (!target) return
      setState({
        direction: (target.dataset.direction as Direction) ?? 'center',
        reaction: (target.dataset.reaction as Reaction) ?? null,
      })
    }
    const attach = () => {
      target = root.querySelector<HTMLElement>('[data-direction]')
      read()
    }
    attach()
    const observer = new MutationObserver(() => {
      if (!target || !root.contains(target)) attach()
      else read()
    })
    observer.observe(root, { subtree: true, childList: true, attributes: true, attributeFilter: ['data-direction', 'data-reaction'] })
    return () => observer.disconnect()
  }, [ref])
  return state
}

function useCopy() {
  const [copied, setCopied] = useState<string | null>(null)
  useEffect(() => {
    if (!copied) return
    const timer = window.setTimeout(() => setCopied(null), 1400)
    return () => window.clearTimeout(timer)
  }, [copied])
  return {
    copied,
    copy: (id: string, text: string) => navigator.clipboard?.writeText(text).then(() => setCopied(id), () => {}),
  }
}

type Copy = ReturnType<typeof useCopy>

function CopyButton(props: { id: string; text: string; t: Text; copy: Copy }) {
  const { id, text, t, copy } = props
  return (
    <button type="button" className="copy" onClick={() => copy.copy(id, text)}>
      {copy.copied === id ? t.copied : t.copy}
    </button>
  )
}

function Code(props: { id: string; code: string; t: Text; copy: Copy; prompt?: boolean }) {
  const { id, code, t, copy, prompt } = props
  return (
    <div className={prompt ? 'code shell' : 'code'}>
      <pre>
        <code>{code}</code>
      </pre>
      <CopyButton id={id} text={code} t={t} copy={copy} />
    </div>
  )
}

function GitHubMark() {
  return (
    <svg viewBox="0 0 16 16" aria-hidden="true" width="18" height="18" fill="currentColor">
      <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8Z" />
    </svg>
  )
}

function Section(props: { id: string; kicker: string; title: string; lead?: ReactNode; children: ReactNode }) {
  const { id, kicker, title, lead, children } = props
  return (
    <section className="section" id={id} aria-labelledby={`${id}-title`}>
      <p className="kicker">{kicker}</p>
      <h2 id={`${id}-title`}>{title}</h2>
      {lead && <p className="section-lead">{lead}</p>}
      {children}
    </section>
  )
}

function Hero(props: { picked: Character; t: Text; copy: Copy }) {
  const { picked, t, copy } = props
  const [tab, setTab] = useState<'npm' | 'skill'>('npm')
  const stageRef = useRef<HTMLDivElement>(null)
  const { direction, reaction } = useAvatarState(stageRef)
  const command = tab === 'npm' ? 'npm i pretty-avatar' : SKILL_COMMAND
  const moved = direction !== 'center' || reaction

  return (
    <header className="hero">
      <div className="hero-copy">
        <p className="eyebrow">{t.eyebrow}</p>
        <h1>
          {t.title[0]}
          <span className="mark">{t.title[1]}</span>
          <span className="nowrap">{t.title[2]}</span>
        </h1>
        <p className="lead">{t.lead}</p>

        <div className="installer">
          <div className="tabs" role="tablist">
            {(['npm', 'skill'] as const).map((key) => (
              <button key={key} type="button" role="tab" aria-selected={tab === key} className="tab"
                onClick={() => setTab(key)}>
                {t.tabs[key]}
              </button>
            ))}
          </div>
          <div className="command">
            <code>
              <span className="dollar">$</span> {command}
            </code>
            <CopyButton id="hero" text={command} t={t} copy={copy} />
          </div>
        </div>

        <ul className="facts">
          {t.facts.map((fact) => (
            <li key={fact}>{fact}</li>
          ))}
        </ul>
      </div>

      <div className="stage-card" ref={stageRef}>
        <div className="bubble" aria-live="polite">
          {reaction ? (
            <>
              {t.bubble.feeling} <b>{reaction}</b>
            </>
          ) : moved ? (
            <>
              {t.bubble.looking} <b>{direction}</b>
            </>
          ) : FINE ? (
            t.bubble.idle
          ) : (
            t.bubble.touch
          )}
        </div>
        <div className="spotlight">
          <Pavatar key={picked.name} name={picked.name} basePath={BASE_PATH} size={232} label={picked.name} />
        </div>
        <p className="stage-name">
          <code>&lt;Pavatar name="{picked.name}" /&gt;</code>
        </p>
      </div>
    </header>
  )
}

// With ~70 characters on the bench, only load the sheets of the ones near the viewport.
function LazyAvatar(props: { name: CastName; size: number }) {
  const { name, size } = props
  const holder = useRef<HTMLDivElement>(null)
  const [visible, setVisible] = useState(false)
  useEffect(() => {
    if (!holder.current) return
    if (!('IntersectionObserver' in window)) {
      setVisible(true)
      return
    }
    const observer = new IntersectionObserver(([entry]) => setVisible(entry.isIntersecting), { rootMargin: '100px' })
    observer.observe(holder.current)
    return () => observer.disconnect()
  }, [])
  return (
    <div ref={holder} style={{ width: size, height: size }}>
      {visible && <Pavatar name={name} basePath={BASE_PATH} size={size} label={name} interactive={false} />}
    </div>
  )
}

const CATEGORIES = ['all', 'animal', 'human'] as const
type Category = (typeof CATEGORIES)[number]

function ClassPhoto(props: { picked: Character; lang: Lang; t: Text; copy: Copy; onPick: (name: CastName) => void }) {
  const { picked, lang, t, copy, onPick } = props
  const snippet = `<Pavatar name="${picked.name}" />`
  const [category, setCategory] = useState<Category>('all')
  const shown = CAST.filter((character) => category === 'all' || character.category === category)
  return (
    <Section id="cast" kicker="02" title={t.castTitle} lead={t.castLead}>
      <div className="cast-filters" role="group" aria-label={t.castFilter}>
        {CATEGORIES.map((value) => (
          <button key={value} type="button" className="chip" aria-pressed={category === value}
            onClick={() => setCategory(value)}>
            {t.categories[value]} ({CAST.filter((character) => value === 'all' || character.category === value).length})
          </button>
        ))}
      </div>
      <ul className="bench">
        {shown.map((character) => {
          const active = character.name === picked.name
          return (
            <li key={character.name} className={active ? 'seat active' : 'seat'} title={`${character.name} · ${character[lang]}`}>
              <LazyAvatar name={character.name} size={128} />
              <button type="button" className="tag" aria-pressed={active} aria-label={`${t.tryIt}: ${character.name}`}
                onClick={() => {
                  onPick(character.name)
                  document.getElementById('play')?.scrollIntoView()
                }}>
                {t.tryIt}
              </button>
            </li>
          )
        })}
      </ul>

      <div className="picked-bar">
        <span className="picked-label">{t.picked}</span>
        <code className="picked-snippet">{snippet}</code>
        <CopyButton id="picked" text={snippet} t={t} copy={copy} />
        <a className="try-it" href="#play">
          {t.tryIt} <span aria-hidden>→</span>
        </a>
      </div>
    </Section>
  )
}

function SheetGrid(props: { src: string; labels: readonly string[]; active: string | null; caption: string }) {
  const { src, labels, active, caption } = props
  return (
    <figure className="sheet">
      <div className="sheet-grid" style={{ backgroundImage: `url("${src}")` }}>
        {labels.map((label) => (
          <span key={label} className={label === active ? 'cell on' : 'cell'}>
            <small>{label}</small>
          </span>
        ))}
      </div>
      <figcaption>{caption}</figcaption>
    </figure>
  )
}

function UnderTheHood(props: { picked: Character; t: Text }) {
  const { picked, t } = props
  const liveRef = useRef<HTMLDivElement>(null)
  const { direction, reaction } = useAvatarState(liveRef)
  return (
    <Section id="how" kicker="03" title={t.howTitle} lead={t.howLead}>
      <div className="hood">
        <div className="hood-live" ref={liveRef}>
          <Pavatar key={picked.name} name={picked.name} basePath={BASE_PATH} size={168} label={picked.name} />
        </div>
        <SheetGrid src={sheetUrl(picked.name, 'directions')} labels={DIRECTIONS}
          active={reaction ? null : direction} caption={t.directionsSheet} />
        <SheetGrid src={sheetUrl(picked.name, 'reactions')} labels={REACTIONS}
          active={reaction} caption={t.reactionsSheet} />
      </div>
      <ol className="steps">
        {t.steps.map(([title, body], index) => (
          <li key={title}>
            <span className="step-number">{index + 1}</span>
            <h3>{title}</h3>
            <p>{body}</p>
          </li>
        ))}
      </ol>
    </Section>
  )
}

type Settings = { size: number; tracking: boolean; deadZone: number; interactive: boolean; sleepAfter: number }
const DEFAULTS: Settings = { size: 140, tracking: true, deadZone: 70, interactive: true, sleepAfter: 20000 }

function snippet(name: string, settings: Settings) {
  const props = [`name="${name}"`]
  for (const key of ['size', 'tracking', 'deadZone', 'interactive', 'sleepAfter'] as const) {
    if (settings[key] !== DEFAULTS[key]) props.push(`${key}={${settings[key]}}`)
  }
  const tag = props.length > 2 ? `<Pavatar\n  ${props.join('\n  ')}\n/>` : `<Pavatar ${props.join(' ')} />`
  return `import { Pavatar } from 'pretty-avatar'\n\n${tag}`
}

function Playground(props: { picked: Character; t: Text; copy: Copy }) {
  const { picked, t, copy } = props
  const [settings, setSettings] = useState<Settings>(DEFAULTS)
  const [boop, setBoop] = useState<Reaction | null>(null)
  const set = <K extends keyof Settings>(key: K, value: Settings[K]) => setSettings((s) => ({ ...s, [key]: value }))

  return (
    <Section id="play" kicker="01" title={t.playTitle} lead={t.playLead}>
      <div className="playground">
        <div className="panel">
          <label className="slider">
            <span>size</span>
            <input type="range" min={64} max={240} step={4} value={settings.size}
              onChange={(e) => set('size', Number(e.target.value))} />
            <output>{settings.size}px</output>
          </label>
          <label className="slider">
            <span>deadZone</span>
            <input type="range" min={0} max={200} step={5} value={settings.deadZone}
              onChange={(e) => set('deadZone', Number(e.target.value))} />
            <output>{settings.deadZone}px</output>
          </label>
          <label className="slider">
            <span>sleepAfter</span>
            <input type="range" min={0} max={30000} step={1000} value={settings.sleepAfter}
              onChange={(e) => set('sleepAfter', Number(e.target.value))} />
            <output>{settings.sleepAfter === 0 ? t.never : `${settings.sleepAfter / 1000}s`}</output>
          </label>
          <div className="switches">
            {(['tracking', 'interactive'] as const).map((key) => (
              <label key={key} className="switch">
                <input type="checkbox" role="switch" checked={settings[key]} onChange={(e) => set(key, e.target.checked)} />
                <span className="knob" aria-hidden />
                {key}
              </label>
            ))}
          </div>
          <Code id="playground" code={snippet(picked.name, settings)} t={t} copy={copy} />
          <div className="downloads">
            <span>{t.download}</span>
            {(['directions', 'reactions'] as const).map((kind) => (
              <a key={kind} className="download" href={sheetUrl(picked.name, kind)} download>
                <span aria-hidden>↓</span> {picked.name}-{kind}.webp
              </a>
            ))}
          </div>
        </div>
        <div className="play-stage">
          <Pavatar key={`${picked.name}-${settings.interactive}`} name={picked.name} basePath={BASE_PATH}
            size={settings.size} tracking={settings.tracking} deadZone={settings.deadZone}
            interactive={settings.interactive} sleepAfter={settings.sleepAfter} onBoop={setBoop} label={picked.name} />
          {settings.deadZone > 0 && settings.tracking && (
            <span className="deadzone" aria-hidden style={{ width: settings.deadZone * 2, height: settings.deadZone * 2 }} />
          )}
          <span className="boop">
            {t.lastBoop}: <b>{boop ?? '—'}</b>
          </span>
        </div>
      </div>
    </Section>
  )
}

function Install(props: { picked: Character; t: Text; copy: Copy }) {
  const { picked, t, copy } = props
  const codes = [
    'npm i pretty-avatar',
    `public/avatars/${picked.name}-directions.webp\npublic/avatars/${picked.name}-reactions.webp`,
    `import { Pavatar } from 'pretty-avatar'\n\nexport function Header() {\n  return <Pavatar name="${picked.name}" />\n}`,
  ]
  return (
    <Section id="install" kicker="04" title={t.installTitle}>
      <ol className="install-steps">
        {t.installSteps.map(([title, note], index) => (
          <li key={title}>
            <h3>{title}</h3>
            {note && <p>{note}</p>}
            <Code id={`install-${index}`} code={codes[index]} t={t} copy={copy} />
          </li>
        ))}
      </ol>

      <h3 className="props-title">{t.propsTitle}</h3>
      <dl className="props">
        {t.props.map(([prop, fallback, note]) => (
          <div key={prop} className="prop">
            <dt>
              <code>{prop}</code>
              {fallback !== '—' && <span className="default">{fallback}</span>}
            </dt>
            <dd>{note}</dd>
          </div>
        ))}
      </dl>
    </Section>
  )
}

function Make(props: { t: Text; copy: Copy }) {
  const { t, copy } = props
  return (
    <Section id="make" kicker="05" title={t.makeTitle} lead={t.makeLead}>
      <div className="make">
        <div>
          <Code id="skill" code={SKILL_COMMAND} t={t} copy={copy} prompt />
          <p className="works-label">{t.worksWith}</p>
          <ul className="agents">
            {AGENTS.map((agent) => (
              <li key={agent}>{agent}</li>
            ))}
            <li className="more">{t.andMore}</li>
          </ul>
        </div>
        <div className="terminal" aria-label={t.makeAsk}>
          <div className="terminal-bar" aria-hidden>
            <i />
            <i />
            <i />
          </div>
          <p className="terminal-label">{t.makeAsk}</p>
          {t.asks.map((ask) => (
            <p key={ask} className="terminal-line">
              <span className="caret">›</span> {ask}
            </p>
          ))}
        </div>
      </div>
      <p className="note">{t.makeNote}</p>
      <a className="link" href={`${REPO}/blob/main/skills/pretty-avatar/reference/prompts.md`} target="_blank" rel="noreferrer">
        {t.prompts} →
      </a>
    </Section>
  )
}

export function App() {
  const [lang, setLang] = useState<Lang>(initialLang)
  const [pickedName, setPickedName] = useState<CastName>('mochi')
  const copy = useCopy()
  const t = TEXT[lang]
  const picked = CAST.find((c) => c.name === pickedName) ?? CAST[0]

  useEffect(() => {
    document.documentElement.lang = lang
    saveLang(lang)
  }, [lang])

  const theme = { '--accent': picked.accent, '--accent-ink': picked.ink } as CSSProperties

  return (
    <div className="app" style={theme}>
      <nav className="topbar">
        <a className="brand" href="#top">
          <Pavatar name={picked.name} basePath={BASE_PATH} size={36} label={picked.name} interactive={false} sleepAfter={0} />
          pretty-avatar
        </a>
        <div className="nav-links">
          <a href="#play">{t.nav.play}</a>
          <a href="#cast">{t.nav.cast}</a>
          <a href="#how">{t.nav.how}</a>
          <a href="#install">{t.nav.install}</a>
        </div>
        <div className="nav-actions">
          <a className="icon-link" href={REPO} target="_blank" rel="noreferrer" aria-label="GitHub">
            <GitHubMark />
          </a>
          <button type="button" className="lang" onClick={() => setLang(lang === 'th' ? 'en' : 'th')}
            aria-label={lang === 'th' ? 'Switch to English' : 'เปลี่ยนเป็นภาษาไทย'}>
            {t.lang}
          </button>
        </div>
      </nav>
      <main className="page" id="top">
        <Hero picked={picked} t={t} copy={copy} />
        <Playground picked={picked} t={t} copy={copy} />
        <ClassPhoto picked={picked} lang={lang} t={t} copy={copy} onPick={setPickedName} />
        <UnderTheHood picked={picked} t={t} />
        <Install picked={picked} t={t} copy={copy} />
        <Make t={t} copy={copy} />
      </main>
      <div className="footer-meadow">
        <footer className="footer">
          <span>{t.footer}</span>
          <a href={REPO} target="_blank" rel="noreferrer">
            github.com/kimookpong/pretty-avatar
          </a>
        </footer>
      </div>
    </div>
  )
}
