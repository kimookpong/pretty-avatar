---
name: pretty-avatar
description: Put a cute cursor-tracking avatar on a page with the Pavatar React component from the pretty-avatar package -- a chibi character that turns its head toward the pointer and reacts when clicked. Uses one of the ready-made characters, or draws a new one (with your own image tool, the OpenAI Images API, or from a user's photo), builds its two sprite sheets into aligned atlases and checks they do not jump. Use when the user runs /pretty-avatar, asks for an avatar or mascot that follows the cursor, wants one of the existing characters on their page, or wants a new character drawn.
---

# /pretty-avatar

Works in any coding agent that can run shell commands and edit files. Turns "put the cat on my page" or "draw me as a chibi" into a working `<Pavatar />`.

A character is two 3×3 sprite sheets: nine head directions and nine expressions. The
component moves `background-position` between cells, so there is no per-frame JavaScript
and no animation library. A character is just its two files -- nothing has to register it.

## Creation presets and format

For animal/human categories, a reference gallery style, or a collection request, read
`reference/creation-format.md`. It defines 30 animal and 30 human generation presets,
the request record, sheet order and output paths. `reference/catalog.json` is the
machine-readable catalog; `scripts/catalog.py --list` lists ids without generating images.
Presets require drawing unless their id appears in `reference/ready-collection.md`.
That reference lists generated characters already built and visually reviewed. Check local
assets first; do not assume locally generated files are already deployed remotely.
For a collection, run `scripts/collection.py prepare` to write each character's two
prompts and a resumable manifest without image calls. Generate each PNG with the chosen
image tool, then run `collection.py build --id <preset-id>`. It screens and verifies in
a staging folder before publishing atlases. Inspect direction, identity, expressions
and clipping visually; only then use `--visual-reviewed`. `collection.py status` reports
remaining work. Preserve the source PNGs and manifest locally for resuming.
Use `avatar.py <name> --preset <id>` on the API route, or pass the preset description
into the existing prompts on the built-in image-tool route. User overrides take precedence.
For planning or asset-only requests, stop at the requested deliverable; page integration
is required only when the user asks to put the avatar on a page.

## Which route

- **The user names a ready-made character, or would take one** -- *Use a ready-made one*.
  No Python, no API key. The common case.
- **The user wants something new, or their own likeness** -- *Draw a new one*.

For page-integration requests, both routes end in *Put it on the page*.

## Use a ready-made one

1. **Pick.** `reference/characters.md` lists the original six; `reference/ready-collection.md` lists the verified generated collection. If the user did not name one, pick one
   that suits the site and say which and why.

2. **Fetch its two sheets** into the folder the project serves static files from --
   `public/` for Next, Vite, CRA and Astro, `static/` for SvelteKit:

   ```bash
   mkdir -p public/avatars
   curl -fsSL -o public/avatars/mochi-directions.webp https://kimookpong.github.io/pretty-avatar/avatars/mochi-directions.webp
   curl -fsSL -o public/avatars/mochi-reactions.webp  https://kimookpong.github.io/pretty-avatar/avatars/mochi-reactions.webp
   ```

3. *Put it on the page.*

## Put it on the page

**Install.** Use the package manager the lockfile points at: `npm i pretty-avatar`,
`pnpm add pretty-avatar`, `yarn add pretty-avatar` or `bun add pretty-avatar`. If the
project is React but not package-managed, copy `Pavatar.tsx` from beside this SKILL.md
into it instead -- one file, React only, inline styles. Then import from that file.

**Render:**

```tsx
import { Pavatar } from 'pretty-avatar'

<Pavatar name="mochi" />
```

`name` reads `/avatars/<name>-directions.webp` and `-reactions.webp`. If the sheets live
elsewhere, add `basePath="/static/avatars"`, or pass both paths (or imported images):

```tsx
<Pavatar directions="/img/me-directions.webp" reactions="/img/me-reactions.webp" />
```

Other props, all optional:

| prop | default | |
| --- | --- | --- |
| `size` | `140` | px, square |
| `label` | `'avatar'` | what a screen reader calls it |
| `tracking` | `true` | turn the head toward the pointer |
| `deadZone` | `70` | px around the centre where it looks straight ahead |
| `interactive` | `true` | react to clicks; `false` renders a plain image |
| `sleepAfter` | `20000` | ms without pointer movement before it dozes off; `0` never |
| `onBoop` | | called with the expression shown on each click |
| `className`, `style` | | on the outer element |

The component is marked `'use client'`, so it can be used straight from a Next.js App
Router page.

**Put it where the user asked.** If they did not say: the top of the page -- the header or
hero, beside or above the title -- where a head that follows the cursor reads best. Edit
the real component file, then tell the user what you changed and where.

## Draw a new one

### First, how will you draw?

Two sheets have to be drawn per character. Check in this order:

1. **You have a built-in image tool.** Use it -- *Drawing it yourself* below. Find out
   first whether it can return a transparent background; that decides which prompt you
   send (*Transparency*).
2. **`OPENAI_API_KEY` is set.** Use *Drawing through the API*. This is the route for
   any agent without an image tool of its own -- it only needs a shell and Python.
3. **Neither.** Say plainly that drawing needs an image tool or an `OPENAI_API_KEY`, and
   offer a ready-made character, or the prompts in `reference/prompts.md` for the user to
   paste into a chat app themselves. Do not drive a web UI in a browser instead.

The build needs Python 3 with Pillow, NumPy and SciPy:

```bash
python3 -c "import PIL, numpy, scipy" || pip install -r <skill-dir>/scripts/requirements.txt
```

`<skill-dir>` is the folder holding this SKILL.md; the skill is usually installed outside
the project, so use its full path. Run every command **from the project root**: sheets are
read from `characters/<name>/` and atlases written to `public/avatars/`. Add
`--dest static/avatars` (or wherever the project serves static files) when `public/` is
not it.

### Drawing through the API

One command draws, screens, builds, verifies and retries:

```bash
python3 <skill-dir>/scripts/avatar.py fox --describe "a chibi fox with warm orange fur, a cream muzzle and dark ear tips"
```

- `--style pastel` for another look (see *Styles*).
- `--reference ~/photo.jpg` to draw someone from a photo.
- `--only reactions` to redraw just the expressions sheet.

Needs `pip install openai`. The model is `gpt-image-1`; set `PRETTY_AVATAR_MODEL` to use
another. If the model returns no alpha, the script redraws that sheet on a key colour and
removes it, which costs one more image.

### Drawing it yourself

1. **Directions sheet.** Send the DIRECTIONS prompt from `reference/prompts.md` with the
   description filled in. Save to `characters/<name>/directions.png`.
2. **Expressions sheet.** Send the EXPRESSIONS prompt with the directions sheet attached
   as a reference image. Save to `characters/<name>/reactions.png`.
3. **Build and verify:**

   ```bash
   python3 <skill-dir>/scripts/avatar.py <name> --skip-generate
   ```

4. **Act on what it says.** It either reports the character ready, or names the sheet at
   fault. Redraw that one and run step 3 again. After two failed redraws, change the
   description instead -- by then the art is the problem, not the build.

Run the commands yourself; do not print them for the user to copy.

### Check which way it looks

The scripts measure everything except which way the character faces. Before handing it
over, look at the `left` cell (middle row, first column) of the built directions atlas:
the face must point to the viewer's left. Sheets occasionally come back mirrored; the fix
is in `reference/troubleshooting.md` -- swap the columns, do not redraw.

### Transparency

The sheets must end up as PNGs with a real alpha channel, and **the prompt cannot get you
one**. Transparency is an option on the image call (`background: "transparent"` on the
OpenAI API). Asked in words without it, a model paints a grey-and-white checkerboard
behind the character, which cannot be removed.

- **The tool can return transparency:** turn the option on and use the prompts as written.
- **It cannot:** use the *key colour* variant in `reference/prompts.md`. It asks for a flat
  pure-green background and never mentions transparency. `avatar.py` removes the green on
  its own; to do it by hand: `python3 <skill-dir>/scripts/key.py characters/<name>/directions.png --in-place`.

Never combine the two ("transparent, or green if you can't") -- that still gets the
checkerboard. What the screen step reports:

| alpha | meaning | do |
| --- | --- | --- |
| `ok` | real transparency | nothing |
| `key` | flat key colour | it is removed automatically |
| `checkerboard` | painted checkerboard | redraw with the right prompt for your tool |
| `opaque` | white or a scene behind it | redraw |

### Writing the description

This decides how good the result is, so spend a sentence on it. "fox" gets a worse fox
than "a chibi fox with warm orange fur, a cream muzzle and dark ear tips". Name the
colours and two or three distinguishing features.

Avoid, because each breaks the alignment:

- **Long loose hair over the shoulders** -- tie it back or put it under a hat. It is drawn
  differently on each sheet and the avatar lurches when clicked. The most common failure.
- **Anything wider than the head** -- wings, big hats. They get clipped at cell edges.
- **Held props** -- the framing is head and shoulders only.

### Styles

`colour` (default), `pastel`, `ink`, `watercolour`, `pixel`, `clay`. Only the rendering
changes; framing and proportions are shared, so a style cannot break the alignment. Keep
one style for both sheets of a character.

### Afterwards

Atlases land in `public/avatars/<name>-{directions,reactions}.webp` (or `--dest`). The
source sheets stay in `characters/<name>/` so the character can be rebuilt without
redrawing; tell the user, and let them decide whether to keep them.

When page integration was requested, *Put it on the page* with `<Pavatar name="<name>" />`.

## Going deeper

`reference/troubleshooting.md` explains each check, what each failure looks like, and the
fixes. Read it when a character fails in a way the script's messages do not cover.
