/**
 * The task tree agrees with itself.
 *
 * `tasks/README.md` states the update discipline: a status change is three
 * edits applied together -- the task file's frontmatter, the glyph in its
 * phase README's index row, and `last-updated`. The first is what every tool
 * reads; the second is what a person reads. Nothing compared them.
 *
 * On 2026-08-26 `T00.12` -- the task that CLOSES GATE 0 -- carried
 * `status: done` in its frontmatter and `in-progress` in the index, and the
 * phase overview still read "2/12 done" against a phase that was complete.
 * Ported from `karyalay-mail-infra`, where the same check found eight drifted
 * rows on 2026-08-25.
 *
 * Drift in this direction is the quiet kind. A README that overstates progress
 * is corrected by the first person who looks for the evidence; one that
 * understates it is simply believed, and the work is done twice.
 */

import fs from 'node:fs'
import path from 'node:path'

/** The legend in tasks/README.md is the only place these are defined. */
export const GLYPH = {
  todo: '☐',
  'in-progress': '◐',
  blocked: '⛔',
  review: '◎',
  done: '☑',
}

const TASK_FILE = /^T[A-Z0-9]+\.\d+-.*\.md$/

function phases(tasksDir) {
  if (!fs.existsSync(tasksDir)) return []
  return fs
    .readdirSync(tasksDir)
    .filter((e) => fs.statSync(path.join(tasksDir, e)).isDirectory())
    .sort()
}

function frontmatterStatus(file) {
  const m = fs.readFileSync(file, 'utf8').match(/^status:\s*(\S+)\s*$/m)
  if (!m) throw new Error(`${file} has no status in its frontmatter`)
  return m[1]
}

/** The index row for a task id, as its list of cells. */
export function indexRow(readme, id) {
  const line = readme
    .split(/\r?\n/)
    .find((l) => new RegExp(`^\\|\\s*\\[?${id.replace('.', '\\.')}\\b`).test(l))
  if (!line) return null
  return line
    .trim()
    .replace(/^\||\|$/g, '')
    .split('|')
    .map((c) => c.trim())
}

/**
 * This repository writes the status cell as glyph plus word -- `☑ done`. Both
 * halves are checked, because a cell that reads `☑ in-progress` is drift that
 * a glyph-only comparison passes over.
 */
export function auditIndex(root) {
  const tasksDir = path.join(root, 'tasks')
  const drifted = []
  let checked = 0

  for (const phase of phases(tasksDir)) {
    const readmePath = path.join(tasksDir, phase, 'README.md')
    if (!fs.existsSync(readmePath)) continue
    const readme = fs.readFileSync(readmePath, 'utf8')

    for (const file of fs.readdirSync(path.join(tasksDir, phase)).filter((f) => TASK_FILE.test(f)).sort()) {
      const id = file.split('-')[0]
      const status = frontmatterStatus(path.join(tasksDir, phase, file))
      const want = GLYPH[status]
      if (!want) {
        drifted.push(`${phase}: ${id} carries status "${status}", which the legend does not define`)
        continue
      }

      const cells = indexRow(readme, id)
      if (cells === null) {
        drifted.push(`${phase}: ${id} has no row in the phase index`)
        continue
      }
      checked++

      const cell = cells[2]
      const [glyph, ...rest] = cell.split(/\s+/)
      if (glyph !== want) {
        drifted.push(`${phase}: ${id} is "${status}" (${want}) and the index shows "${cell}"`)
      } else if (rest.length && rest.join(' ') !== status) {
        drifted.push(`${phase}: ${id} is "${status}" and the index spells it "${rest.join(' ')}"`)
      }
    }
  }

  return { drifted, checked }
}

/**
 * The glyph map above is a copy, and a copy is a second place for one fact to
 * live. This keeps the copy honest: rename a glyph or add a status in the
 * legend and this fails until the copy moves with it.
 */
export function auditLegend(root) {
  const readme = fs.readFileSync(path.join(root, 'tasks', 'README.md'), 'utf8')
  const problems = []

  for (const [status, glyph] of Object.entries(GLYPH)) {
    if (!new RegExp(`\\|\\s*${glyph}\\s*\\|\\s*\`?${status}\`?\\s*\\|`).test(readme)) {
      problems.push(`the legend in tasks/README.md does not map ${glyph} to \`${status}\``)
    }
  }

  const declared = [...readme.matchAll(/^\|\s*(\S)\s*\|\s*`([a-z-]+)`\s*\|/gm)].map((m) => m[2]).sort()
  const known = Object.keys(GLYPH).sort()
  if (declared.join(',') !== known.join(',')) {
    problems.push(`the legend declares [${declared}] and this check knows [${known}]`)
  }

  return problems
}

/**
 * The control. The corpus is clean once it is swept, and without this the
 * audit above is an assertion about a comparison nobody has watched fail.
 */
export function selfTest() {
  const readme = '| ID | Task | Status |\n| -- | ---- | ------ |\n| T09.01 | [x](T09.01-x.md) | ☐ todo |\n'
  const cells = indexRow(readme, 'T09.01')
  if (!cells || cells[2] !== '☐ todo') throw new Error('indexRow no longer reads a status cell')
  if (cells[2].split(/\s+/)[0] === GLYPH.done) throw new Error('a ☐ row compared equal to done')
  if (indexRow(readme, 'T09.02') !== null) throw new Error('a missing row did not read as missing')
  return 'a drifted row and a missing row are both detected'
}
