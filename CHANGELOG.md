# Changelog

## 0.3.1

- The npm page shows the English README. npm had picked up `README.th.md` instead, so
  the Thai README moves to `docs/README.th.md` on GitHub.
- Quick start follows the demo site's three steps: add the package, put two sheets in
  `public/avatars`, render it.

## 0.3.0

- Back to one way of getting a ready-made character: put its two sheets in
  `public/avatars/` and render `<Pavatar name="…" />`. The README lists all 67 characters
  and the URLs to fetch them from.
- Removes what 0.2.0 added: the `pretty-avatar/characters/*` imports, the `character`
  prop and the `Character` type. 0.2.0 pointed at a `pretty-avatar-collection` package
  that was never published; it is deprecated.
- The package is the component alone again, about 3 kB gzipped.

## 0.1.1

- New README in English and Thai: quick start, the two ways to get a character, a table
  of reactions, the drawing pipeline as a diagram, and an FAQ.
- Redesigned demo site at https://kimookpong.github.io/pretty-avatar/.
- No change to the component or its props.

## 0.1.0

- First release: `<Pavatar>` with `name`/`basePath` or `directions`/`reactions`, `size`,
  `label`, `tracking`, `deadZone`, `interactive`, `sleepAfter` and `onBoop`.
