#!/usr/bin/env node
/**
 * T00.09 — the contract validation harness.
 *
 * Runs every check that can fail without a human reading anything:
 *
 *   1. every YAML and JSON artifact parses
 *   2. every artifact validates against its schema
 *   3. every JSON Schema compiles as draft 2020-12
 *   4. every event payload composes with the envelope and round-trips a sample
 *   5. every auth example validates against claims-v1, and a bad one is rejected
 *   6. cross-references resolve: error codes, permissions, roles, record kinds
 *   7. the OpenAPI documents reconcile 1:1 with Appendix C via the C-number map
 *   8. no OpenAPI document names an error code the catalog does not define
 *   9. no deferral's target tag has passed with the deferred thing absent
 *  10. the delta register projects all three appendices and every claim resolves
 *  11. every task's frontmatter status matches the glyph in its phase index
 *
 * Exit code is the number of failures, capped at 250.
 */

import fs from 'node:fs'
import path from 'node:path'
import process from 'node:process'
import YAML from 'yaml'
import Ajv2020 from 'ajv/dist/2020.js'
import addFormats from 'ajv-formats'
import * as deferrals from './deferrals.mjs'
import * as deltas from './deltas.mjs'
import * as taskindex from './taskindex.mjs'

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..', '..')
const failures = []
let checks = 0

function check(label, fn) {
  checks++
  try {
    const detail = fn()
    console.log(`PASS ${label}${detail ? ' -- ' + detail : ''}`)
  } catch (err) {
    failures.push({ label, message: err.message })
    console.log(`FAIL ${label}\n     ${err.message.replace(/\n/g, '\n     ')}`)
  }
}

const read = (rel) => fs.readFileSync(path.join(ROOT, rel), 'utf8')
const loadYaml = (rel) => YAML.parse(read(rel))
const loadJson = (rel) => JSON.parse(read(rel))

function listFiles(dir, ext) {
  const full = path.join(ROOT, dir)
  if (!fs.existsSync(full)) return []
  return fs.readdirSync(full).filter((f) => f.endsWith(ext)).sort().map((f) => path.join(dir, f))
}

function ajv() {
  const instance = new Ajv2020({ strict: false, allErrors: true, allowUnionTypes: true })
  addFormats(instance)
  // JSON Schema defines idn-email; ajv-formats does not ship it. Master 6.5
  // requires SMTPUTF8 interoperability, so the contracts use it deliberately.
  instance.addFormat('idn-email', /^[^@\s]+@[^@\s]+$/u)
  // roles-v1 references the role enum in permissions-v1 by absolute $id.
  instance.addSchema(loadJson('auth/permissions-v1.schema.json'))
  return instance
}

function assertValid(validate, data, what) {
  if (!validate(data)) {
    const lines = (validate.errors || []).slice(0, 12).map((e) => `  ${e.instancePath || '/'} ${e.message}`)
    throw new Error(`${what} failed validation:\n${lines.join('\n')}`)
  }
}

// ---------------------------------------------------------------- 1. parsing
const yamlFiles = ['openapi', 'errors', 'auth', 'auth/examples', 'observability', 'dns', 'events', 'actions'].flatMap((d) => listFiles(d, '.yaml'))
const jsonFiles = ['errors', 'auth', 'auth/examples', 'observability', 'dns', 'events', 'actions'].flatMap((d) => listFiles(d, '.json'))

check('every YAML artifact parses', () => {
  for (const f of yamlFiles) YAML.parse(read(f))
  return `${yamlFiles.length} files`
})
check('every JSON artifact parses', () => {
  for (const f of jsonFiles) JSON.parse(read(f))
  return `${jsonFiles.length} files`
})

// ------------------------------------------------- 3. schema self-validity
check('every JSON Schema compiles as draft 2020-12', () => {
  const schemaFiles = ['events', 'errors', 'auth', 'observability', 'dns', 'actions'].flatMap((d) => listFiles(d, '.schema.json'))
  const instance = ajv()
  for (const f of schemaFiles) {
    if (f.endsWith('permissions-v1.schema.json')) continue
    try {
      instance.compile(loadJson(f))
    } catch (err) {
      throw new Error(`${f}: ${err.message}`)
    }
  }
  return `${schemaFiles.length} schemas`
})

// ------------------------------------------------ 2. artifacts vs schemas
for (const [artifact, schema] of [
  ['errors/error-catalog-v1.yaml', 'errors/error-catalog-v1.schema.json'],
  ['auth/permissions-v1.yaml', 'auth/permissions-v1.schema.json'],
  ['dns/domain-record-contract-v1.yaml', 'dns/domain-record-contract-v1.schema.json'],
]) {
  check(`${artifact} validates against ${path.basename(schema)}`, () => {
    const instance = ajv()
    const compiled = artifact.includes('permissions-v1')
      ? instance.getSchema('https://contracts.karyalay.in/mail/auth/permissions-v1.schema.json')
      : instance.compile(loadJson(schema))
    assertValid(compiled, loadYaml(artifact), artifact)
  })
}
check('auth/roles-v1.yaml validates against roles-v1.schema.json', () => {
  const instance = ajv()
  assertValid(instance.compile(loadJson('auth/roles-v1.schema.json')), loadYaml('auth/roles-v1.yaml'), 'auth/roles-v1.yaml')
})

// ------------------------------------------------- 4. events round-trip
function sampleValue(prop) {
  if (!prop) return 'sample'
  if (prop.type === 'integer') return prop.minimum ?? 1
  if (prop.type === 'boolean') return true
  if (prop.type === 'array') return [sampleValue(prop.items)]
  if (prop.enum) return prop.enum[0]
  if (prop.format === 'uuid') return '018f5a2c-0000-7000-8000-000000000004'
  if (prop.format === 'date-time') return '2026-08-18T00:00:00.000000Z'
  if (prop.format === 'idn-email') return 'user@example.com'
  const canned = {
    '^[A-Z][A-Z0-9]*(_[A-Z0-9]+)*$': 'PROVISIONING_FAILED',
    '^[a-z][a-z0-9_]*$': 'mail_admin',
    '^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$': 'sel2026a',
  }
  if (prop.pattern && canned[prop.pattern]) return canned[prop.pattern]
  if (prop.pattern && prop.pattern.includes('a-z]{2,63}')) return 'example.com'
  return 'sample'
}

check('every event payload composes with the envelope', () => {
  const instance = ajv()
  const validateEnvelope = instance.compile(loadJson('events/envelope-v1.schema.json'))
  const catalog = loadYaml('events/catalog-v1.yaml')
  if (catalog.events.length !== 45) throw new Error(`catalog holds ${catalog.events.length} events; Appendix D holds 45`)
  const problems = []
  for (const entry of catalog.events) {
    const payloadSchema = loadJson(path.join('events', entry.payload_schema))
    const validatePayload = instance.compile(payloadSchema)
    const data = {}
    for (const field of payloadSchema.required || []) data[field] = sampleValue(payloadSchema.properties[field])
    if (!validatePayload(data)) {
      problems.push(`${entry.event} payload: ${JSON.stringify(validatePayload.errors?.[0])}`)
      continue
    }
    const message = {
      event: entry.event,
      version: entry.version,
      event_id: '018f5a2c-0000-7000-8000-000000000001',
      occurred_at: '2026-08-18T00:00:00.000000Z',
      producer: entry.producer,
      trace_id: '4bf92f3577b34da6a3ce929d0e0e4736',
      request_id: 'req_01J0000000000000000000',
      organisation_id: '018f5a2c-0000-7000-8000-000000000002',
      resource: { type: entry.family, id: '018f5a2c-0000-7000-8000-000000000003', generation: 1 },
      data,
    }
    if (!validateEnvelope(message)) problems.push(`${entry.event} envelope: ${JSON.stringify(validateEnvelope.errors?.[0])}`)
  }
  if (problems.length) throw new Error(problems.slice(0, 8).join('\n'))
  return `${catalog.events.length} events`
})

check('every event in the catalog has a schema file and vice versa', () => {
  const catalog = loadYaml('events/catalog-v1.yaml')
  const declared = new Set(catalog.events.map((e) => e.payload_schema))
  const present = new Set(listFiles('events', '.schema.json').map((f) => path.basename(f)).filter((f) => f !== 'envelope-v1.schema.json'))
  for (const f of declared) if (!present.has(f)) throw new Error(`catalog names ${f}, which does not exist`)
  for (const f of present) if (!declared.has(f)) throw new Error(`${f} exists but no catalog entry names it`)
  return `${declared.size} payload schemas`
})

// ------------------------------------------------- 5. auth examples
check('every auth example validates against claims-v1', () => {
  const validate = ajv().compile(loadYaml('auth/claims-v1.yaml'))
  const manifest = loadYaml('auth/examples/manifest-v1.yaml')
  const roles = loadYaml('auth/roles-v1.yaml').roles.map((r) => r.role)
  const covered = new Set(manifest.examples.map((e) => e.expected_role).filter(Boolean))
  for (const role of roles) if (!covered.has(role)) throw new Error(`no sample token for role ${role} (T00.03 acceptance)`)
  for (const example of manifest.examples) assertValid(validate, loadJson(path.join('auth/examples', example.file)), example.file)
  return `${manifest.examples.length} fixtures, ${roles.length} roles covered`
})

check('a service token carrying a tenant claim is rejected (negative test)', () => {
  const validate = ajv().compile(loadYaml('auth/claims-v1.yaml'))
  const bad = { ...loadJson('auth/examples/service-identity.json'), karyalay_organisation_id: '018f5a2c-0000-7000-8000-000000000005' }
  if (validate(bad)) throw new Error('accepted; Master 9.6 and Repo 1 29.2 forbid a tenant-scoped service token')
  return 'rejected'
})

// ------------------------------------------------- 6. cross-references
const catalogCodes = new Set(loadYaml('errors/error-catalog-v1.yaml').errors.map((e) => e.code))
const permissions = new Set(loadYaml('auth/permissions-v1.yaml').permissions.map((p) => p.permission))
const roleCodes = new Set(loadYaml('auth/roles-v1.yaml').roles.map((r) => r.role))

check('every role granted in permissions-v1 exists in roles-v1', () => {
  for (const entry of loadYaml('auth/permissions-v1.yaml').permissions) {
    for (const bundle of entry.default_role_bundles || []) {
      if (!roleCodes.has(bundle.role)) throw new Error(`permission ${entry.permission} grants unknown role ${bundle.role}`)
    }
  }
  return `${permissions.size} permissions, ${roleCodes.size} roles`
})

check('every permission in roles-v1 exists in permissions-v1', () => {
  for (const role of loadYaml('auth/roles-v1.yaml').roles) {
    for (const grant of role.default_permissions || []) {
      if (!permissions.has(grant.permission)) throw new Error(`role ${role.role} grants unknown permission ${grant.permission}`)
    }
  }
  return 'inverse index consistent'
})

check('the DNS contract maps every observation status and verifies every record', () => {
  const contract = loadYaml('dns/domain-record-contract-v1.yaml')
  const mapped = new Set(contract.health_state_mapping.map((m) => m.observation_status))
  for (const status of contract.observation_status.values) {
    if (!mapped.has(status)) throw new Error(`observation status ${status} has no health-state mapping`)
  }
  const kinds = contract.records.map((r) => r.record_kind)
  if (new Set(kinds).size !== kinds.length) throw new Error('a record kind appears more than once')
  for (const record of contract.records) if (!record.verification_rule) throw new Error(`${record.record_kind} has no verification rule`)
  return `${kinds.length} record kinds, each once, each with a verification rule`
})

check('the telemetry contract keeps repo-local metric catalogs out', () => {
  const text = read('observability/telemetry-contract-v1.yaml')
  const leaked = ['mail_api_requests_total', 'ops_job_oldest_seconds', 'dovecot_auth_total', 'migration_active'].filter((m) => text.includes(m))
  if (leaked.length) throw new Error(`repo-local metric names duplicated here: ${leaked.join(', ')}`)
  const contract = loadYaml('observability/telemetry-contract-v1.yaml')
  const ids = contract.correlation_identifiers.map((c) => c.id)
  for (const required of ['trace_id', 'request_id', 'event_id', 'idempotency_key', 'generation']) {
    if (!ids.includes(required)) throw new Error(`correlation identifier ${required} is missing (Master 6.2 keeps these distinct)`)
  }
  return `${ids.length} correlation identifiers, no repo-local catalogs`
})

// ------------------------------------------------- 7/8. OpenAPI
// The pinned contract version has one source. A literal here drifts from the
// generators the moment a release is cut, and the drift passes silently.
const PINNED_VERSION = JSON.parse(fs.readFileSync('package.json', 'utf8')).version

const openapiFiles = listFiles('openapi', '.yaml').filter((f) => !f.includes('reconciliation'))

check('every OpenAPI document declares 3.1.0 and the pinned contract version', () => {
  for (const f of openapiFiles) {
    const doc = loadYaml(f)
    if (doc.openapi !== '3.1.0') throw new Error(`${f} declares ${doc.openapi}`)
    if (doc.info?.version !== PINNED_VERSION) throw new Error(`${f} declares info.version ${doc.info?.version}, expected ${PINNED_VERSION}`)
  }
  return `${openapiFiles.length} documents`
})

check('every versioned artifact declares the release it ships in', () => {
  // v0.2.0 shipped with observability/ and dns/ still declaring 0.1.0. Nothing
  // caught it: the version check above only reads OpenAPI info.version, and
  // those two files are hand-authored, so the regeneration stage never saw
  // them either. A consumer reading two versions out of one tag cannot tell
  // which is authoritative, so this walks every artifact that declares a
  // version at all and holds all of them to package.json.
  const declared = []
  for (const f of [...listFiles('auth', '.yaml'), ...listFiles('dns', '.yaml'), ...listFiles('errors', '.yaml'), ...listFiles('events', '.yaml'), ...listFiles('observability', '.yaml')]) {
    const doc = loadYaml(f)
    if (typeof doc?.contract_version !== 'string') continue
    declared.push(f)
    if (doc.contract_version !== PINNED_VERSION) {
      throw new Error(`${f} declares contract_version ${doc.contract_version}, but this release is ${PINNED_VERSION}`)
    }
  }
  for (const f of openapiFiles) {
    declared.push(f)
    const doc = loadYaml(f)
    if (doc['x-karyalay-contract-version'] && doc['x-karyalay-contract-version'] !== PINNED_VERSION) {
      throw new Error(`${f} declares x-karyalay-contract-version ${doc['x-karyalay-contract-version']}, expected ${PINNED_VERSION}`)
    }
  }
  if (declared.length < 6) {
    throw new Error(`only ${declared.length} artifacts declare a version; the release carries at least 6, so this check is inspecting less than it should`)
  }
  return `${declared.length} artifacts at ${PINNED_VERSION}`
})

check('OpenAPI operations reconcile 1:1 with Appendix C', () => {
  const recon = loadYaml('openapi/catalog-reconciliation-v1.yaml')
  if (recon.declared_operation_count !== recon.emitted_operation_count) {
    throw new Error(`Appendix C declares ${recon.declared_operation_count}; documents emit ${recon.emitted_operation_count}`)
  }
  const byDoc = new Map()
  // Appendix C documents only. infra-executor-api-v1.yaml holds Appendix AI
  // deltas, not Appendix C rows, and reconciles against
  // executor-reconciliation-v1.yaml in the check below. Folding it in here
  // would make one count cover two catalogs, so neither could be exhaustive.
  for (const f of openapiFiles.filter((f) => !f.endsWith('infra-executor-api-v1.yaml'))) {
    const doc = loadYaml(f)
    const ids = new Map()
    for (const [p, item] of Object.entries(doc.paths)) {
      for (const [method, op] of Object.entries(item)) {
        ids.set(op.operationId, { path: p, method, catalog: op['x-karyalay-catalog-id'] })
      }
    }
    byDoc.set(path.basename(f), ids)
  }
  const seen = new Set()
  for (const row of recon.operations) {
    const ids = byDoc.get(row.document)
    if (!ids) throw new Error(`${row.catalog_id} names document ${row.document}, which does not exist`)
    const op = ids.get(row.operation_id)
    if (!op) throw new Error(`${row.catalog_id} names operationId ${row.operation_id}, absent from ${row.document}`)
    if (op.catalog !== row.catalog_id) throw new Error(`${row.operation_id} carries catalog id ${op.catalog}, expected ${row.catalog_id}`)
    if (op.path !== row.path) throw new Error(`${row.catalog_id} path mismatch: ${op.path} vs ${row.path}`)
    if (seen.has(row.operation_id)) throw new Error(`operationId ${row.operation_id} used twice`)
    seen.add(row.operation_id)
  }
  const total = [...byDoc.values()].reduce((n, m) => n + m.size, 0)
  if (total !== recon.operations.length) throw new Error(`documents hold ${total} operations; the reconciliation lists ${recon.operations.length}`)
  return `${total} operations`
})

check('the executor document reconciles 1:1 with Appendix AI', () => {
  // The same exhaustiveness property the Appendix C check enforces, applied to
  // the hand-authored document. A document with no map is one where a seventh
  // operation can be added quietly, and "the allow-list is closed" would then
  // be a sentence in a description rather than a fact.
  const recon = loadYaml('openapi/executor-reconciliation-v1.yaml')
  const doc = loadYaml('openapi/infra-executor-api-v1.yaml')

  const emitted = new Map()
  for (const [p, item] of Object.entries(doc.paths)) {
    for (const [method, op] of Object.entries(item)) {
      emitted.set(op.operationId, { path: p, method: method.toUpperCase(), catalog: op['x-karyalay-catalog-id'] })
    }
  }
  if (emitted.size !== recon.declared_operation_count) {
    throw new Error(`document emits ${emitted.size} operations; the map declares ${recon.declared_operation_count}`)
  }
  for (const row of recon.operations) {
    const op = emitted.get(row.operation_id)
    if (!op) throw new Error(`${row.catalog_id} names operationId ${row.operation_id}, absent from the document`)
    if (op.catalog !== row.catalog_id) throw new Error(`${row.operation_id} carries catalog id ${op.catalog}, expected ${row.catalog_id}`)
    if (op.path !== row.path) throw new Error(`${row.catalog_id} path mismatch: ${op.path} vs ${row.path}`)
    if (op.method !== row.method) throw new Error(`${row.catalog_id} method mismatch: ${op.method} vs ${row.method}`)
  }
  return `${emitted.size} executor operations`
})

check('no operation in the executor document carries a free-text command surface', () => {
  // The property ADR-INF-038 exists to guarantee, asserted rather than
  // described. "No generic remote shell" is worth nothing as prose in a
  // description; here it is a test that fails if anybody adds the field.
  const doc = loadYaml('openapi/infra-executor-api-v1.yaml')
  const banned = /^(command|cmd|script|shell|exec|args|argv|query|sql|path|raw|payload)$/i
  const found = []
  const walk = (node, trail) => {
    if (Array.isArray(node)) return node.forEach((v, i) => walk(v, trail))
    if (!node || typeof node !== 'object') return
    for (const [k, v] of Object.entries(node)) {
      if (k === 'properties' && v && typeof v === 'object') {
        for (const name of Object.keys(v)) if (banned.test(name)) found.push(`${trail}.${name}`)
      }
      walk(v, `${trail}.${k}`)
    }
  }
  walk(doc.paths, 'paths')
  if (found.length) throw new Error(`command-shaped fields present: ${found.join(', ')}`)
  return 'six operations, no command field'
})

check('the inlined action envelope matches actions/action-envelope-v1.schema.json', () => {
  // The OpenAPI document must resolve every $ref locally, so the AI-12 envelope
  // is transcribed into it rather than referenced out. A transcription that can
  // drift is two definitions wearing one name, so this compares them field for
  // field and fails on any difference.
  const schema = loadJson('actions/action-envelope-v1.schema.json')
  const doc = loadYaml('openapi/infra-executor-api-v1.yaml')
  const inlined = doc.components.schemas.ActionEnvelope
  const strip = (n) => {
    if (Array.isArray(n)) return n.map(strip)
    if (!n || typeof n !== 'object') return n
    return Object.fromEntries(Object.entries(n).filter(([k]) => !['$schema', '$id', '$defs'].includes(k)).map(([k, v]) => [k, strip(v)]))
  }
  const a = JSON.stringify(strip(schema))
  const b = JSON.stringify(strip(inlined))
  if (a !== b) throw new Error('the inlined envelope has drifted from the schema file; regenerate it rather than editing one side')

  const observed = doc.components.schemas.ObservedState
  if (JSON.stringify(strip(schema.$defs.observed_state)) !== JSON.stringify(strip(observed))) {
    throw new Error('the inlined observed_state has drifted from the schema file')
  }
  return `${Object.keys(schema.properties).length} envelope fields, matched`
})

check('no OpenAPI document names an error code the catalog does not define', () => {
  // Every `code` enum anywhere in the document, found structurally rather than
  // at one hard-coded path. An earlier version of this check looked only at
  // schema.allOf[1].properties.code.enum; when the generator moved to a flat
  // per-status Problem schema the path stopped matching, the count fell to
  // zero, and the check passed without inspecting anything.
  const codeEnums = (node, out = []) => {
    if (Array.isArray(node)) { for (const v of node) codeEnums(v, out); return out }
    if (!node || typeof node !== 'object') return out
    for (const [k, v] of Object.entries(node)) {
      if (k === 'code' && v && Array.isArray(v.enum)) out.push(...v.enum)
      else codeEnums(v, out)
    }
    return out
  }

  let counted = 0
  for (const f of openapiFiles) {
    const doc = loadYaml(f)
    const codes = [
      ...(doc.components?.schemas?.ErrorCode?.enum || []),
      ...codeEnums(doc.components?.responses || {}),
      ...codeEnums(doc.paths || {}),
    ]
    for (const code of codes) {
      if (!catalogCodes.has(code)) throw new Error(`${f} names ${code}, absent from errors/error-catalog-v1.yaml`)
      counted++
    }
    if (codes.length === 0) throw new Error(`${f} exposes no error codes at all -- the check found nothing to verify, which is a bug in the check or the generator, not a clean document`)
  }
  return `${counted} code references, all resolved`
})

check('the provisioning exchange carries the ADR-KEM-008 union, not either side alone', () => {
  const doc = loadYaml('openapi/internal-provisioning-api-v1.yaml')
  const S = doc.components.schemas
  const desired = S.DesiredState
  if (!desired) throw new Error('DesiredState absent from the provisioning document')

  // Decisions 1-6: every field the union resolved, present at the envelope level.
  const required = ['schema_version', 'resource_type', 'resource_id', 'organisation_id', 'desired_generation', 'desired_status', 'spec', 'correlation']
  for (const k of required) {
    if (!desired.properties[k]) throw new Error(`DesiredState is missing ${k} (ADR-KEM-008)`)
    if (!desired.required.includes(k)) throw new Error(`DesiredState does not require ${k} (ADR-KEM-008)`)
  }
  if (!desired.properties.dependencies) throw new Error('DesiredState is missing dependencies (ADR-KEM-008 decision 4)')

  // Decisions 2, 3, 5: the retired spellings must be gone from the envelope.
  // "Either is defensible; publishing both is not" -- ADR-KEM-008 divergence 1.
  for (const k of ['mailbox_id', 'generation', 'domain_id', 'storage_key', 'quota_bytes', 'auth_state', 'receive_state', 'send_state', 'filter_generation', 'primary_address']) {
    if (desired.properties[k]) throw new Error(`DesiredState still carries ${k} at the envelope level; decision 2/5 moves type-specific and typed fields into spec`)
  }
  // ...and must be reachable inside spec, so nothing was dropped rather than moved.
  const spec = S.DesiredStateSpec
  if (!spec) throw new Error('DesiredStateSpec absent -- decision 5 nests typed fields under spec')
  for (const k of ['mailbox_id', 'domain_id', 'storage_key', 'quota_bytes', 'auth_state', 'receive_state', 'send_state', 'filter_generation', 'primary_address']) {
    if (!spec.properties[k]) throw new Error(`DesiredStateSpec lost ${k}; the union moves Repo 1 §12.2 fields, it does not drop them`)
  }

  // Decision 6: correlation survives. Master §30 requires it across this hop.
  if (!desired.properties.correlation.properties?.operation_id) throw new Error('correlation lost operation_id (Master §30, decision 6)')

  return `${required.length} envelope fields, ${Object.keys(spec.properties).length} nested in spec`
})

check('readiness is the seven-value union and the observation can record drift', () => {
  const S = loadYaml('openapi/internal-provisioning-api-v1.yaml').components.schemas
  const obs = S.ObservationReport
  if (!obs) throw new Error('ObservationReport absent')

  // Decision 7: Repo 3 §50's six, plus Repo 1 Appendix A.32's ABSENT.
  const want = ['PENDING', 'READY', 'DEGRADED', 'FAILED', 'RESTRICTED', 'DELETING', 'ABSENT']
  const got = obs.properties.readiness?.enum || []
  const missing = want.filter((v) => !got.includes(v))
  const extra = got.filter((v) => !want.includes(v))
  if (missing.length) throw new Error(`readiness is missing ${missing.join(', ')} (ADR-KEM-008 decision 7)`)
  if (extra.length) throw new Error(`readiness carries undeclared value(s) ${extra.join(', ')}`)

  // Decision 3: desired_generation beside observed_generation, per Repo 1 §29.1's own wording.
  for (const k of ['desired_generation', 'observed_generation', 'schema_version']) {
    if (!obs.properties[k]) throw new Error(`ObservationReport is missing ${k}`)
  }
  if (obs.properties.generation) throw new Error('ObservationReport still carries the ambiguous `generation`; decision 3 splits it')
  if (obs.properties.status) throw new Error('ObservationReport still carries `status`; decision 7 renames it readiness')

  // Decision 8: checksum drift is one of Repo 3 §50's two drift triggers and
  // Repo 1 Appendix A.32 had nowhere to record it.
  if (!obs.properties.checksum) throw new Error('ObservationReport cannot record a checksum, so checksum-detected drift cannot be reported (decision 8)')

  return `${got.length} readiness values, checksum recordable`
})

check('a dependency cannot name a resource kind the envelope cannot carry', () => {
  const S = loadYaml('openapi/internal-provisioning-api-v1.yaml').components.schemas
  const kinds = S.DesiredStateResourceType?.enum || []
  if (!kinds.length) throw new Error('DesiredStateResourceType absent or empty')
  const dep = S.ResourceDependency
  if (!dep) throw new Error('ResourceDependency absent (ADR-KEM-008 decision 4)')
  const ref = dep.properties.resource_type?.$ref
  if (ref !== '#/components/schemas/DesiredStateResourceType') {
    throw new Error(`ResourceDependency.resource_type is ${ref || 'inline'}; it must share the envelope's vocabulary or a dependency could name a kind that cannot exist`)
  }
  for (const k of ['resource_id', 'min_generation']) {
    if (!dep.required.includes(k)) throw new Error(`ResourceDependency does not require ${k}`)
  }
  // Both source vocabularies must survive the union.
  for (const k of ['domain', 'mailbox', 'alias', 'group', 'quota', 'filter_set', 'restriction', 'dkim_key']) {
    if (!kinds.includes(k)) throw new Error(`resource_type lost Repo 3 Appendix O.1 kind ${k}`)
  }
  for (const k of ['organisation', 'placement']) {
    if (!kinds.includes(k)) throw new Error(`resource_type lost Repo 1 Appendix A.31 kind ${k}`)
  }
  return `${kinds.length} resource kinds, shared by envelope and dependencies`
})

check('every operation permission resolves in permissions-v1', () => {
  let counted = 0
  for (const f of openapiFiles) {
    const doc = loadYaml(f)
    for (const item of Object.values(doc.paths)) {
      for (const op of Object.values(item)) {
        for (const token of String(op['x-karyalay-permission'] || '').split(/[\s,;]+/)) {
          if (/^[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*$/.test(token)) {
            if (!permissions.has(token)) throw new Error(`${f} ${op.operationId} names permission ${token}, absent from auth/permissions-v1.yaml`)
            counted++
          }
        }
      }
    }
  }
  return `${counted} permission references, all resolved`
})

check('every $ref inside an OpenAPI document resolves', () => {
  let counted = 0
  for (const f of openapiFiles) {
    const doc = loadYaml(f)
    const walk = (node) => {
      if (Array.isArray(node)) return node.forEach(walk)
      if (!node || typeof node !== 'object') return
      for (const [key, value] of Object.entries(node)) {
        if (key === '$ref' && typeof value === 'string') {
          counted++
          if (!value.startsWith('#/')) throw new Error(`${f} has a non-local $ref: ${value}`)
          let cursor = doc
          for (const segment of value.slice(2).split('/')) {
            cursor = cursor?.[segment.replace(/~1/g, '/').replace(/~0/g, '~')]
            if (cursor === undefined) throw new Error(`${f} has an unresolved $ref: ${value}`)
          }
        } else walk(value)
      }
    }
    walk(doc)
  }
  return `${counted} refs resolved`
})

// ------------------------------------------- 9. deferrals vs the current tag
//
// ADR-KEM-012, "The process lesson": ADR-KEM-009 deferred seven deltas to
// `v0.2.0`, the target passed three times, and nothing failed because nothing
// compared a deferral's target against the version the repository had reached.
// These five checks are that comparison. See tools/validate/deferrals.mjs.

const deferralRegister = deferrals.loadRegister(ROOT)
const contractVersion = loadJson('package.json').version

check('the deferral register is well-formed', () => {
  const problems = deferrals.auditShape(deferralRegister)
  if (problems.length) throw new Error(problems.join('\n'))
  return `${deferralRegister.deferrals.length} deferrals`
})

check("no deferral's target tag has passed with the deferred thing absent", () => {
  const problems = deferrals.auditMaturity(deferralRegister, contractVersion)
  if (problems.length) throw new Error(problems.join('\n'))
  const withTag = deferralRegister.deferrals.filter((d) => d.target?.tag).length
  const blind = deferrals.unmaturable(deferralRegister)
  // Printed on every run rather than passed over: these are the deferrals no
  // version comparison can mature, and they are held only by the owner ratchet.
  return `${withTag} tag-targeted deferrals checked against v${contractVersion}` +
    (blind.length ? `; ${blind.length} NOT maturable by version (${blind.join(', ')})` : '')
})

check('every open deferral has an owner, and the ownerless count only falls', () => {
  const { problems, unassigned } = deferrals.auditOwnership(deferralRegister)
  if (problems.length) throw new Error(problems.join('\n'))
  return `${unassigned.length} ownerless, at the declared baseline`
})

check('every honoured deferral resolves to a real operation or schema', () => {
  const { problems, resolved } = deferrals.auditArtifacts(deferralRegister, ROOT)
  if (problems.length) throw new Error(problems.join('\n'))
  if (resolved === 0) throw new Error('nothing was resolved -- the check found no artifact to verify, which is a bug in the check, not a clean register')
  return `${resolved} artifacts resolved in their documents`
})

check('the deferral check fires on ADR-KEM-009 at v0.4.0 (negative test)', () => {
  const fixture = deferrals.loadRegister(ROOT, 'tools/validate/fixtures/deferral-register-at-v0.4.0.yaml')
  const shape = deferrals.auditShape(fixture)
  if (shape.length) throw new Error(`the fixture itself is malformed: ${shape.join('; ')}`)

  // The situation as it actually stood when v0.4.0 was tagged.
  const atTarget = deferrals.auditMaturity(fixture, '0.4.0')
  const want = ['AI-04', 'AI-05', 'AI-06', 'AI-07', 'AI-08', 'AI-09', 'AI-12']
  for (const id of want) {
    if (!atTarget.some((m) => m.startsWith(`${id} `))) throw new Error(`the check did not fire on ${id} at v0.4.0, which is the whole reason it exists`)
  }
  if (atTarget.length !== want.length) {
    throw new Error(`expected ${want.length} violations at v0.4.0, got ${atTarget.length}:\n${atTarget.join('\n')}`)
  }

  // ...and it must fire at v0.2.0 too, the tag the deferral actually named.
  if (deferrals.auditMaturity(fixture, '0.2.0').length !== want.length) {
    throw new Error('the check did not fire at v0.2.0, the target tag itself')
  }

  // Before the target, a deferral is not a defect. A check that flags
  // everything is not a check.
  const atV1 = deferrals.auditMaturity(fixture, '0.1.0')
  if (want.some((id) => atV1.some((m) => m.startsWith(`${id} `)))) {
    throw new Error(`the check flagged a deferral at v0.1.0, before its target had been reached:\n${atV1.join('\n')}`)
  }
  // The one thing it must say at v0.1.0 is that a row cannot have been
  // honoured in a tag that does not exist yet.
  if (!atV1.some((m) => m.startsWith('FIXTURE-ALREADY-HONOURED') && m.includes('ahead of'))) {
    throw new Error('the check accepted a deferral honoured in a tag ahead of the current version')
  }

  // And an honoured row must not be flagged, however far past its target.
  if (deferrals.auditMaturity(fixture, '0.9.0').some((m) => m.startsWith('FIXTURE-ALREADY-HONOURED'))) {
    throw new Error('the check flagged a deferral that was delivered on time')
  }
  return '7 violations at v0.4.0 and at v0.2.0, none of the seven at v0.1.0'
})

// --------------------------------------- 10. the cross-repository delta register
//
// Repo 4's Appendix AI, Repo 3's Appendix AB and Repo 2's Appendix N are three
// prose tables inside three 4,000-line specifications, which is why a delta's
// disposition, target tag and owner could not be checked by anything.
// docs/registers/delta-register-v1.yaml is the machine-readable projection.

const deltaRegister = deltas.loadRegister(ROOT)

check('the delta register validates against its schema', () => {
  const instance = ajv()
  assertValid(instance.compile(loadJson(deltas.SCHEMA_PATH)), deltaRegister, deltas.REGISTER_PATH)
  return `${deltas.allDeltas(deltaRegister).length} deltas -- ${deltas.summarise(deltaRegister)}`
})

check('the delta register holds every row its appendices declare', () => {
  const { problems, counts } = deltas.auditRowCounts(deltaRegister)
  if (problems.length) throw new Error(problems.join('\n'))
  return counts.join(', ')
})

check('every delta id in the register appears in the appendix it came from', () => {
  // Only runs in full when the sibling repositories are checked out beside
  // this one, which CI does not do. The detail line says which mode ran, so a
  // pass that inspected nothing cannot look like a pass that inspected
  // everything -- START-HERE 6.4, applied to this check rather than to a host.
  const siblings = path.resolve(ROOT, '..')
  const { problems, checked } = deltas.auditAgainstAppendices(deltaRegister, siblings)
  if (problems.length) throw new Error(problems.join('\n'))
  return checked.join('; ')
})

check('every artifact a delta claims resolves in the document that should hold it', () => {
  const { problems, resolved } = deltas.auditArtifacts(deltaRegister, ROOT)
  if (problems.length) throw new Error(problems.join('\n'))
  if (resolved === 0) throw new Error('nothing resolved -- the check found no artifact to verify, which is a bug in the check, not a clean register')
  return `${resolved} artifacts resolved, catalog ids cross-checked`
})

check('the delta register and the deferral register describe the same deferrals', () => {
  const problems = deltas.auditDeferralLinkage(deltaRegister, deferralRegister)
  if (problems.length) throw new Error(problems.join('\n'))
  const deferred = deltas.allDeltas(deltaRegister).filter((d) => d.disposition === 'DEFERRED')
  return `${deferred.length} deferred deltas, each with an enforceable target`
})

check('no delta relates to an id that does not exist', () => {
  const { problems, counted } = deltas.auditCrossReferences(deltaRegister)
  if (problems.length) throw new Error(problems.join('\n'))
  return `${counted} cross-references resolved`
})

check('every ADR the delta register names exists and is in the decision register', () => {
  const { problems, counted, unraised } = deltas.auditAdrReferences(deltaRegister, ROOT)
  if (problems.length) throw new Error(problems.join('\n'))
  // Printed rather than passed over: a known defect with no ADR raised is the
  // ADR-KEM-009 shape one level down, and the count should only ever fall.
  return `${counted} ADR references resolved; ${unraised} known defect(s) with NO ADR raised`
})

// ------------------------------------------------- task tree

check("every task's frontmatter status matches the glyph in its phase index", () => {
  const { drifted, checked } = taskindex.auditIndex(ROOT)
  if (drifted.length) throw new Error(drifted.join('\n'))
  // Non-vacuity. Every assertion above passes over an empty task tree, and a
  // regex that stopped matching would produce exactly that.
  if (checked < 12) throw new Error(`only ${checked} index rows were read; the scan is not finding the task tree`)
  return `${checked} index rows agree with their task frontmatter`
})

check('the legend in tasks/README.md is the one this harness enforces', () => {
  const problems = taskindex.auditLegend(ROOT)
  if (problems.length) throw new Error(problems.join('\n'))
  return `${Object.keys(taskindex.GLYPH).length} statuses, legend and harness agree`
})

check('a drifted index row is actually caught (negative test)', () => taskindex.selfTest())

// ------------------------------------------------- negative test
check('a deliberately broken catalog fails (negative test)', () => {
  const validate = ajv().compile(loadJson('errors/error-catalog-v1.schema.json'))
  const a = structuredClone(loadYaml('errors/error-catalog-v1.yaml'))
  a.errors.find((e) => e.code === 'SUBMISSION_STATUS_UNKNOWN').http_status = 500
  if (validate(a)) throw new Error('accepted SUBMISSION_STATUS_UNKNOWN mapped to 500; 39.1 pins it to 202')
  const b = structuredClone(loadYaml('errors/error-catalog-v1.yaml'))
  b.errors[0].retry_class = 'MAYBE_LATER'
  if (validate(b)) throw new Error('accepted a retry class that 39 does not define')
  return 'two mutations rejected'
})

console.log('')
console.log(`${checks} checks, ${failures.length} failures`)
process.exit(Math.min(failures.length, 250))
