/**
 * Checks over the machine-readable delta register.
 *
 * Three repositories each keep a delta register and all three are prose tables
 * buried in a 4,000-line specification, which is why a delta's disposition,
 * target tag and owner could not be checked by anything. ADR-KEM-012 named
 * that as the gap its own missing check belonged with, and ADR-OPS-024 hit the
 * same gap from the other side -- it could not machine-check which acceptance
 * scenario a phase actually owns, for the same reason.
 *
 * docs/registers/delta-register-v1.yaml is the projection. These checks are
 * what make it worth having:
 *
 *   - it validates against its own schema, so a disposition carries the fields
 *     that disposition means (RESOLVED needs an artifact, OPEN needs evidence
 *     of absence, PARTIAL needs a list of what is missing, DEFERRED needs a
 *     row in the deferral register)
 *   - the row count matches what the appendix declares, so this projection
 *     cannot drop a row quietly -- which is exactly how ADR-KEM-011's session
 *     bootstrap went unregistered
 *   - every claimed artifact resolves for real
 *   - every DEFERRED row is in the deferral register and every deferral-register
 *     row is a delta, so the two cannot drift apart
 *   - every id referenced by `related` exists
 *   - every ADR-KEM-nnn this register names has a file AND a decision-register
 *     row, so a delta cannot point at a decision that was never written down
 *
 * The appendices remain the authority. Where this register and an appendix
 * disagree, the appendix wins under Master Contract 0.3 and this file is the
 * thing to fix.
 */

import fs from 'node:fs'
import path from 'node:path'
import YAML from 'yaml'

export const REGISTER_PATH = 'docs/registers/delta-register-v1.yaml'
export const SCHEMA_PATH = 'docs/registers/delta-register-v1.schema.json'

const RESOLVED_LIKE = new Set(['RESOLVED', 'CANONICAL', 'CONFIRMED', 'PARTIAL'])

export function loadRegister(root, rel = REGISTER_PATH) {
  return YAML.parse(fs.readFileSync(path.join(root, rel), 'utf8'))
}

export function allDeltas(register) {
  return (register.sources || []).flatMap((s) => (s.deltas || []).map((d) => ({ ...d, _source: s.id })))
}

/** The projection must hold as many appendix rows as the appendix declares. */
export function auditRowCounts(register) {
  const problems = []
  const counts = []
  for (const source of register.sources || []) {
    const inAppendix = (source.deltas || []).filter((d) => d.in_appendix !== false)
    if (inAppendix.length !== source.declared_row_count) {
      problems.push(
        `${source.id} declares ${source.declared_row_count} rows in ${source.appendix} and this register holds ${inAppendix.length}. ` +
        `A projection that can lose a row silently is the defect ADR-KEM-011 found in Appendix N itself.`
      )
    }
    counts.push(`${source.id}:${inAppendix.length}`)
  }
  return { problems, counts }
}

/**
 * Where the appendix source file is on disk, cross-check the ids against it.
 * CI for this repository clones this repository alone, so this check usually
 * runs in the weaker mode -- and says which mode it ran in rather than
 * reporting a pass that inspected nothing.
 */
export function auditAgainstAppendices(register, siblingRoot) {
  const problems = []
  const checked = []
  for (const source of register.sources || []) {
    const full = path.join(siblingRoot, source.repository, source.path)
    if (!fs.existsSync(full)) { checked.push(`${source.id}:absent`); continue }
    const text = fs.readFileSync(full, 'utf8')
    const ids = (source.deltas || []).filter((d) => d.in_appendix !== false && /^(AI|D)-\d+$/.test(d.id)).map((d) => d.id)
    if (ids.length === 0) { checked.push(`${source.id}:no-id-column`); continue }
    const missing = ids.filter((id) => !text.includes(id))
    if (missing.length) problems.push(`${source.id}: ${missing.join(', ')} appear in this register and not in ${source.path}`)
    checked.push(`${source.id}:${ids.length} ids matched`)
  }
  return { problems, checked }
}

/** Every claimed artifact resolved for real. Status is not capability. */
export function auditArtifacts(register, root) {
  const problems = []
  let resolved = 0
  const cache = new Map()
  const loadDoc = (rel) => {
    if (!cache.has(rel)) {
      const full = path.join(root, rel)
      cache.set(rel, fs.existsSync(full) ? YAML.parse(fs.readFileSync(full, 'utf8')) : null)
    }
    return cache.get(rel)
  }

  for (const d of allDeltas(register)) {
    if (!RESOLVED_LIKE.has(d.disposition)) continue
    for (const artifact of d.satisfied_by || []) {
      if (artifact.document) {
        const doc = loadDoc(artifact.document)
        if (!doc) { problems.push(`${d.id} claims ${artifact.document}, which does not exist`); continue }
        let found = null
        for (const item of Object.values(doc.paths || {})) {
          for (const op of Object.values(item || {})) {
            if (op && typeof op === 'object' && op.operationId === artifact.operation_id) found = op
          }
        }
        if (!found) { problems.push(`${d.id} claims ${artifact.operation_id} in ${artifact.document}; no such operation`); continue }
        // If the row also names a catalog id, the document must agree with it.
        if (artifact.catalog_id && found['x-karyalay-catalog-id'] && found['x-karyalay-catalog-id'] !== artifact.catalog_id) {
          problems.push(`${d.id} maps ${artifact.operation_id} to ${artifact.catalog_id}; the document says ${found['x-karyalay-catalog-id']}`)
          continue
        }
        resolved++
      } else if (artifact.schema) {
        const full = path.join(root, artifact.schema)
        if (!fs.existsSync(full)) { problems.push(`${d.id} claims ${artifact.schema}, which does not exist`); continue }
        const schema = JSON.parse(fs.readFileSync(full, 'utf8'))
        if (schema.$id !== artifact.schema_id) { problems.push(`${d.id} claims ${artifact.schema} carries $id ${artifact.schema_id}; it carries ${schema.$id ?? '(none)'}`); continue }
        resolved++
      } else if (artifact.correlation_id) {
        const doc = loadDoc(artifact.file)
        if (!doc) { problems.push(`${d.id} claims ${artifact.file}, which does not exist`); continue }
        const ids = (doc.correlation_identifiers || doc.correlation || []).map?.((c) => c.id) || []
        if (!ids.includes(artifact.correlation_id)) { problems.push(`${d.id} claims correlation identifier ${artifact.correlation_id} in ${artifact.file}; it defines ${ids.join(', ') || 'none'}`); continue }
        resolved++
      } else if (artifact.file) {
        const full = path.join(root, artifact.file)
        if (!fs.existsSync(full) || fs.statSync(full).size === 0) { problems.push(`${d.id} claims ${artifact.file}, which does not exist or is empty`); continue }
        resolved++
      }
    }
  }
  return { problems, resolved }
}

/** The two registers must describe the same set of deferrals, both ways. */
export function auditDeferralLinkage(register, deferralRegister) {
  const problems = []
  const deferralIds = new Set((deferralRegister.deferrals || []).map((d) => d.id))
  const deltas = allDeltas(register)

  for (const d of deltas) {
    if (d.disposition !== 'DEFERRED') continue
    if (!deferralIds.has(d.deferral_register_entry)) {
      problems.push(`${d.id} is DEFERRED and points at deferral-register entry ${d.deferral_register_entry ?? '(none)'}, which does not exist -- so its target is enforced by nothing`)
    }
  }

  // The inverse. A deferral that is not a delta is either a delta this
  // projection lost or a deferral that is about something else; both need
  // saying, so the deferral register carries an explicit escape.
  const deltaIds = new Set(deltas.map((d) => d.id))
  const NON_DELTA = new Set(['OPEN-002', 'KEM-003-FENCING'])
  for (const d of deferralRegister.deferrals || []) {
    if (NON_DELTA.has(d.id)) continue
    if (!deltaIds.has(d.id)) {
      problems.push(`deferral ${d.id} has no row in the delta register; either it is a delta this projection lost, or it belongs on the non-delta list in tools/validate/deltas.mjs with a reason`)
    }
  }
  return problems
}

/** No delta may point at an id that does not exist. */
export function auditCrossReferences(register) {
  const problems = []
  const ids = new Set(allDeltas(register).map((d) => d.id))
  let counted = 0
  for (const d of allDeltas(register)) {
    for (const ref of d.related || []) {
      counted++
      if (!ids.has(ref)) problems.push(`${d.id} relates to ${ref}, which is in no source's register`)
    }
  }
  const seen = new Set()
  for (const d of allDeltas(register)) {
    if (seen.has(d.id)) problems.push(`${d.id} is listed twice`)
    seen.add(d.id)
  }
  return { problems, counted }
}

/** What the register says about the programme, printed on every run. */
export function summarise(register) {
  const tally = {}
  for (const d of allDeltas(register)) tally[d.disposition] = (tally[d.disposition] || 0) + 1
  return Object.entries(tally).sort().map(([k, v]) => `${k} ${v}`).join(', ')
}

/**
 * Every ADR this register names must exist. An `open_defects[].ref` of null is
 * a finding recorded on purpose -- a known defect with no ADR raised -- and is
 * left alone; a ref that names an ADR-KEM id which has no file is a dangling
 * pointer to a decision nobody took.
 */
export function auditAdrReferences(register, root) {
  const problems = []
  const decisionRegister = fs.readFileSync(path.join(root, 'docs/adr/DECISION-REGISTER.md'), 'utf8')
  const adrFiles = fs.readdirSync(path.join(root, 'docs/adr'))
  let counted = 0
  let unraised = 0

  const checkRef = (where, ref) => {
    if (ref == null) return
    if (!/^ADR-KEM-\d+$/.test(ref)) return // external ADRs live in sibling repos
    counted++
    if (!adrFiles.some((f) => f.startsWith(ref + '-'))) problems.push(`${where} names ${ref}, which has no file in docs/adr/`)
    if (!decisionRegister.includes(ref)) problems.push(`${where} names ${ref}, which has no row in DECISION-REGISTER.md`)
  }

  for (const d of allDeltas(register)) {
    checkRef(d.id, d.deferred_by)
    checkRef(d.id, d.resolved_by)
    for (const defect of d.open_defects || []) {
      if (defect.ref == null) unraised++
      checkRef(`${d.id} open defect`, defect.ref)
    }
  }
  return { problems, counted, unraised }
}
