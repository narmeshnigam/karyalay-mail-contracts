# Consuming the contracts

How a repository pins a release of `karyalay-mail-contracts`, generates from it,
and proves in its own CI that it builds against the tag. Required by
[ADR-KEM-001](docs/adr/ADR-KEM-001-shared-contracts-ownership.md): Gate 0 does
not close until all four consumers record a green validation run against a
tagged release.

## The three rules

1. **Pin a tag, never a branch.** Master §0.3. A branch moves; a contract that
   moves under a consumer is not a contract.
2. **Never fork a schema.** Master §0.3 prohibits a private copy. Vendoring a
   *pinned* copy for offline builds is fine — editing it is not, and the
   verification step below exists to catch it.
3. **Generate, do not transcribe.** Hand-written types drift silently. If your
   language has a generator, use it and commit the output; if it does not,
   validate against the schema at runtime in tests.

## What you are pinning

| Path | Artifact | Format |
| --- | --- | --- |
| `openapi/public-control-api-v1.yaml` | 70 customer-administration operations | OpenAPI 3.1 |
| `openapi/mailbox-api-v1.yaml` | 26 mailbox data-plane operations | OpenAPI 3.1 |
| `openapi/internal-provisioning-api-v1.yaml` | 7 operations toward Infra | OpenAPI 3.1 |
| `openapi/operations-api-v1.yaml` | 4 operations toward Ops | OpenAPI 3.1 |
| `openapi/catalog-reconciliation-v1.yaml` | Appendix C ↔ operationId map | YAML |
| `events/envelope-v1.schema.json` | The shared event envelope | JSON Schema 2020-12 |
| `events/<name>-v1.schema.json` | 45 event payloads | JSON Schema 2020-12 |
| `events/catalog-v1.yaml` | Event index: subject, family, schema file | YAML |
| `errors/error-catalog-v1.yaml` | 80 error codes | YAML |
| `auth/claims-v1.yaml` | Token claims | JSON Schema in YAML |
| `auth/roles-v1.yaml` | 14 roles and their default bundles | YAML |
| `auth/permissions-v1.yaml` | 32 permissions | YAML |
| `observability/telemetry-contract-v1.yaml` | Correlation, naming, cardinality | YAML |
| `observability/log-record-v1.schema.json` | Shared log fields | JSON Schema 2020-12 |
| `dns/domain-record-contract-v1.yaml` | Customer-domain record set | YAML |

`docs/`, `tools/` and `tasks/` are **not** release artifacts. `docs/BUILD-ORDER.md`
and `docs/INFRASTRUCTURE-PLAN.md` are held here for custody only and carry no
contract authority.

## Pinning

```bash
CONTRACTS_TAG=v0.1.0

git submodule add https://github.com/<org>/karyalay-mail-contracts.git contracts
git -C contracts checkout "$CONTRACTS_TAG"
```

Record the tag in **one** place your build reads — a `CONTRACTS_TAG` file, a
`Makefile` variable, a `composer.json` extra. Two places means one of them will
be stale.

### Verify what you pinned

A pinned tag can still be edited in a working copy. Verify before generating:

```bash
git -C contracts describe --exact-match --tags   # must print the tag
git -C contracts status --porcelain              # must print nothing
```

Both checks belong in CI, not only in a developer's habits.

## Per-language notes

### PHP — `karyalay-mail`

Generate server-side request/response DTOs from the OpenAPI documents, and load
the error catalog at runtime rather than re-declaring codes in an enum.

```bash
composer require --dev openapitools/openapi-generator-cli
vendor/bin/openapi-generator-cli generate \
  -i contracts/openapi/public-control-api-v1.yaml \
  -g php -o build/contracts/public-control
```

Repo 1 §26.2 additionally requires a generated
`contracts/generated/public-mail-api.yaml` validated against controller
behaviour in CI. **That document and the one here must agree**: this repository
is the contract, and Repo 1's generated document is evidence that the
implementation matches it. A diff between them is a defect in Repo 1, not a
reason to edit the contract.

The error catalog is a data file, so read it:

```php
$catalog = Yaml::parseFile('contracts/errors/error-catalog-v1.yaml');
$byCode  = array_column($catalog['errors'], null, 'code');
// $byCode['MAILBOX_QUOTA_EXCEEDED']['http_status'] === 507
```

Declaring the codes in a PHP enum instead is a fork by another name — the enum
and the catalog will diverge on the first addition.

### TypeScript — `karyalay-webmail`

```bash
npm i -D openapi-typescript ajv ajv-formats yaml
npx openapi-typescript contracts/openapi/mailbox-api-v1.yaml \
  -o src/generated/mailbox-api.ts
npx openapi-typescript contracts/openapi/public-control-api-v1.yaml \
  -o src/generated/public-control-api.ts
```

Commit the generated files and add a CI step that regenerates and fails on a
diff. Uncommitted generated types are types nobody reviews.

Derive the error-to-UX mapping from the catalog rather than restating Repo 2
Appendix G in the client — the catalog already carries `ux_class` and
`ux_behavior` for the 49 codes the browser can encounter, and `null` for the
rest, which is itself the signal that a code should never reach a screen.

### Go — `karyalay-mail-infra`

The controller consumes `internal-provisioning-api-v1.yaml` and the
`mail.v1.*` event schemas.

```bash
go install github.com/oapi-codegen/oapi-codegen/v2/cmd/oapi-codegen@latest
oapi-codegen -package contracts -generate types,client \
  contracts/openapi/internal-provisioning-api-v1.yaml > internal/contracts/provisioning.gen.go
```

> **Read [ADR-KEM-008](docs/adr/ADR-KEM-008-desired-state-and-observation-shape.md)
> before generating.** Repo 1 §12.2 and Repo 3 §49 describe the desired-state
> document differently, and `v0.1.0` publishes the Repo 1 shape. The reconciliation
> proposes a union in `v0.2.0`, and items in it are shared-breaking.

For events, validate against the JSON Schemas at consume time:

```go
//go:embed contracts/events/*.schema.json
var eventSchemas embed.FS
```

### Ansible / YAML — `karyalay-mail-infra`, `karyalay-mail-ops`

No code generation. Load the contract files as facts and assert against them:

```yaml
- name: Load the DNS record contract
  ansible.builtin.include_vars:
    file: "{{ contracts_dir }}/dns/domain-record-contract-v1.yaml"
    name: dns_contract

- name: Every record required for activation has a verification rule
  ansible.builtin.assert:
    that:
      - dns_contract.records
        | selectattr('required_for_activation')
        | rejectattr('verification_rule', 'defined')
        | list | length == 0
```

## Wiring contract validation into your CI

Every consumer runs three checks. The first two are the evidence ADR-KEM-001
requires; the third is what stops a silent fork.

```yaml
- name: Contracts — pinned tag is exact and clean
  run: |
    git -C contracts describe --exact-match --tags
    test -z "$(git -C contracts status --porcelain)"

- name: Contracts — upstream harness passes on the pinned tree
  working-directory: contracts
  run: npm ci && npm run validate

- name: Contracts — generated artifacts are up to date
  run: |
    <your generate command>
    git diff --exit-code -- <generated paths>
```

Record the run URL in your repository's Phase 0 evidence. That recorded run is
what closes Gate 0 for your repository.

## When a contract changes

Change classes are Master §0.4:

| Class | Example | What you do |
| --- | --- | --- |
| Shared compatible | A new optional event field, a new endpoint, a new metric | Re-pin at leisure. Old consumers keep working — this is what "additive" buys. |
| Shared breaking | An event rename, an identifier semantic change, an auth model change | Re-pin deliberately, regenerate, and expect code changes. Requires a master-contract revision upstream. |

A published tag is **never moved**. A correction ships as `v0.1.1` or later. If
you find a defect in a tagged contract, raise it — do not patch your vendored
copy, because the next consumer will hit the same defect and fix it differently.

## When you find a gap

Master §0.2 is explicit: **do not resolve a shared-contract conflict by
invention.** If your repository needs something the contracts do not define:

1. Stop at the affected boundary.
2. Raise an ADR in `docs/adr/` here, following the existing `ADR-KEM-*` files.
3. Reference it from your repository's task file so the blocker names a decision
   rather than an open question.

Four ADRs in `docs/adr/` (KEM-005 through KEM-008) exist because Gate 0 found
exactly these gaps. They are the pattern to follow, not exceptions to it.
