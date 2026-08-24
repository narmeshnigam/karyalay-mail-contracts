/**
 * The check ADR-KEM-012 said was worth writing and did not write.
 *
 * ADR-KEM-009 deferred AI-04..AI-09 and AI-12 to `v0.2.0`. `v0.2.0`, `v0.3.0`
 * and `v0.4.0` were tagged and pushed with none of them present, and nothing
 * failed, because nothing compared a deferral's target tag against the version
 * the repository had actually reached. Ten Repo 4 tasks stayed blocked for six
 * days on a decision that had already been taken.
 *
 *   "A deferral needs an owner, not just a target tag. [...] the target tag
 *    passed three times and nothing failed, because no check compares a
 *    deferral's target against the current version."
 *                                   -- ADR-KEM-012, "The process lesson"
 *
 * This module is that comparison. It reads docs/registers/deferral-register-v1.yaml
 * and answers four questions:
 *
 *   1. Has any deferral's target tag been reached or passed while the deferral
 *      is still open?  (the ADR-KEM-009 failure, exactly)
 *   2. Does a deferral recorded as honoured actually have the artifact it
 *      claims -- the operation resolvable in the document, the schema present
 *      with the $id it names?  Status is not capability (START-HERE 6.4): a
 *      register row saying HONOURED is worth nothing on its own.
 *   3. Is every open deferral tracked at all -- a target, and either an owner
 *      or a place in the ownerless ratchet?
 *   4. Has the number of ownerless deferrals grown past its committed baseline?
 *
 * Deliberate limit, stated rather than hidden: only `target.tag` is comparable
 * against a version. Deferrals targeted at a wave or a gate are surfaced on
 * every run as UNMATURABLE and held by the ownership ratchet instead. Turning
 * one into a tag target is what makes it enforceable, and that is a decision,
 * not a tooling change.
 */

import fs from 'node:fs'
import path from 'node:path'
import YAML from 'yaml'

export const REGISTER_PATH = 'docs/registers/deferral-register-v1.yaml'

const OPEN_STATUSES = new Set(['OPEN'])
const HONOURED_STATUSES = new Set(['HONOURED', 'MISSED_THEN_HONOURED'])
export const VALID_STATUSES = new Set([...OPEN_STATUSES, ...HONOURED_STATUSES, 'WITHDRAWN'])

/** Numeric semver compare; tolerates a leading `v`. Returns <0, 0 or >0. */
export function compareVersions(a, b) {
  const parse = (v) => String(v).replace(/^v/, '').split('.').map((n) => {
    const parsed = Number(n)
    if (!Number.isInteger(parsed) || parsed < 0) throw new Error(`not a version: ${v}`)
    return parsed
  })
  const [x, y] = [parse(a), parse(b)]
  for (let i = 0; i < Math.max(x.length, y.length); i++) {
    const d = (x[i] ?? 0) - (y[i] ?? 0)
    if (d !== 0) return d
  }
  return 0
}

export function loadRegister(root, rel = REGISTER_PATH) {
  return YAML.parse(fs.readFileSync(path.join(root, rel), 'utf8'))
}

/**
 * Every structural complaint about the register itself, so a malformed row
 * cannot slip past the maturity check by being unreadable.
 */
export function auditShape(register) {
  const problems = []
  const seen = new Set()
  for (const d of register.deferrals || []) {
    const at = d.id ? `deferral ${d.id}` : 'a deferral with no id'
    if (!d.id) { problems.push(`${at} has no id`); continue }
    if (seen.has(d.id)) problems.push(`${at} is listed twice`)
    seen.add(d.id)
    if (!d.title) problems.push(`${at} has no title`)
    if (!d.deferred_by) problems.push(`${at} does not say which decision deferred it`)
    if (!VALID_STATUSES.has(d.status)) problems.push(`${at} has status ${d.status ?? '(none)'}, which is not one of ${[...VALID_STATUSES].join(', ')}`)
    const targets = ['tag', 'wave', 'gate'].filter((k) => d.target && d.target[k] != null)
    if (targets.length === 0) {
      problems.push(`${at} names no target at all -- a deferral with no target can never mature and can never be caught, which is the ADR-KEM-009 failure with the tag removed`)
    } else if (targets.length > 1) {
      problems.push(`${at} names ${targets.length} targets (${targets.join(', ')}); one deferral has one target or the maturity rule is ambiguous`)
    }
    if (HONOURED_STATUSES.has(d.status)) {
      if (!d.honoured_in) problems.push(`${at} is ${d.status} and does not say which tag honoured it`)
      if (!Array.isArray(d.satisfied_by) || d.satisfied_by.length === 0) {
        problems.push(`${at} is ${d.status} and names no artifact -- "honoured" with nothing to point at is a status, not a capability`)
      }
    }
  }
  return problems
}

/**
 * Question 1, and the reason this file exists. An open deferral whose target
 * tag the repository has reached or passed.
 */
export function auditMaturity(register, currentVersion) {
  const problems = []
  for (const d of register.deferrals || []) {
    const tag = d.target?.tag
    if (!tag) continue
    if (OPEN_STATUSES.has(d.status) && compareVersions(tag, currentVersion) <= 0) {
      problems.push(
        `${d.id} was deferred to ${tag} by ${d.deferred_by} on ${d.deferred_on ?? 'an unrecorded date'}, ` +
        `this repository is at v${currentVersion}, and it is still ${d.status}. ` +
        `The target has been reached or passed and the deferred thing does not exist. ` +
        `Owner: ${d.decision_owner ?? 'nobody'}; owning task: ${d.owning_task ?? 'none'}.`
      )
    }
    // A deferral cannot have been honoured in a tag that does not exist yet.
    if (d.honoured_in && compareVersions(d.honoured_in, currentVersion) > 0) {
      problems.push(`${d.id} claims it was honoured in ${d.honoured_in}, which is ahead of v${currentVersion}`)
    }
  }
  return problems
}

/**
 * Question 3 and 4. An open deferral must be tracked by somebody, and the
 * number of untracked ones may only fall.
 */
export function auditOwnership(register) {
  const problems = []
  const unassigned = []
  for (const d of register.deferrals || []) {
    if (!OPEN_STATUSES.has(d.status)) continue
    if (!d.decision_owner) {
      problems.push(`${d.id} is open and has no decision_owner field at all -- write UNASSIGNED if that is the truth, so it is counted`)
    } else if (d.decision_owner === 'UNASSIGNED') {
      unassigned.push(d.id)
    } else if (!d.owning_task) {
      problems.push(`${d.id} names ${d.decision_owner} as its owner and no task that raises it; that is the shape ADR-KEM-009 closed a task without creating`)
    }
  }
  const baseline = register.unassigned_owner_baseline
  if (typeof baseline !== 'number') {
    problems.push('the register declares no unassigned_owner_baseline, so ownerless deferrals are not ratcheted')
  } else if (unassigned.length > baseline) {
    problems.push(
      `${unassigned.length} deferrals have no decision owner (${unassigned.join(', ')}) against a baseline of ${baseline}. ` +
      `The baseline is a ratchet: assign an owner, or lower it -- do not raise it.`
    )
  } else if (unassigned.length < baseline) {
    problems.push(`only ${unassigned.length} deferrals are ownerless against a baseline of ${baseline}; lower the baseline to ${unassigned.length} so the ratchet keeps its teeth`)
  }
  return { problems, unassigned }
}

/**
 * Question 2. Resolve every claimed artifact for real: the operationId must be
 * present in the named OpenAPI document, the schema file must exist and carry
 * the $id it declares. A path that exists is not an operation that is served.
 */
export function auditArtifacts(register, root) {
  const problems = []
  let resolved = 0
  const docCache = new Map()
  const loadDoc = (rel) => {
    if (!docCache.has(rel)) {
      const full = path.join(root, rel)
      if (!fs.existsSync(full)) { docCache.set(rel, null) }
      else docCache.set(rel, YAML.parse(fs.readFileSync(full, 'utf8')))
    }
    return docCache.get(rel)
  }

  for (const d of register.deferrals || []) {
    if (!HONOURED_STATUSES.has(d.status)) continue
    for (const artifact of d.satisfied_by || []) {
      if (artifact.document) {
        const doc = loadDoc(artifact.document)
        if (!doc) { problems.push(`${d.id} claims ${artifact.document}, which does not exist`); continue }
        const ids = new Set()
        for (const item of Object.values(doc.paths || {})) {
          for (const [method, op] of Object.entries(item || {})) {
            if (op && typeof op === 'object' && op.operationId) ids.add(op.operationId)
            void method
          }
        }
        if (!ids.has(artifact.operation_id)) {
          problems.push(`${d.id} claims ${artifact.operation_id} in ${artifact.document}; the document defines no such operation`)
        } else resolved++
      } else if (artifact.schema) {
        const full = path.join(root, artifact.schema)
        if (!fs.existsSync(full)) { problems.push(`${d.id} claims ${artifact.schema}, which does not exist`); continue }
        const schema = JSON.parse(fs.readFileSync(full, 'utf8'))
        if (artifact.schema_id && schema.$id !== artifact.schema_id) {
          problems.push(`${d.id} claims ${artifact.schema} carries $id ${artifact.schema_id}; it carries ${schema.$id ?? '(none)'}`)
        } else resolved++
      } else {
        problems.push(`${d.id} names an artifact that is neither a document+operation_id nor a schema: ${JSON.stringify(artifact)}`)
      }
    }
  }
  return { problems, resolved }
}

/** Deferrals no version comparison can ever mature. Printed, never silent. */
export function unmaturable(register) {
  return (register.deferrals || [])
    .filter((d) => OPEN_STATUSES.has(d.status) && !d.target?.tag)
    .map((d) => `${d.id}->${d.target?.wave != null ? `wave ${d.target.wave}` : `gate ${d.target?.gate}`}`)
}
