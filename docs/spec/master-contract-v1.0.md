**KARYALAY**

Email  
Master Architecture &  
Integration Contract

Version 1.0 | Engineering Baseline | 16 August 2026

**Purpose**  
The normative system contract shared by all Karyalay Email repositories and coding agents. It freezes the architectural boundaries, integration contracts, security and reliability requirements, canonical models, and end-to-end invariants required for an independently operated commercial email service.

**POSTFIX • DOVECOT • RSPAMD • KARYALAY CONTROL PLANE • KARYALAY WEBMAIL • OPERATIONS**

**STATUS: NORMATIVE BASELINE FOR REPOSITORY SPECIFICATIONS**

This document does not replace the four repository specifications. It constrains them. Any repository implementation that conflicts with this contract is non-conformant unless the master contract is revised through the architecture-change process defined herein.

**Contents**

Top-level sections and appendices. Page numbers correspond to this v1.0 baseline; use Word's Navigation Pane for second-level headings.

| **0\.** Document Governance and Reading Rules **3**<br><br>**1\.** Mission, Scope and Quality Bar **6**<br><br>**2\.** Non-Negotiable Architectural Principles **8**<br><br>**3\.** System Context and Product Boundaries **10**<br><br>**4\.** Repository Responsibilities and Dependency Direction **12**<br><br>**5\.** Technology and Open-Source Component Baseline **14**<br><br>**6\.** Canonical Domain Model and Identifier Rules **16**<br><br>**7\.** Multi-Tenancy and Isolation Model **18**<br><br>**8\.** Trust Zones, Network Boundaries and Service Topology **19**<br><br>**9\.** Identity, Authentication and Session Architecture **21**<br><br>**10\.** Authorization and Administrative Privilege Model **23**<br><br>**11\.** Secrets, Cryptographic Keys and Certificate Management **25**<br><br>**12\.** Customer Domain Onboarding and DNS Architecture **27**<br><br>**13\.** Inbound Mail Flow Contract **29**<br><br>**14\.** Outbound Submission and Delivery Contract **31**<br><br>**15\.** Aliases, Forwarding, Distribution Groups and Auto-Replies **33**<br><br>**16\.** Internet Mail Standards and Interoperability Baseline **34**<br><br>**17\.** Mailbox Storage, Namespace, Quotas and Lifecycle **36**<br><br>**18\.** Message Model, Threading, Search and Indexing Boundaries **38**<br><br>**19\.** Webmail/Data-Plane Integration Contract **40**<br><br>**20\.** Public and Internal HTTP API Conventions **42**<br><br>**21\.** Provisioning and Infrastructure Control Contract **44**<br><br>**22\.** Event Architecture and Durable Integration **46**<br><br>**23\.** Error Taxonomy and Failure Semantics **48**<br><br>**24\.** Transactions, Idempotency, Concurrency and Reconciliation **50**<br><br>**25\.** Background Jobs, Queues and Schedulers **51**<br><br>**26\.** Security Architecture and Threat Controls **52** | **27\.** Anti-Abuse, Spam, Reputation and Deliverability Architecture **55**<br><br>**28\.** Data Classification, Privacy, Retention and Deletion **58**<br><br>**29\.** Auditability and Administrative Accountability **60**<br><br>**30\.** Observability: Logs, Metrics, Traces and Correlation **62**<br><br>**31\.** Service Levels, Performance and Reliability Objectives **64**<br><br>**32\.** Capacity, Scaling and Placement Strategy **65**<br><br>**33\.** High Availability, Failover and Degraded Modes **67**<br><br>**34\.** Backup, Restore and Disaster Recovery **69**<br><br>**35\.** Environments, Deployment Topology and Configuration Management **71**<br><br>**36\.** CI/CD, Supply-Chain Security and Release Engineering **74**<br><br>**37\.** Testing and Verification Strategy **76**<br><br>**38\.** Compatibility, Versioning and Upgrade Policy **79**<br><br>**39\.** Incident Response and Emergency Control Plane **80**<br><br>**40\.** Operational Governance, ADRs and Change Management **82**<br><br>**41\.** Cross-Repository End-to-End Flows **83**<br><br>**42\.** Global Definition of Done and Production Acceptance **86**<br><br>**43\.** Phased Delivery Gates **88**<br><br>**Appendix A.** Canonical Entity Catalog **90**<br><br>**Appendix B.** Role and Permission Baseline **92**<br><br>**Appendix C.** Event Catalog Baseline **94**<br><br>**Appendix D.** Error Catalog Baseline **96**<br><br>**Appendix E.** Port and Firewall Matrix Baseline **98**<br><br>**Appendix F.** DNS and Naming Baseline **99**<br><br>**Appendix G.** SLO and Alert Baseline **100**<br><br>**Appendix H.** Data Retention Baseline **101**<br><br>**Appendix I.** Standards and Authoritative References **102**<br><br>**Appendix J.** Coding-Agent Handoff Rules **104** |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |

# 0\. Document Governance and Reading Rules

## 0.1 Document identity

| **Field**        | **Value**                                                                                                    |
| ---------------- | ------------------------------------------------------------------------------------------------------------ |
| Document         | Karyalay Email — Master Architecture & Integration Contract                                                  |
| Version          | 1.0                                                                                                          |
| Status           | Normative engineering baseline                                                                               |
| Effective date   | 16 August 2026                                                                                               |
| Owners           | Karyalay Product Engineering, Platform Engineering, Security and Operations                                  |
| Applies to       | \`karyalay-mail\`, \`karyalay-webmail\`, \`karyalay-mail-infra\`, \`karyalay-mail-ops\`                      |
| Primary audience | Repository coding agents, maintainers, security reviewers, SRE/operations, future Karyalay engineering teams |
| Change authority | Architecture review process defined in Section 40                                                            |

This document defines the shared architecture of Karyalay Email. It is deliberately more prescriptive than a normal architecture overview because four repositories may be implemented in parallel by independent coding agents. The objective is to eliminate incompatible assumptions before implementation begins.

**Non-negotiable: a repository specification may add implementation detail, but it MUST NOT contradict, silently weaken, rename, or reinterpret a normative requirement in this document.**

## 0.2 Normative language

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **MAY**, and **OPTIONAL** carry their normal requirements meaning. "MUST" is a release-blocking requirement unless this document explicitly assigns it to a later delivery gate.

A coding agent encountering an ambiguity SHALL follow this precedence order:

**1\.** This Master Architecture & Integration Contract.

**2\.** Machine-readable shared contracts committed under the approved contracts directory.

**3\.** The repository-specific engineering specification.

**4\.** An approved Architecture Decision Record (ADR) that explicitly modifies a lower-priority item without conflicting with this master contract.

**5\.** Existing implementation conventions.

If two higher-priority sources conflict, implementation MUST stop at the affected boundary and an ADR/change request MUST be raised. The agent MUST NOT resolve a shared-contract conflict by invention.

## 0.3 Source-of-truth hierarchy

The following artifacts are authoritative for integration:

contracts/  
├── openapi/  
│ ├── public-control-api-v1.yaml  
│ ├── mailbox-api-v1.yaml  
│ ├── internal-provisioning-api-v1.yaml  
│ └── operations-api-v1.yaml  
├── events/  
│ ├── envelope-v1.schema.json  
│ └── \*.schema.json  
├── errors/  
│ └── error-catalog-v1.yaml  
├── auth/  
│ ├── claims-v1.yaml  
│ ├── roles-v1.yaml  
│ └── permissions-v1.yaml  
├── observability/  
│ └── telemetry-contract-v1.yaml  
└── dns/  
└── domain-record-contract-v1.yaml

The repository specifications SHALL contain readable copies and examples of these contracts, but generated contract artifacts MUST originate from one canonical source. A repository MUST NOT maintain a private fork of a shared schema.

## 0.4 Architecture freeze and exceptions

The v1.0 architecture is considered frozen once all five engineering documents are approved. Changes fall into three classes:

| **Change class**     | **Example**                                                                          | **Approval**                                |
| -------------------- | ------------------------------------------------------------------------------------ | ------------------------------------------- |
| Local implementation | internal class names, query optimization, component refactor without contract change | repository owner                            |
| Shared compatible    | additive optional event field, new API endpoint, new metric                          | architecture owner + affected repo owners   |
| Shared breaking      | identifier semantics, event rename, auth model, data-plane protocol change           | master-contract revision and migration plan |

Emergency security changes MAY be applied immediately when necessary to protect users or mail reputation, but an ADR and contract reconciliation MUST follow before the next normal release.

## 0.5 Architecture principles versus implementation details

This master document intentionally locks:

• service responsibilities and repository ownership;

• externally observable behavior and integration semantics;

• trust boundaries and authentication patterns;

• canonical entity names and identifiers;

• mail-flow invariants;

• durability, consistency, failure and reconciliation semantics;

• security and privacy minimums;

• deliverability and abuse boundaries;

• monitoring, audit and incident requirements;

• availability, performance, backup and recovery objectives;

• standards and compatibility baseline.

The four repository documents will separately define source trees, classes/modules, exact database DDL, code style, detailed screens, daemon configurations, Ansible roles, individual dashboards, exact tests and runbooks.

# 1\. Mission, Scope and Quality Bar

## 1.1 Product mission

Karyalay Email SHALL be an independently operated, multi-tenant business email hosting service capable of hosting customer-owned domains and mailboxes without a commercial mailbox host, white-label email platform, commercial SMTP relay, or third-party outbound delivery provider in the critical mail path.

Karyalay shall operate the customer relationship, control plane, authentication, tenant policy, mail transport, mailbox storage, delivery queues, anti-abuse controls, monitoring, backup and support tooling. Mature open-source infrastructure MAY be used where it is technically strong and replaceable.

The target experience is not "a mail server with a web page." The quality bar is a commercial business mailbox service whose routine customer experience is comparable with established hosted-email products: reliable sending and receiving, modern webmail, standards-compatible desktop/mobile access, usable administration, migration, security controls, traceable operations and professional deliverability.

## 1.2 Included v1 product capabilities

The complete v1 platform SHALL support at minimum:

• customer organisations and delegated mail administrators;

• customer-owned custom domains;

• automated domain ownership verification and DNS-health checking;

• individual mailboxes with configurable storage quotas;

• aliases and multiple sender identities;

• distribution groups and controlled external members;

• inbound and outbound Internet email;

• authenticated SMTP submission;

• standards-based IMAP access for third-party clients;

• secure webmail with inbox, folders, conversations, search, compose, drafts, attachments, spam/trash and mailbox settings;

• Sieve-based server-side rules, vacation responses and forwarding;

• DKIM signing, SPF support, DMARC policy/reporting support and ARC handling;

• spam and malware filtering;

• mailbox/account security, MFA and app-password support where necessary for legacy clients;

• rate limits and anti-abuse controls at user, domain, organisation, IP-pool and platform levels;

• account/domain suspension and emergency restriction mechanisms;

• mailbox/domain migration from standards-compatible existing providers;

• audit logs, security events, operational telemetry and support diagnostics;

• backup, restoration and disaster-recovery workflows;

• direct-to-MX outbound delivery under Karyalay-controlled reputation;

• staged rollout, capacity management, HA and safe degraded operation.

## 1.3 Explicit v1 non-goals

The following are intentionally outside the first general-availability contract unless later added through a master revision:

• bulk newsletter/marketing-campaign delivery;

• a SendGrid/Mailgun-style public transactional email API;

• legal hold, eDiscovery, journaling and compliance archive products;

• client-side or end-to-end encrypted mailbox semantics that prevent server-side search/filtering;

• calendar/groupware and conferencing;

• native Android/iOS applications;

• globally active-active mailbox storage across multiple continents;

• Karyalay-written replacements for SMTP, IMAP, DNS, cryptographic primitives, antivirus engines or mature spam classifiers.

Future bulk mail MUST use separate sending subdomains, reputation pools and policies from ordinary human/business mail. It MUST NOT be bolted onto ordinary mailbox sending in a way that risks shared IP/domain reputation.

## 1.4 Independence definition

"Independent" means Karyalay controls the data and service behavior and can replace any open-source component without migrating customers to another email provider. It does not mean rebuilding mature standards implementations merely to remove open-source dependencies.

Unavoidable external dependencies include physical/virtual compute suppliers, Internet transit, IP address allocation/announcement, public DNS delegation/registries, trusted public certificate authorities and recipient networks. They MUST be abstracted operationally where practical so one supplier does not become an architectural lock-in.

## 1.5 Quality attributes

Every design decision SHALL be evaluated against these ordered qualities:

**1\.** \*\*No silent mail loss.\*\* Accepted mail must be durably tracked until delivered, explicitly expired/bounced, quarantined under defined policy, or recoverably stored.

**2\.** \*\*Security and tenant isolation.\*\* A mistake must not expose another organisation's mail or credentials.

**3\.** \*\*Deliverability and reputation protection.\*\* One compromised tenant must not easily damage the entire platform.

**4\.** \*\*Recoverability.\*\* Failures are expected; irrecoverable ambiguity is not.

**5\.** \*\*Interoperability.\*\* Standards-compliant mail clients and remote MTAs must work predictably.

**6\.** \*\*Observability.\*\* Operators must be able to explain what happened to a message or account without reading random server files manually.

**7\.** \*\*Usability.\*\* The mailbox and admin experiences must be coherent for ordinary business users.

**8\.** \*\*Scalability.\*\* Growth should be achieved primarily by adding nodes and redistributing placement, not redesigning core semantics.

**9\.** \*\*Maintainability.\*\* Future engineers must be able to understand and safely change the system.

**10\.** \*\*Cost discipline.\*\* Avoid complexity that is not required by current scale, while keeping the architecture migration-friendly.

# 2\. Non-Negotiable Architectural Principles

## 2.1 Critical-path ownership

**MUST: Karyalay SHALL directly operate SMTP acceptance, authenticated submission, outbound queues, DKIM signing, mailbox delivery, IMAP access and mailbox storage. No commercial SMTP relay or white-label mailbox provider may be silently inserted into this path.**

Temporary third-party emergency routing is not part of the normal architecture and would require an incident-level, explicitly approved contingency with customer/security implications documented.

## 2.2 Build product logic; reuse solved protocol infrastructure

The platform SHALL use proven open-source protocol components unless a written ADR establishes that they no longer meet requirements. Karyalay engineering effort is concentrated on control-plane behavior, user experience, provisioning, migration orchestration, anti-abuse policy, observability, support and the integrations between those components.

## 2.3 Control plane and data plane are separate

The control plane manages desired state. The mail data plane continues delivering and serving already-provisioned mail during a reasonable control-plane outage.

CONTROL PLANE  
Karyalay Mail API → desired state → provisioning/reconciliation → directory projections  
<br/>DATA PLANE  
SMTP/Submission → filtering → queues → LMTP → mailbox storage → IMAP/mailbox gateway

A routine outage of the customer billing/admin UI MUST NOT stop existing users from receiving email or cause accepted SMTP queues to disappear.

## 2.4 No browser-to-IMAP design

Browser webmail SHALL NOT connect directly to Dovecot IMAP or Postfix SMTP using user credentials. karyalay-webmail consumes authenticated Karyalay HTTP APIs. The server-side mailbox gateway owned by karyalay-mail translates product operations into mailbox/data-plane operations.

This provides one authorization boundary, one audit model and one stable product API while retaining IMAP/SMTP compatibility for external mail clients.

## 2.5 Desired state and reconciliation

Provisioning uses desired-state semantics. A control-plane database record saying "active" is insufficient. Infrastructure state MUST carry a generation/revision, and a resource becomes operationally ACTIVE only when required projections are applied and health checks validate them.

Every asynchronous provisioning action MUST be safely retryable and reconcilable.

## 2.6 Durable integration

Cross-repository state changes that must not be lost SHALL use a transactional outbox or equivalent durable handoff. Event delivery is at-least-once; consumers are idempotent. "Best effort HTTP webhook" is not acceptable for critical provisioning or security transitions.

## 2.7 Queue ownership

Postfix's queue is the authoritative SMTP delivery queue. Application code MUST NOT create a second competing queue for already-submitted RFC 5322 messages. Application/background-job queues may orchestrate provisioning, migration, notifications and analysis, but outbound message delivery after SMTP acceptance belongs to the MTA.

## 2.8 Default-deny administration

Administrative and service permissions are least-privilege and explicit. Cross-tenant access is denied by default. Content access by support staff is NOT a normal support permission.

## 2.9 Safe degradation

When dependency health is uncertain, the system SHALL prefer temporary deferral/retry over accepting data it cannot durably preserve or silently discarding mail. Email protocols are designed to retry transient failures; Karyalay SHALL use that property deliberately.

# 3\. System Context and Product Boundaries

## 3.1 External actors

| **Actor**                  | **Relationship**                                                                     |
| -------------------------- | ------------------------------------------------------------------------------------ |
| Mailbox user               | Reads/sends/manages own mailbox through webmail or standard clients                  |
| Organisation owner         | Controls organisation-level subscription and highest customer admin authority        |
| Mail administrator         | Manages domains, mailboxes, aliases, groups and mail policies within an organisation |
| Helpdesk administrator     | Performs defined non-sensitive account/support actions                               |
| Remote sender MTA          | Sends Internet mail to Karyalay MX                                                   |
| Remote recipient MX        | Receives direct outbound Internet mail from Karyalay                                 |
| DNS operator               | May be customer, Karyalay or third party; publishes required domain records          |
| Karyalay platform operator | Operates infrastructure and availability, not customer content by default            |
| Security/abuse analyst     | Investigates compromise/abuse using governed telemetry and controls                  |
| Deliverability analyst     | Monitors sending reputation and remote-provider behavior                             |
| Migration operator         | Executes/monitors mailbox imports under customer authorization                       |

## 3.2 Logical system context

INTERNET  
┌──────────────┼───────────────┐  
│ │ │  
Remote MTAs DNS ecosystem Remote MXs  
│ │ ▲  
▼ │ │  
MX EDGE ─────── DNS ─────── OUTBOUND MTA  
│ ▲  
▼ │  
FILTERING SUBMISSION  
│ ▲  
▼ │  
LMTP users/clients  
│ │  
▼ │  
MAILBOX STORAGE ◄── DOVECOT ──────────┘  
▲  
│  
Mailbox Gateway/API ◄── Karyalay Webmail  
▲  
│  
Karyalay Control Plane ◄── Admin/customer UI  
│  
├── identity  
├── provisioning/reconciliation  
├── billing/quotas/policy  
├── events/audit  
└── Ops/abuse/migration/reputation

## 3.3 Service boundaries

The architecture distinguishes:

• \*\*Internet SMTP edge\*\*: accepts or defers inbound remote MTA traffic.

• \*\*Submission edge\*\*: authenticated user/client outbound SMTP.

• \*\*Filtering/policy layer\*\*: authentication validation, spam/malware, outbound abuse controls, signing.

• \*\*Mailbox service\*\*: LMTP delivery, IMAP, Sieve, mailbox metadata/indexes and physical message storage.

• \*\*Mailbox gateway\*\*: server-side product adapter offering webmail-safe APIs without exposing protocol credentials to browsers.

• \*\*Control plane\*\*: customer entities, desired state, policy, lifecycle, auth references, subscription/quota and provisioning orchestration.

• \*\*Operations plane\*\*: migrations, diagnostics, reputation, abuse cases, recovery and maintenance workflows.

• \*\*Observability plane\*\*: metrics, logs, traces, alerting and audit pipelines with access controls.

## 3.4 Data ownership

The control database is authoritative for commercial/customer configuration. Dovecot/mailbox storage is authoritative for mailbox message state. Postfix queues are authoritative for accepted undelivered SMTP messages. Rspamd/Redis data is operational/filtering state, not a customer source of truth. Audit storage is append-oriented evidence and must not be reconstructed solely from application logs.

# 4\. Repository Responsibilities and Dependency Direction

## 4.1 Canonical repositories

| **Repository**          | **Owns**                                                                                                                                                                                          | **MUST NOT own**                                                                                                   |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| \`karyalay-mail\`       | control plane, domain/mailbox lifecycle, public/internal APIs, mailbox gateway, policy state, provisioning orchestration, customer/admin security, billing/entitlements integration, canonical DB | Postfix/Dovecot host configuration, infrastructure deployment, migration engine implementation, browser UI         |
| \`karyalay-webmail\`    | web mailbox UX, compose/reading/search/folders/settings UI, client state, accessibility/responsiveness, calls to mailbox/control APIs                                                             | direct IMAP/SMTP credentials, authoritative mailbox data, tenant admin business logic, infrastructure provisioning |
| \`karyalay-mail-infra\` | hosts/networks, Postfix, Dovecot, Rspamd, ClamAV, Redis, DNS, TLS, storage, load balancing, config projections, monitoring plumbing, backup infrastructure, Ansible                               | customer business workflows, billing, web UI, migration product orchestration, support case policy                 |
| \`karyalay-mail-ops\`   | migrations, abuse workflows, deliverability/reputation analysis, diagnostics, restoration orchestration, maintenance/capacity jobs, operational consoles/workflows                                | canonical mailbox/domain lifecycle, core webmail UI, raw infrastructure configuration source of truth              |

## 4.2 Dependency direction

karyalay-webmail  
│  
▼  
karyalay-mail ───────► shared contracts  
│  
▼  
provisioning contract  
│  
▼  
karyalay-mail-infra  
<br/>karyalay-mail-ops ─────► karyalay-mail APIs/events  
│  
└──────────────► infra operational APIs/telemetry

No repository is permitted to bypass an owning repository merely because a database table or daemon is technically reachable.

Examples:

• Webmail MUST call the mailbox API to create a draft; it MUST NOT write mailbox indexes or Dovecot state directly.

• Ops MUST call a defined suspend/restrict API; it MUST NOT change the canonical \`mailboxes.status\` row directly.

• Infra MAY consume a read-only configuration projection but MUST NOT become the source of customer subscription truth.

• \`karyalay-mail\` MUST NOT SSH into arbitrary nodes to mutate configuration; it submits desired state to the provisioning boundary.

## 4.3 Shared-contract repository/package

The shared machine-readable contracts SHOULD live in a dedicated versioned package or top-level contracts repository that all four projects consume in CI. If organisational constraints keep them in one of the four repositories, that location is treated as logically independent and write access is restricted.

## 4.4 Cross-repository ownership rule

**Rule: every persisted entity, API operation, event, security decision and operational workflow MUST have exactly one authoritative owner. Other repositories may cache, project, display, react to or request changes, but they do not become co-authorities.**

# 5\. Technology and Open-Source Component Baseline

## 5.1 Approved baseline

| **Capability**            | **Baseline**                                                       | **Architectural role**                                                             |
| ------------------------- | ------------------------------------------------------------------ | ---------------------------------------------------------------------------------- |
| SMTP MTA/queue            | Postfix                                                            | inbound SMTP, authenticated submission integration, outbound queue/direct delivery |
| IMAP/LMTP/Sieve           | Dovecot CE 2.4 generation                                          | mailbox protocol access, LMTP local delivery, server-side filters/quotas           |
| Filtering/auth/signing    | Rspamd                                                             | spam classification, SPF/DKIM/DMARC/ARC, DKIM signing, rate/reputation hooks       |
| Malware scan              | ClamAV                                                             | attachment/message malware scanning                                                |
| Relational state          | MariaDB                                                            | canonical control-plane relational state and selected directory projections        |
| Fast operational state    | Redis-compatible                                                   | Rspamd statistics/rate state, cache/short-lived coordination where justified       |
| Recursive DNS             | Unbound                                                            | local recursive DNS for mail/filtering nodes                                       |
| Authoritative DNS         | NSD or equivalent authoritative-only server                        | Karyalay-operated zones where used                                                 |
| L4/L7 proxy               | HAProxy                                                            | appropriate TCP/HTTP load distribution and health routing                          |
| Identity                  | Keycloak or Karyalay-compatible OIDC provider                      | OIDC/OAuth identity, MFA/federation engine; Karyalay owns product IAM semantics    |
| Observability             | OpenTelemetry + Prometheus-compatible metrics + Grafana            | common telemetry model and operator visualization                                  |
| Infrastructure automation | Ansible                                                            | reproducible node configuration and service deployment                             |
| Backups                   | restic-class encrypted content-addressed backup + native snapshots | independent encrypted backup/recovery                                              |

## 5.2 Component version policy

Repository specifications SHALL pin supported major/minor versions in release manifests, not in this master contract. The following rules apply:

• only currently maintained upstream release lines may enter production;

• security updates are evaluated continuously and have an expedited release path;

• major-version upgrades require staging compatibility tests and rollback plans;

• daemon defaults are not considered policy; all security/delivery-critical behavior is explicitly configured;

• unsupported plugins or abandoned forks require an ADR and replacement plan;

• open-source licenses must be inventoried and release obligations met.

## 5.3 Replacement principle

Open-source components are implementation dependencies, not product authorities. Canonical customer data models and public APIs MUST avoid exposing unnecessary component-specific identifiers or configuration formats. This allows a future replacement of, for example, the spam engine or mailbox backend without changing the customer-facing Karyalay model.

# 6\. Canonical Domain Model and Identifier Rules

## 6.1 Core entity graph

Organisation  
├── Membership / Roles  
├── Subscription / Entitlements  
└── MailDomain  
├── DomainVerification  
├── DKIMKeySet  
├── DomainPolicy  
├── Mailbox  
│ ├── MailboxIdentity  
│ ├── Alias  
│ ├── ForwardingRule  
│ ├── VacationRule  
│ ├── SieveFilterSet  
│ ├── AppPassword  
│ ├── MailboxPlacement  
│ └── Usage/Quota  
└── DistributionGroup  
<br/>Infrastructure  
├── MailNode  
├── StorageNode  
├── SMTPPool  
├── IPAddress  
└── PlacementGeneration  
<br/>Operations  
├── MigrationJob  
├── AbuseCase  
├── SecurityEvent  
├── RestoreJob  
└── IncidentReference

## 6.2 Identifier requirements

• Canonical business entities MUST use UUIDs.

• UUIDv7, as standardized by RFC 9562, is preferred for newly generated identifiers because it remains globally unique while providing time-ordering properties useful for distributed database/index workloads.

• Identifiers exposed in APIs are opaque to clients; clients MUST NOT infer creation time, shard or permission from the UUID.

• Natural keys such as email address or domain are never the sole immutable primary key.

• Every resource that participates in reconciliation SHALL carry an integer or monotonic \`generation\`/\`desired_generation\` field.

• Event IDs, request IDs, trace IDs and idempotency keys are separate concepts and MUST NOT be overloaded.

## 6.3 Canonical naming

The following names are normative across schemas, APIs and telemetry:

| **Concept**               | **Canonical field** |
| ------------------------- | ------------------- |
| Tenant                    | \`organisation_id\` |
| Hosted domain             | \`domain_id\`       |
| Mailbox                   | \`mailbox_id\`      |
| User/identity             | \`identity_id\`     |
| Mail node                 | \`mail_node_id\`    |
| Storage node              | \`storage_node_id\` |
| SMTP/IP pool              | \`smtp_pool_id\`    |
| Migration                 | \`migration_id\`    |
| Abuse case                | \`abuse_case_id\`   |
| Request correlation       | \`request_id\`      |
| Distributed trace         | \`trace_id\`        |
| Resource desired revision | \`generation\`      |

No repository may substitute tenant_id, company_id, account_id, user_mail_id or similar synonyms at shared boundaries.

## 6.4 Domain canonicalization

Hosted domains SHALL be stored and compared in canonical DNS form. Internationalized domain names are normalized to an IDNA A-label representation for DNS/routing keys while the user-facing Unicode form MAY also be retained for display. Domain names are case-insensitive.

## 6.5 Local-part policy

SMTP technically allows case-sensitive local-parts, but Karyalay-hosted mailbox/alias uniqueness SHALL be case-insensitive within a hosted domain for predictable business behavior. Original display casing MAY be retained.

SMTPUTF8 transport support is required for interoperability. However, v1 mailbox/alias creation SHOULD default to ASCII local-parts until internationalized local-part creation, validation, client compatibility and operational tooling have passed the dedicated certification suite.

## 6.6 Address identity distinction

A **mailbox** is a storage/security principal. An **address/identity** is an address authorized to receive and/or send. Multiple aliases/identities may resolve to one mailbox. APIs MUST NOT assume one address equals one mailbox.

# 7\. Multi-Tenancy and Isolation Model

## 7.1 Tenant boundary

organisation_id is the primary commercial and authorization tenant boundary. A custom domain belongs to exactly one active organisation at a time. Mailboxes, aliases and groups inherit that boundary through their domain and explicit organisation reference.

## 7.2 Isolation requirements

• Every control-plane query involving tenant-owned data MUST include or derive the authorised \`organisation_id\` boundary.

• Object-level authorization is required even if a UUID is difficult to guess.

• Unique database constraints involving email addresses/domains MUST be designed so cross-tenant collisions cannot create ambiguity.

• Cache keys MUST include tenant/resource identity where tenant data is cached.

• Search indexes and mailbox gateway requests MUST be scoped to the authenticated mailbox/authorised admin context.

• Logs MUST NOT accidentally leak another tenant's addresses/content through error responses.

• Provisioning projections MUST include stable resource IDs and organisation IDs so stale rows cannot be attached to the wrong tenant.

## 7.3 Shared infrastructure versus dedicated isolation

The standard service uses shared infrastructure with logical isolation. Higher tiers MAY later provide dedicated outbound IP pools, storage nodes or clusters. Dedicated infrastructure is an entitlement/placement decision and MUST NOT create a different customer data model.

## 7.4 Tenant deletion

Organisation deletion is a governed workflow, not a database cascade. It MUST freeze new mail changes, determine domain release policy, stop new deliveries at an explicit stage, expire/revoke credentials, preserve recoverable backups for the published window, create deletion/audit evidence and eventually remove tenant content according to retention policy.

## 7.5 No cross-tenant global mailbox administrator

Normal organisation admins cannot see or manipulate other tenants. Platform support roles are separately governed and audited. A platform-level "super admin" MUST be a break-glass capability with strong MFA, short-lived elevation, reason capture, alerting and immutable audit records.

# 8\. Trust Zones, Network Boundaries and Service Topology

## 8.1 Trust zones

| **Zone**        | **Examples**                                         | **Trust posture**               |
| --------------- | ---------------------------------------------------- | ------------------------------- |
| Public Internet | remote MTAs, browsers, mail clients                  | untrusted                       |
| Public edge     | MX, submission, HTTPS load balancers                 | hostile-input boundary          |
| Application     | control API, mailbox gateway, web backend            | authenticated service zone      |
| Mail internal   | LMTP/IMAP backends, filtering, directory projections | restricted service network      |
| Data            | MariaDB, Redis, mailbox storage                      | no direct public access         |
| Management      | Ansible/SSH/bastion, monitoring administration       | privileged, strongly restricted |
| Backup          | backup targets and restore workers                   | isolated, encryption-required   |
| Observability   | collectors, metrics/log stores                       | sensitive metadata zone         |

## 8.2 Network invariants

• Public database ports are forbidden.

• Public Redis is forbidden.

• Mailbox filesystem shares are never Internet-accessible.

• Management SSH is not exposed indiscriminately to the Internet; access is through approved management paths with MFA/device controls where possible.

• Service-to-service traffic is authenticated where the protocol supports it; network location alone is not authorization.

• Firewall policy is default-deny between zones and is represented as code in \`karyalay-mail-infra\`.

• Outbound Internet access from internal services is limited to documented needs.

## 8.3 Public protocol endpoints

The initial public service may expose:

| **Port** | **Protocol** | **Purpose**                                                 |
| -------- | ------------ | ----------------------------------------------------------- |
| 25/TCP   | SMTP         | server-to-server inbound; outbound initiated from MTA nodes |
| 465/TCP  | submissions  | authenticated implicit-TLS message submission               |
| 587/TCP  | submission   | authenticated STARTTLS message submission                   |
| 993/TCP  | IMAPS        | secure IMAP for external clients                            |
| 995/TCP  | POP3S        | optional; disabled unless product decision enables POP      |
| 4190/TCP | ManageSieve  | optional external server-side rules management              |
| 443/TCP  | HTTPS        | webmail, control APIs, autoconfiguration/MTA-STS endpoints  |

Plaintext POP3/IMAP ports SHOULD remain closed. STARTTLS-capable legacy ports are not exposed merely for compatibility unless a documented business requirement and security review exists.

## 8.4 Node-role separation

Small beta environments MAY combine roles, but production logical roles remain explicit: MX/filter nodes, submission/outbound nodes, mailbox/storage nodes, control/API nodes, database nodes, DNS resolvers/authoritative nodes, observability nodes and backup targets. The configuration model MUST support later separation without changing resource semantics.

# 9\. Identity, Authentication and Session Architecture

## 9.1 Identity separation

Karyalay identity and mailbox identity are related but distinct. A human Karyalay identity may be entitled to one or more mailboxes; a mailbox may also exist as a functional/shared mailbox without an independently interactive Karyalay user until shared-mailbox functionality is formally enabled.

The control plane MUST model:

• human identity;

• organisation membership;

• role/permission grants;

• mailbox ownership/access grants;

• protocol credentials/app passwords;

• active sessions/devices;

• MFA authenticators and recovery state;

• service identities.

A mailbox password MUST NOT become the canonical Karyalay account password.

## 9.2 Browser authentication

Browser-facing Karyalay Email applications SHALL use OIDC Authorization Code flow with PKCE and secure server/client practices appropriate to the chosen architecture. Tokens are short-lived; refresh/session state is revocable. Browser applications MUST NOT persist long-lived bearer tokens in insecure browser storage.

MFA SHOULD be strongly encouraged for all users and REQUIRED for organisation owners, mail administrators and privileged Karyalay staff. The product architecture SHALL support phishing-resistant authenticators/passkeys as the preferred stronger method, with recovery mechanisms that do not negate the assurance of MFA.

## 9.3 Legacy mail-client authentication

External IMAP/SMTP clients SHOULD use OAuth mechanisms such as OAUTHBEARER/XOAUTH2 when supported by the client and Dovecot/auth stack. Because many existing mail clients/devices still require password-style authentication, Karyalay MAY issue app passwords under these rules:

• app passwords are separate from the user's primary login password;

• created only after strong reauthentication;

• display the secret once;

• store only a secure verifier/hash where protocol mechanics allow;

• bind to a mailbox and optionally a named device/purpose;

• can be individually revoked;

• are listed with created/last-used metadata;

• can be globally disabled by organisation policy;

• trigger security events on suspicious use;

• are automatically revoked when the mailbox is permanently deleted or a security reset requires it.

## 9.4 Password requirements

Password handling SHALL follow current NIST SP 800-63B-4 principles rather than obsolete composition folklore. The repository specification shall set exact length and blocklist requirements. Passwords MUST be salted and hashed with a current memory-hard password hashing algorithm approved by Security; plaintext or reversible storage is prohibited.

## 9.5 Session model

Every interactive session SHALL have a unique session ID, identity ID, authentication time, last activity, client/device metadata, risk metadata and revocation state. Users must be able to view and revoke their sessions. Privileged role changes, password/security reset and confirmed compromise MUST support broad session revocation.

## 9.6 Service-to-service identity

Internal services SHALL authenticate as named service identities. Preferred pattern: mutually authenticated TLS between services combined with short-lived scoped workload tokens or equivalent workload identity. Static shared API keys are not the default architecture.

Each internal token MUST state audience and scopes. A token issued for mail-ops MUST NOT automatically authorize provisioning-admin operations.

## 9.7 Authentication event requirements

The security-event stream SHALL record, at minimum:

• successful/failed login;

• MFA enrollment/removal/challenge failure;

• app-password creation/revocation/use anomaly;

• password reset/recovery;

• session creation/revocation;

• suspicious IP/device/risk signal;

• administrative impersonation or delegated access;

• service-identity authentication failure.

Events SHALL avoid secrets and message content.

# 10\. Authorization and Administrative Privilege Model

## 10.1 Authorization pattern

Authorization combines role-based permissions with object/tenant checks. Roles are bundles for usability; permissions are the enforcement primitive. APIs SHALL check permissions server-side for every protected operation.

## 10.2 Customer roles baseline

| **Role**           | **Baseline purpose**                                                                                            |
| ------------------ | --------------------------------------------------------------------------------------------------------------- |
| \`org_owner\`      | highest customer authority, subscription ownership, administrator appointment, destructive organisation actions |
| \`mail_admin\`     | domains, mailboxes, aliases, groups, domain policy and routine security administration                          |
| \`helpdesk_admin\` | limited password/session/mailbox support without high-risk domain/policy/destructive powers                     |
| \`security_admin\` | security policy, sessions, MFA enforcement, security events and account restriction                             |
| \`billing_admin\`  | plan, invoices, storage/purchased entitlements; no mailbox-content power                                        |
| \`auditor\`        | read-only approved audit/security views                                                                         |
| \`mailbox_user\`   | own mailbox, preferences, identities/aliases as allowed, own sessions/security                                  |

The detailed permission matrix is in Appendix B and the repository spec. Roles MUST be tenant-scoped.

## 10.3 Platform roles baseline

| **Role**                   | **Baseline purpose**                                                                  |
| -------------------------- | ------------------------------------------------------------------------------------- |
| \`platform_ops\`           | infrastructure/service health and controlled operational actions                      |
| \`platform_support\`       | customer troubleshooting with metadata access; no default content access              |
| \`platform_security\`      | security incident controls and privileged investigations                              |
| \`abuse_analyst\`          | outbound/inbound abuse cases, restriction recommendations/actions according to policy |
| \`deliverability_analyst\` | IP/domain/provider reputation and delivery diagnostics                                |
| \`platform_billing\`       | commercial subscription support                                                       |
| \`break_glass_admin\`      | exceptional emergency authority; no standing everyday use                             |

## 10.4 Sensitive operations

High-risk operations SHALL require reauthentication and/or additional confirmation. Examples include:

• disable MFA;

• reveal/generate an app password;

• change primary domain ownership;

• delete a mailbox/domain/organisation;

• change external forwarding policy;

• export account/security data;

• elevate another administrator;

• release a suspended/compromised mailbox;

• access customer message content under a future governed support/legal feature;

• rotate/recover critical domain keys.

## 10.5 Support access

Support interfaces should solve routine cases through metadata: queue IDs, SMTP response, message IDs/hashes, timestamps, authentication results, mailbox quota, DNS status, migration status and client errors. Message body/attachment access is not part of baseline support authority.

If future content-assisted support is added, it requires explicit user/org authorization where applicable, reason capture, time-limited access, content-access audit, and separate security/privacy approval.

# 11\. Secrets, Cryptographic Keys and Certificate Management

## 11.1 Secret classes

Secrets include database credentials, service credentials, OAuth client secrets, app-password verifiers, DKIM private keys, TLS private keys, backup encryption keys, signing keys, recovery tokens and infrastructure bootstrap credentials.

Each secret class MUST have an owner, storage mechanism, access policy, rotation policy, compromise procedure and recovery method.

## 11.2 General secret rules

• Secrets MUST NOT be committed to Git, container images, sample configuration, tickets, general application logs or crash dumps.

• Production secrets MUST be injected through an approved secret-management mechanism or protected local secret file generated by deployment automation.

• File permissions and service users SHALL enforce least privilege.

• Long-lived credentials SHOULD be eliminated where workload identity/short-lived credentials are practical.

• Rotation must support overlap when the consuming protocol requires zero-downtime transition.

• Revocation paths must be tested.

## 11.3 DKIM key architecture

Each customer domain SHALL have independently managed DKIM signing material. Karyalay MUST NOT use one universal signing key for unrelated customer domains.

Baseline:

• RSA 2048-bit DKIM keys are supported as the broad-compatibility default;

• selectors are generated/managed by Karyalay and are versioned;

• private keys remain only in approved signing/security boundaries;

• public keys are published through DNS contract records;

• planned rotation uses overlapping selectors so in-flight/queued messages and DNS caches remain valid;

• old selectors are retained for a defined safe verification period before retirement;

• key access and rotation are auditable;

• future support for additional DKIM algorithms requires interoperability testing and an ADR.

## 11.4 TLS certificates

Public SMTP/IMAP/HTTPS endpoints use publicly trusted certificates obtained through ACME where possible. Certificate issuance/renewal is automated and monitored. Renewal failures alert well before expiry.

Internal TLS certificates MAY use a private Karyalay CA/workload identity system. Private CA trust MUST never be confused with public client trust.

## 11.5 Backup encryption keys

Backup encryption keys are stored independently from backup repositories and from the machines being backed up. At least two authorized recovery custodians/processes must make restoration possible without creating an uncontrolled single-person secret.

# 12\. Customer Domain Onboarding and DNS Architecture

## 12.1 Domain lifecycle

Canonical domain lifecycle:

REQUESTED  
↓  
OWNERSHIP_PENDING  
↓  
VERIFIED  
↓  
CONFIGURING  
↓  
READY_FOR_CUTOVER  
↓  
ACTIVE  
↓  
SUSPENDED / DELETING / RELEASED

Mailbox provisioning MAY occur before MX cutover so a migration can be staged. A domain MUST NOT become fully ACTIVE merely because the ownership TXT record exists; required service records and routing readiness must be evaluated.

## 12.2 Ownership verification

The control plane issues a high-entropy, domain-specific verification token published as a TXT record under an approved name. Verification tokens:

• are scoped to a domain and organisation;

• expire or can be rotated;

• are never accepted for a different domain;

• must be revalidated during sensitive domain transfer flows;

• are not authentication credentials for mailbox access.

## 12.3 DNS record contract

The onboarding engine SHALL generate and continuously evaluate at least:

• MX records pointing to Karyalay ingress names;

• SPF TXT record or include strategy appropriate to Karyalay outbound infrastructure;

• per-domain DKIM selector TXT records;

• DMARC TXT record and recommended policy progression;

• autoconfig/autodiscover records/endpoints where supported;

• A/AAAA records for relevant service hostnames;

• PTR/reverse DNS for Karyalay-owned sending IPs through the IP provider/delegation path;

• MTA-STS policy host/TXT record where enabled;

• TLS-RPT record where enabled;

• optional CAA/DNSSEC recommendations/management for Karyalay-hosted DNS zones.

## 12.4 DNS health state

Each required/recommended record SHALL be represented as a machine-readable check with status such as PASS, WARN, FAIL, PENDING, NOT_APPLICABLE, plus observed values, expected values, resolver timestamp and remediation guidance.

A single green "DNS configured" boolean is insufficient.

## 12.5 SPF strategy

The platform SHALL maintain a stable Karyalay SPF include domain so outbound IP changes do not require editing every customer domain. The include tree MUST remain below practical DNS-lookup limits and must not become deeply nested. Dedicated-IP customers MAY have additional mechanisms.

SPF is not used as authorization to send arbitrary From addresses; sender authorization is enforced by the submission/control plane.

## 12.6 DMARC strategy

Current DMARC behavior SHALL be based on the current standards-track DMARC specification, RFC 9989, and current reporting RFCs. Onboarding SHOULD begin with a monitoring-friendly policy where appropriate and guide administrators toward stronger enforcement after legitimate senders are aligned. Karyalay MUST NOT automatically publish an aggressive reject policy that will break a customer's known legitimate third-party senders without explicit validation/consent.

Aggregate reports are operational/security data and SHALL be parsed through a controlled pipeline. Failure reports may contain sensitive message information and therefore require stricter privacy handling if enabled.

## 12.7 Customer-managed versus Karyalay-managed DNS

The product supports:

**1\.** \*\*Customer-managed DNS:\*\* display exact required records, verify them, never assume immediate propagation.

**2\.** \*\*Karyalay-managed authoritative DNS:\*\* control plane can create/rotate relevant records automatically through an internal DNS API.

The logical DomainRecordRequirement model is the same in both modes.

# 13\. Inbound Mail Flow Contract

## 13.1 Canonical inbound flow

Remote MTA  
│ SMTP/25  
▼  
Postfix ingress  
│ connection/envelope controls  
▼  
Rspamd policy/filtering  
├─ SPF validation  
├─ DKIM validation  
├─ DMARC evaluation  
├─ ARC validation  
├─ reputation / DNS intelligence  
├─ spam classification  
└─ ClamAV integration  
│  
▼  
Postfix accepted queue  
│  
▼ LMTP  
Dovecot LMTP  
├─ recipient/quota validation  
├─ Sieve  
└─ mailbox delivery  
│  
▼  
Mailbox storage + indexes

## 13.2 Acceptance invariant

**Invariant: once Karyalay returns a successful final SMTP acceptance for a message, the platform owns responsibility for the message and MUST retain sufficient durable state to deliver it, intentionally quarantine it under policy, or generate a standards-appropriate delivery failure. It MUST NOT disappear because an application process restarted.**

Pre-acceptance checks SHOULD reject permanent invalid recipients during SMTP conversation rather than accept then backscatter. Temporary internal failures SHOULD normally result in a temporary 4xx deferral before final acceptance when safe delivery cannot be guaranteed.

## 13.3 Recipient lookup

The ingress MTA uses a read-optimized directory projection generated from canonical control-plane state. The projection contains only routing fields needed by the mail plane and is versioned/generation-aware. It SHOULD remain usable during control-plane API outage.

Recipient resolution covers:

• active mailbox addresses;

• active aliases;

• distribution groups;

• explicit catch-all only where enabled;

• plus-addressing/subaddressing according to domain/mailbox policy;

• suspended/deleting domain/mailbox states;

• routing-loop prevention.

## 13.4 Anti-backscatter rule

Karyalay SHALL avoid accepting mail to nonexistent recipients merely to generate a later bounce. Recipient validation should happen before final acceptance whenever possible. DSNs generated after acceptance must follow SMTP/message standards and never create reflection loops.

## 13.5 Spam handling

Spam policy distinguishes outright protocol rejection, quarantine/Junk placement, tagging and accept. The exact score thresholds belong to Infra/Ops policy, but these invariants apply:

• obvious malware/high-confidence abusive messages MAY be rejected before acceptance;

• uncertain spam should generally be delivered to Junk rather than silently dropped;

• user/admin allow/block mechanisms cannot bypass mandatory malware/platform safety controls;

• filtering actions and reasons are observable and explainable to operators;

• message content used for classifier learning is handled under privacy rules.

## 13.6 Quota behavior

Recipient quota SHOULD be checked early enough to reduce accepted-undeliverable mail while accounting for race conditions. If a mailbox becomes over quota after acceptance, the message remains the platform's responsibility and is retried/handled under defined LMTP/queue policy; it is not silently discarded.

## 13.7 Internal delivery

Mail between two Karyalay-hosted domains still passes required submission/auth/policy controls. An internal-delivery optimization MAY avoid unnecessary Internet routing but MUST preserve authentication/audit semantics and must not become a bypass around abuse policy.

# 14\. Outbound Submission and Delivery Contract

## 14.1 Submission endpoints

Authenticated users/clients submit via SMTP submission (465/587) or the server-side webmail send API. Port 25 is not a user submission endpoint.

TLS is mandatory before credentials. Legacy plaintext authentication over unencrypted transport is prohibited.

## 14.2 Canonical outbound flow

Webmail / SMTP client  
│  
▼  
Authentication + mailbox authorization  
│  
▼  
Envelope / From identity authorization  
│  
▼  
Outbound Rspamd / abuse policy  
│  
├─ rate / recipient / anomaly checks  
├─ malware / prohibited-content policy where applicable  
└─ DKIM signing  
│  
▼  
Postfix outbound queue  
│  
├─ DNS MX lookup  
├─ TLS / policy negotiation  
├─ retry scheduling  
└─ DSN generation  
│  
▼  
Remote recipient MX

## 14.3 Sender authorization

Authentication to mailbox A does not authorize arbitrary From: values. The sender must be:

• the mailbox primary address;

• an active alias/identity explicitly authorized to that mailbox;

• a delegated/shared address the identity has send permission for;

• a system-approved special sender.

Envelope sender and header sender are set according to authentication/bounce/DMARC policy. Spoofing another customer domain or unowned Internet domain is prohibited.

## 14.4 Direct-to-MX delivery

Normal outbound mail is delivered directly from Karyalay-managed MTA/IP pools to recipient MX servers. DNS, HELO/EHLO identity, PTR, SPF, DKIM, DMARC alignment and TLS posture must remain coherent for each sending pool.

## 14.5 SMTP queue semantics

After successful submission to the MTA, Postfix queue ID and platform message correlation metadata SHALL be captured for diagnostics. Remote 4xx responses result in retry according to MTA policy. Remote 5xx permanent responses result in a DSN/bounce where appropriate. Queue expiry is explicitly configured and monitored.

The user interface MAY expose human-readable delivery state when reliable signals are available, but MUST NOT falsely equate "accepted by Karyalay" with "delivered to recipient inbox."

## 14.6 Message size and recipients

Platform-wide maximum message size, per-plan limits and recipient-count limits are explicit configuration. Webmail compose validates before upload/send where possible; SMTP enforces independently. Limits include MIME/base64 overhead considerations.

## 14.7 Outbound abuse gate

A message can be rejected or temporarily deferred at submission for account/tenant restriction, anomalous volume, prohibited bulk behavior, malicious payload or policy violation. Such enforcement returns a stable machine-readable/SMTP diagnostic and creates an abuse/security signal where appropriate.

## 14.8 Bulk-mail separation

Ordinary mailbox submission is for human/business correspondence and reasonable application-generated mail associated with the account. High-volume newsletters, purchased lists, unsolicited campaigns and bulk marketing are prohibited in the standard pool. A future campaigns product requires separate infrastructure and reputation domains/IP pools.

# 15\. Aliases, Forwarding, Distribution Groups and Auto-Replies

## 15.1 Aliases

An alias maps an accepted local address to one or more valid internal destinations according to product policy. Alias loops are rejected at configuration time where detectable and protected against at delivery time.

Aliases may optionally be authorized sender identities. Receiving an alias does not automatically grant send-as permission unless product policy explicitly does so.

## 15.2 External forwarding

External forwarding is a significant deliverability/authentication risk. Karyalay SHALL implement Sender Rewriting Scheme (SRS) or equivalent envelope strategy for forwarded messages where required to preserve SPF-related behavior and SHALL use ARC appropriately to preserve authentication assessment through indirect flows.

External forwarding rules must:

• be user/admin visible;

• support organisation policy to disable/restrict them;

• protect against loops;

• limit fan-out;

• avoid automatic forwarding of spam/malware when policy indicates;

• generate audit/security events for creation/change;

• avoid exposing internal secrets in rewritten addresses.

## 15.3 Distribution groups

Groups have a stable group ID, address, membership, posting policy and external-member policy. Posting may be limited to organisation members, approved senders or authenticated internal users. Open unauthenticated Internet relays are forbidden.

Group expansion is bounded and observable. Large groups may require separate handling/rate policy but remain distinct from bulk marketing.

## 15.4 Catch-all

Catch-all addresses are disabled by default because they increase spam load, typo acceptance and backscatter complexity. If enabled by an entitled administrator, the UI MUST explain risk, only one effective catch-all target exists per domain, and anti-abuse controls remain intact.

## 15.5 Vacation/auto-replies

Server-side vacation replies use Sieve or an equivalent standards-aware mechanism and MUST avoid loops/storms. They SHALL not reply blindly to mailing-list traffic, bulk/preference headers, spam or automated DSNs. Users can define active window, subject/body and frequency suppression.

# 16\. Internet Mail Standards and Interoperability Baseline

## 16.1 Required standards posture

Karyalay Email is a standards-based Internet mail service. Implementations SHALL treat protocol RFCs as authoritative even where another provider behaves differently. Provider-specific adaptations MAY be added when they do not violate standards or security.

The compatibility baseline includes, at minimum, current or applicable versions of:

| **Area**                       | **Standards / baseline**                                                          |
| ------------------------------ | --------------------------------------------------------------------------------- |
| SMTP transport                 | RFC 5321 and applicable SMTP extensions                                           |
| Internet Message Format        | RFC 5322 and MIME family                                                          |
| Message submission             | RFC 6409 plus submission TLS conventions                                          |
| IMAP                           | RFC 9051 IMAP4rev2 plus required compatibility with widely used IMAP4rev1 clients |
| Email authentication           | RFC 7208 SPF; RFC 6376 DKIM; RFC 9989 DMARC                                       |
| DMARC reports                  | RFC 9990 aggregate reporting; RFC 9991 failure reporting where enabled            |
| Authenticated Received Chain   | RFC 8617 ARC                                                                      |
| SMTP transport security policy | RFC 8461 MTA-STS and RFC 8460 TLS-RPT where enabled                               |
| Internationalized mail         | RFC 6530 family / SMTPUTF8 interoperability                                       |
| UUIDs                          | RFC 9562                                                                          |
| HTTP semantics                 | RFC 9110 family as applicable                                                     |
| API problem responses          | RFC 9457 Problem Details                                                          |
| OAuth/OIDC                     | current stable OAuth/OIDC standards supported by approved identity stack          |

## 16.2 Compatibility targets

GA compatibility tests SHALL cover at least:

• Gmail/Google Workspace send and receive;

• Microsoft Outlook.com/Microsoft 365 send and receive;

• Yahoo send and receive;

• common self-hosted Postfix/Exim peers;

• Apple Mail;

• Outlook desktop where standards support permits;

• Thunderbird;

• current Android/iOS mail clients using standards protocols;

• major browsers for webmail.

## 16.3 Provider policy registry

Gmail, Yahoo, Microsoft and other major recipient networks update sender requirements over time. Those requirements MUST NOT be scattered as magic constants through the codebase. karyalay-mail-ops owns a versioned provider-policy/diagnostic registry referenced by dashboards and runbooks.

The platform SHALL continuously satisfy at least valid forward/reverse DNS, authenticated sending, TLS and low complaint/spam behavior expected by major mailbox providers. Current Gmail guidance, for example, requires SPF or DKIM for all senders and stricter SPF+DKIM+DMARC requirements for high-volume senders, with spam rates kept below 0.3%; Karyalay policy SHOULD target materially better than published failure thresholds.

## 16.4 Interoperability principle

A provider's temporary quirk may justify a workaround, but workarounds must be isolated, documented, tested and removable. The shared canonical model is not redesigned around one recipient provider.

# 17\. Mailbox Storage, Namespace, Quotas and Lifecycle

## 17.1 Storage authority

Mailbox storage and Dovecot-maintained mailbox state are authoritative for message bodies, MIME parts, folder membership, flags and mailbox protocol state. The control-plane MariaDB MUST NOT store complete message bodies or attachments as ordinary application rows.

Control-plane data may store bounded metadata required for product integration, such as mailbox usage snapshots, search task state or message correlation identifiers, but it is not a shadow mailbox database.

## 17.2 Storage format and abstraction

The exact Dovecot storage format is an Infra-spec decision selected for recoverability, performance and supported replication/backup behavior. Application code MUST address mailboxes by canonical mailbox IDs and placement records, never by constructing filesystem paths.

A placement record conceptually contains:

mailbox_id  
storage_node_id  
mail_cluster_id  
desired_generation  
observed_generation  
placement_state  
mailbox_storage_locator # internal, opaque outside infra/mailbox gateway  
created_at  
updated_at

## 17.3 Mailbox namespace

Every new mailbox gets a deterministic set of special-use folders/semantics at first provision, covering Inbox, Sent, Drafts, Junk/Spam, Trash and Archive where the underlying client/protocol behavior supports it. Folder names visible to users may be localized, but special-use semantics are canonical.

Third-party IMAP clients may create arbitrary folders subject to quotas/limits. Webmail SHALL not assume only Karyalay-created folders exist.

## 17.4 Quota model

Quotas exist at multiple layers:

• mailbox storage bytes;

• optional mailbox count per organisation/subscription;

• maximum message size;

• optional message/folder count protective limits;

• organisation aggregate purchased storage where product plans require it.

Dovecot/mail delivery enforces mailbox storage truth. The control plane maintains entitlement and near-real-time usage projection for UI/billing. Disagreement is reconciled from mailbox/storage authority rather than billing counters overriding physical truth.

Quota changes are versioned desired state and apply without mailbox recreation.

## 17.5 Quota thresholds and user experience

The product SHOULD surface warnings before hard exhaustion. A baseline policy may notify at 80%, 90% and 95%, while exact thresholds remain configurable. Notifications must not become a spam loop.

When at hard quota:

• existing mail remains readable;

• users may delete/archive/export according to product capabilities;

• new inbound delivery follows defined quota/LMTP behavior and is never silently lost;

• sending may remain possible if policy permits, but saving Sent/Drafts must be handled explicitly;

• administrators can increase quota subject to entitlement/capacity.

## 17.6 Lifecycle states

Canonical mailbox lifecycle states include at least:

REQUESTED  
PROVISIONING  
ACTIVE  
RESTRICTED  
SUSPENDED  
DEPROVISIONING  
DELETED_RECOVERABLE  
PURGED  
PROVISIONING_FAILED  
RESTORE_PENDING

RESTRICTED is intended for security/abuse controls where selected capabilities (often outbound send/auth) are disabled while mail preservation/inbound receipt may continue according to policy. SUSPENDED is a stronger administrative/commercial state. Exact enforcement matrix is a shared contract, not a UI convention.

## 17.7 Deletion

Mailbox deletion is two-phase or multi-phase:

**1\.** authorise destructive request and reauthenticate where required;

**2\.** enter deletion state and prevent incompatible changes;

**3\.** revoke sessions/app passwords and sender authorization;

**4\.** update recipient/routing state according to deletion policy;

**5\.** preserve mailbox in recoverable storage for the published recovery window;

**6\.** eventually cryptographically/physically purge according to retention capability;

**7\.** retain only permitted audit/commercial metadata.

Recreating the same email address during the recovery window must not accidentally attach the old mailbox storage to the new mailbox ID.

## 17.8 Shared mailbox future-proofing

The model SHALL not hard-code one human identity per mailbox. Delegated read/send permissions and shared mailbox UX may be a later feature. Storage identity and human identity therefore remain separate now.

# 18\. Message Model, Threading, Search and Indexing Boundaries

## 18.1 Message identity

Multiple identifiers exist and MUST be distinguished:

• RFC \`Message-ID\` supplied/generated in the message;

• IMAP UID valid within a UIDVALIDITY/mailbox context;

• Postfix queue ID for a delivery attempt/queue entry;

• Karyalay mailbox API message reference, opaque and scoped to a mailbox;

• thread/conversation ID generated by product logic;

• trace/request IDs for system execution.

None is globally interchangeable.

## 18.2 RFC Message-ID handling

Outbound messages SHOULD have a standards-valid Message-ID generated if the composing client did not provide an acceptable one. Inbound duplicate detection MUST NOT rely solely on Message-ID because legitimate duplicates and malformed/missing IDs exist.

## 18.3 Threading contract

Webmail conversation grouping SHALL use a standards-aware algorithm based primarily on Message-ID, In-Reply-To and References, with bounded subject normalization/fallback where necessary. Subject-only grouping is prohibited as the primary algorithm.

Threading behavior must be deterministic across sessions and reasonably stable across mailbox reindexing. A repository spec shall define edge cases: missing IDs, duplicate IDs, broken references, subject changes, forwarded mail, list prefixes and very long chains.

## 18.4 Search ownership

Mailbox search is a mailbox-service capability exposed through the karyalay-mail mailbox API. Webmail does not maintain an authoritative local search index. Infra may enable Dovecot full-text-search plugins/backends appropriate to scale; the public search query contract remains stable.

## 18.5 Search baseline

The product search grammar SHALL support at least combinations of:

free text  
from:&lt;address/text&gt;  
to:&lt;address/text&gt;  
cc:&lt;address/text&gt;  
subject:&lt;text&gt;  
has:attachment  
is:read | is:unread  
is:starred  
in:&lt;folder/special-use&gt;  
after:&lt;date&gt;  
before:&lt;date&gt;  
larger:&lt;size&gt;  
smaller:&lt;size&gt;

The webmail spec defines UX and parser behavior. The mailbox API owns canonical parsed query semantics. Unsupported/invalid operators return useful validation errors rather than silently changing meaning.

## 18.6 Index rebuild safety

Search indexes are rebuildable derived state. Loss/corruption of an index must not imply loss of message bodies. Reindexing can degrade search performance but must preserve mailbox availability where practical.

## 18.7 Attachment metadata

Attachment name/type/size and safe metadata may be indexed for search/UX, but attachment content extraction is untrusted-input processing and must be sandboxed/resource-limited. Search extractors are never allowed to execute active content.

# 19\. Webmail/Data-Plane Integration Contract

## 19.1 Webmail architecture

karyalay-webmail is a browser application consuming Karyalay HTTPS APIs. It is not an IMAP client running in the browser and does not know Dovecot credentials.

Browser  
│ HTTPS + OIDC session  
▼  
Karyalay Webmail frontend/backend  
│ mailbox/control API  
▼  
karyalay-mail Mailbox Gateway  
│ authenticated internal protocol access  
├── Dovecot / mailbox store  
└── Postfix submission

## 19.2 Required mailbox API surface classes

The shared contract SHALL eventually cover:

• mailbox/folder listing and special-use metadata;

• message list/pagination;

• thread list/thread detail;

• message body/headers retrieval;

• attachment metadata and streamed retrieval;

• flags/read/star operations;

• move/copy/delete/archive/spam actions;

• search;

• draft create/update/delete;

• compose/send/reply/forward submission;

• folder create/rename/delete;

• settings/signatures/sender identities;

• filters, forwarding and vacation state through control APIs;

• mailbox usage/quota;

• safe raw-message/source access if exposed.

## 19.3 Streaming and large payloads

Large attachments and message bodies MUST be streamed rather than buffered entirely in application memory. Uploads use bounded multipart/resumable patterns chosen in the API spec. Backpressure, cancellation, maximum sizes, checksum/integrity checks and temporary-file cleanup are required.

## 19.4 HTML message rendering

Email HTML is hostile input. Webmail MUST:

• sanitize HTML using an allowlist-based, maintained sanitizer;

• strip active scripts, event handlers, forms or dangerous URLs as defined by the security spec;

• isolate rendered message content from the application DOM as strongly as practical;

• enforce a restrictive Content Security Policy;

• prevent HTML/CSS from escaping the message rendering area or spoofing application chrome;

• treat \`cid:\` inline images safely;

• block or privacy-proxy remote images by default according to product policy;

• clearly distinguish dangerous attachment/URL handling;

• provide safe plain-text fallback.

No inbound HTML may be trusted because it came through spam filtering.

## 19.5 Compose send semantics

Webmail sending is a two-stage product action:

**1\.** persist/synchronize the draft state if applicable;

**2\.** submit the final RFC message through an authenticated Karyalay server-side submission interface.

The send endpoint is idempotency-aware to avoid duplicate sends on browser retry. After the server has accepted a send request, the UI must communicate "sent/submitted" versus downstream delivery outcomes accurately.

## 19.6 Draft concurrency

Draft updates carry a revision token/version. Concurrent tabs/devices must not silently overwrite newer draft content. The webmail spec SHALL define conflict behavior and autosave intervals; the mailbox API supplies atomic revision semantics.

## 19.7 Offline behavior

Full offline mail is not a v1 requirement. The client MAY cache bounded non-sensitive UI/message data for responsiveness, but security/session revocation must remain enforceable and browser caches must avoid uncontrolled exposure on shared devices.

# 20\. Public and Internal HTTP API Conventions

## 20.1 API namespaces

Baseline namespaces:

/api/v1/... customer/user/public product APIs  
/internal/v1/... authenticated service-to-service APIs

Mailbox APIs MAY use a distinct documented prefix under /api/v1, but versioning semantics remain common.

## 20.2 Representation conventions

• JSON encoded as UTF-8 for structured API bodies unless streaming/binary content requires another type.

• JSON field names use \`snake_case\`.

• Dates/times use RFC 3339 UTC timestamps with explicit offset/Z.

• Durations/byte sizes use unambiguous units; names include units where not standardized.

• UUIDs are strings in canonical representation.

• Unknown response fields must be tolerated by clients where practical for additive evolution.

• PATCH semantics, if used, are explicitly defined rather than assumed.

## 20.3 Error format

HTTP error responses SHALL use RFC 9457 Problem Details with Karyalay extensions, conceptually:

{  
"type": "<https://errors.mail.karyalay.in/mailbox/quota-exceeded>",  
"title": "Mailbox quota exceeded",  
"status": 409,  
"code": "MAILBOX_QUOTA_EXCEEDED",  
"detail": "The requested operation would exceed the mailbox quota.",  
"request_id": "...",  
"trace_id": "...",  
"errors": \[\]  
}

code is the stable programmatic Karyalay error identifier. Human strings may evolve/localize.

## 20.4 Pagination

Large collections use cursor-based pagination by default. Offset pagination MAY be used for bounded admin tables where consistency/performance is acceptable. Cursor tokens are opaque and integrity-protected where needed.

## 20.5 Idempotency

Mutating operations with material duplicate risk—mailbox creation, provisioning requests, migration start, destructive operations, final message send—SHALL accept/use an idempotency mechanism. Idempotency-Key is the preferred HTTP header where applicable.

The server stores enough result state for a defined idempotency window and rejects incompatible reuse of a key with a different request fingerprint.

## 20.6 Concurrency control

Mutable resources SHOULD expose version, ETag or equivalent optimistic-concurrency token. Updates with stale versions return a defined conflict rather than silently overwriting high-value state.

## 20.7 Request correlation

Every inbound request receives/propagates request_id and trace context. A trusted incoming correlation ID MAY be propagated after validation; untrusted arbitrary values must not allow log injection or collision abuse.

## 20.8 Authentication and authorization errors

401 denotes absent/invalid authentication. 403 denotes authenticated caller without permission. APIs MUST not reveal the existence of cross-tenant resources when doing so creates information leakage; in such cases a 404-style response may be required by endpoint policy.

## 20.9 Rate limiting

Public APIs implement per-user/session/IP/tenant rate controls appropriate to operation risk. Responses use documented rate-limit semantics. Authentication and expensive search endpoints receive stronger abuse protection.

## 20.10 API documentation

OpenAPI definitions are mandatory for public/internal HTTP contracts and are validated in CI. Generated clients/types SHOULD derive from canonical specs to reduce drift.

# 21\. Provisioning and Infrastructure Control Contract

## 21.1 Purpose

The provisioning boundary converts canonical desired state into mail-infrastructure state. It MUST be declarative/reconciling rather than a loose collection of imperative SSH commands.

## 21.2 Resource reconciliation

For a resource such as a mailbox:

Control DB desired state  
mailbox_id = X  
generation = 14  
state = ACTIVE  
quota = 20 GiB  
placement = cluster-a/storage-03  
│  
▼  
Provisioning/reconciler  
│  
├─ auth/directory projection  
├─ Postfix recipient/routing projection  
├─ Dovecot user/storage mapping  
├─ quota state  
└─ health validation  
│  
▼  
Observed generation = 14  
Provisioning status = READY

If only generation 13 is observed, the control plane knows reconciliation remains outstanding.

## 21.3 Provisioning API properties

Internal provisioning operations MUST be:

• authenticated and authorization-scoped;

• idempotent for the same resource/generation;

• asynchronous where work may be long-running;

• observable by operation ID/status;

• deterministic from desired state;

• safe to retry after ambiguous network failure;

• explicit about partial failures;

• auditable for privileged changes.

## 21.4 No configuration mutation from browser/control requests

A customer request creates desired state; it does not directly edit daemon files synchronously on an SMTP node. Infra reconciliation generates validated configuration/projections and performs safe reloads/updates.

## 21.5 Directory projection

Postfix/Dovecot may query a dedicated read-only SQL/lookup projection. Canonical application tables SHOULD NOT be exposed directly to mail daemons if that couples their availability/schema unnecessarily.

Projection updates use transactions/generation and have consistency monitoring. Stale-projection alerts compare canonical desired generation against observed mail-plane generation.

## 21.6 Activation gate

A mailbox/domain is exposed as ACTIVE only after required checks succeed, for example:

• directory/routing projection present;

• mailbox storage initialized/accessible;

• quota mapping valid;

• authentication identity usable;

• required domain routing state valid;

• health/reconciliation generation caught up.

Failure leaves an actionable PROVISIONING_FAILED/CONFIGURING state with retriable diagnostics, not a false green state.

## 21.7 Deprovisioning safety

Destructive infrastructure removal is delayed until canonical deletion/recovery policy permits. Routing/auth state may be disabled before data is purged. Reconciler MUST distinguish "disabled but recoverable" from "physically deleted."

# 22\. Event Architecture and Durable Integration

## 22.1 Event purpose

Events communicate committed facts to other repositories without creating tight synchronous coupling. Events are not remote procedure calls and do not replace APIs for operations requiring immediate authoritative response.

## 22.2 Delivery semantics

• producer commit + outbox record is atomic for critical domain events;

• publisher retries until handed to the durable event transport;

• consumers assume at-least-once delivery;

• consumer handlers are idempotent;

• ordering is guaranteed only where explicitly documented for a resource/partition;

• events can arrive after a newer resource state, so consumers compare resource version/generation when relevant;

• poison events go to a dead-letter/quarantine workflow with alerting, not silent deletion.

## 22.3 Canonical envelope

{  
"event": "mailbox.provisioned",  
"version": 1,  
"event_id": "018f...",  
"occurred_at": "2026-08-16T01:00:00Z",  
"producer": "karyalay-mail",  
"trace_id": "...",  
"request_id": "...",  
"organisation_id": "...",  
"resource": {  
"type": "mailbox",  
"id": "...",  
"generation": 14  
},  
"data": {}  
}

Fields may be nullable only as explicitly defined by the envelope schema. Security/platform events not belonging to a customer may omit organisation_id according to schema.

## 22.4 Event naming

Event names use lower-case dotted past-tense facts such as:

domain.verified  
mailbox.requested  
mailbox.provisioned  
mailbox.restricted  
mailbox.deleted  
quota.changed  
migration.started  
migration.completed  
abuse.case_opened  
security.session_revoked

Command-style names such as provision_mailbox_now are not domain events.

## 22.5 Event data minimization

Event payloads contain IDs and bounded state necessary for consumers. They MUST NOT carry message bodies, attachment contents, passwords, app-password secrets or private cryptographic keys.

## 22.6 Schema evolution

Additive optional fields MAY remain within an event major version if old consumers safely ignore them. Semantic changes/removal/type changes require a new event schema version. Producers may dual-publish during migrations if approved.

# 23\. Error Taxonomy and Failure Semantics

## 23.1 Error categories

Canonical error codes are grouped by domain:

AUTH_\*  
AUTHZ_\*  
ORGANISATION_\*  
MAIL_DOMAIN_\*  
MAILBOX_\*  
ALIAS_\*  
GROUP_\*  
DNS_\*  
PROVISIONING_\*  
STORAGE_\*  
QUOTA_\*  
MESSAGE_\*  
SUBMISSION_\*  
MIGRATION_\*  
ABUSE_\*  
RATE_LIMIT_\*  
DEPENDENCY_\*  
INTERNAL_\*

## 23.2 Stable examples

| **Code**                             | **Meaning**                                        |
| ------------------------------------ | -------------------------------------------------- |
| \`MAIL_DOMAIN_NOT_FOUND\`            | requested hosted-domain resource absent/invisible  |
| \`MAIL_DOMAIN_NOT_ACTIVE\`           | operation requires active domain                   |
| \`MAILBOX_ALREADY_EXISTS\`           | address/resource uniqueness conflict               |
| \`MAILBOX_NOT_FOUND\`                | mailbox absent/invisible                           |
| \`MAILBOX_RESTRICTED\`               | operation disallowed by security/abuse restriction |
| \`MAILBOX_QUOTA_EXCEEDED\`           | operation cannot be completed within quota         |
| \`PROVISIONING_IN_PROGRESS\`         | desired state not yet reconciled                   |
| \`PROVISIONING_FAILED\`              | reconciliation reached an actionable failure       |
| \`MAIL_STORAGE_UNAVAILABLE\`         | mailbox backend temporarily unavailable            |
| \`SUBMISSION_SENDER_NOT_AUTHORIZED\` | From/envelope sender not permitted                 |
| \`ABUSE_RESTRICTED\`                 | account/tenant policy blocks operation             |
| \`RATE_LIMIT_EXCEEDED\`              | caller exceeded defined limit                      |
| \`DEPENDENCY_UNAVAILABLE\`           | temporary dependency failure                       |

The complete catalog defines HTTP status, retryability, user message class, logging severity and whether security details must be redacted.

## 23.3 Retryability

Every internal error must be classifiable as retryable, non-retryable, or conditionally retryable. Clients MUST NOT blindly retry all 5xx responses at high frequency.

Retryable operations use exponential backoff with jitter and bounded attempts/time. Critical reconciler workflows persist retry state and eventually alert/human-escalate rather than disappear.

## 23.4 SMTP failure mapping

Infra maps internal recipient/policy/storage states to standards-appropriate SMTP enhanced status codes. Permanent policy/unknown-recipient failures use 5xx; transient dependency/capacity failures use 4xx. The exact mapping is centralized and testable.

## 23.5 Error privacy

Customer-facing errors do not expose filesystem paths, SQL text, internal IPs, stack traces, secret values, other tenants' addresses or detailed abuse-detection rules. Full internal diagnostics are correlated by request/trace ID in restricted telemetry.

# 24\. Transactions, Idempotency, Concurrency and Reconciliation

## 24.1 Transaction boundaries

A database transaction can guarantee only state inside its database. Operations spanning DB + infrastructure + event transport use state machines/outbox/reconciliation, not distributed-transaction fantasy.

## 24.2 Lifecycle operation pattern

A high-value lifecycle operation follows this pattern:

Validate + authorize  
↓  
DB transaction:  
desired state  
operation record  
audit intent/result metadata  
event outbox  
COMMIT  
↓  
async reconciliation/external effects  
↓  
observed state update  
↓  
completion/failure event

## 24.3 Idempotent create

For create operations, the combination of caller scope + idempotency key maps to one request fingerprint and outcome for a defined retention window. A retried identical request returns the same logical result; a different request using the same key returns an idempotency conflict.

## 24.4 Message-send idempotency

Webmail send requires special treatment because duplicated mail is user-visible and potentially damaging. Before the final submission boundary, a send request uses a unique submission idempotency token. Once accepted by Postfix, the token is recorded with the resulting queue/message correlation. A browser retry returns the prior accepted outcome instead of submitting a second copy.

This does not attempt to deduplicate arbitrary SMTP clients that legitimately submit identical messages twice.

## 24.5 Optimistic concurrency

Administrative resources that may be edited concurrently carry a version. Stale destructive/security updates fail with conflict and require refresh/re-evaluation. Last-write-wins is not accepted for domain ownership, quota entitlement, security policy, aliases/groups or privileged role assignments.

## 24.6 Reconciliation loops

Reconciliation compares desired versus observed state continuously or on durable work queues. It must repair drift caused by node outage/reload failure/manual emergency intervention. Drift that cannot be repaired automatically creates a visible incident/alert.

## 24.7 Manual repair policy

Direct production database or config edits are emergency-only. If used, the operator records reason/change and the canonical desired state is reconciled immediately so the next automated run does not undo or hide the repair.

# 25\. Background Jobs, Queues and Schedulers

## 25.1 Job classes

Application jobs include:

• provisioning/reconciliation work;

• DNS verification/rechecks;

• mailbox usage snapshots;

• migration orchestration;

• DKIM rotation preparation/verification;

• notification generation;

• retention/deletion workflows;

• security/reputation aggregation;

• backup verification orchestration;

• restore workflows;

• periodic consistency audits.

SMTP delivery itself is not an application background job; it is Postfix queue work.

## 25.2 Durable job requirements

Critical jobs are persisted. Worker process restart must not lose them. Every job has:

job_id  
job_type  
resource_id / organisation_id where applicable  
payload_version  
created_at  
scheduled_at  
attempt  
max_attempts or escalation policy  
lease/lock state  
last_error_code  
trace/correlation  
status

## 25.3 Worker leases

Long jobs use leases/heartbeats so a crashed worker can be recovered without two workers permanently owning the same work. Handlers remain idempotent because lease systems cannot guarantee exactly-once execution under every failure.

## 25.4 Scheduling

Periodic jobs use one authoritative scheduler/leader mechanism per job class to avoid duplicated global runs, but duplicate execution must still be safe. User-facing schedule times preserve the user's timezone intent while persisted scheduler instants are normalized.

## 25.5 Poison work

After repeated deterministic failure, a job enters an actionable failed/dead-letter state with structured diagnostics and alerting where impact warrants. "Retry forever every second" is prohibited.

# 26\. Security Architecture and Threat Controls

## 26.1 Security baseline

Karyalay Email SHALL be engineered and verified against OWASP ASVS 5.0 as the web/application-security baseline, together with current NIST SP 800-63-4 guidance for authentication/federation design and protocol-specific mail security standards. The repository security specifications map concrete controls/tests to these baselines.

The service is a high-value target because a mailbox can reset passwords, receive invoices/contracts, expose private communications and impersonate a business. Security therefore applies to the entire mail/control/operations chain, not only login pages.

## 26.2 Threat model categories

At minimum, the system threat model SHALL cover:

• account takeover and credential stuffing;

• phishing and recovery/social-engineering abuse;

• app-password theft;

• session/token theft;

• tenant-boundary bypass/IDOR;

• XSS through hostile email HTML;

• malicious attachments, parsers and previewers;

• SSRF through remote content, URL previews, migration connectors and DNS-related features;

• SQL/command/template injection;

• path traversal and unsafe archive extraction;

• open relay and sender-spoofing configuration mistakes;

• SMTP smuggling/request interpretation discrepancies where applicable;

• mail bombs/decompression bombs/MIME parser resource exhaustion;

• DDoS and connection/resource exhaustion;

• spam/phishing account abuse;

• insider/privileged administrator abuse;

• secret/private-key compromise;

• supply-chain compromise of dependencies/images/packages;

• backup theft/destruction;

• DNS/domain takeover and DKIM key misuse;

• malicious migration source data;

• cross-service confused-deputy attacks;

• logging/telemetry leakage of private content.

## 26.3 Secure coding requirements

All repositories MUST use:

• parameterized database access or a safe ORM/query layer;

• output encoding and context-aware HTML sanitization;

• bounded parsers and input-size limits;

• strong schema validation at untrusted boundaries;

• CSRF protections appropriate to the session architecture;

• restrictive CORS rather than wildcard authenticated APIs;

• CSP and browser security headers;

• safe URL validation before server-side fetches;

• cryptographically secure random generation for tokens/secrets;

• dependency and secret scanning in CI;

• no custom cryptographic primitives.

## 26.4 Message-content isolation

Message parsers/renderers/previewers are exposed to hostile content. High-risk file conversion and extraction SHOULD execute in sandboxed, resource-limited workers without access to production credentials or broad networks. A malformed document must not compromise the control plane.

## 26.5 Remote image/privacy protection

Remote images and tracking resources in email can reveal user IP, time and client attributes. Default webmail policy SHALL block them or fetch through a privacy-preserving proxy that strips cookies/credentials, prevents internal-network SSRF and constrains content types/sizes. User "always load from sender" preferences remain revocable.

## 26.6 Open relay prevention

A production release MUST include automated open-relay tests covering unauthenticated external-to-external relay, crafted envelope/header combinations, IPv4/IPv6, alternate listener ports and authentication edge cases. Any configuration enabling unintended relay is a release blocker.

## 26.7 Tenant-isolation verification

Security CI SHALL include object-authorization tests/fuzzing proving that IDs from organisation B cannot be read/modified by organisation A across control, mailbox and ops APIs. This includes batch endpoints, searches, exports, attachments and indirect references.

## 26.8 Privileged access

Production operator access:

• uses named identities, not shared accounts;

• requires MFA;

• is logged/audited;

• is time-bounded/elevated for high-risk actions where practical;

• follows separation of duties for break-glass and key recovery;

• does not permit routine direct content browsing.

## 26.9 Security testing gate

Before general availability, the platform MUST pass:

• SAST/dependency/secret scans;

• DAST/API security tests;

• mail-protocol abuse/open-relay tests;

• webmail hostile-HTML/XSS corpus tests;

• MIME/attachment fuzz/resource-exhaustion tests for Karyalay parsers;

• tenant-isolation tests;

• authentication/session tests;

• backup/restore security tests;

• infrastructure/CIS-style hardening checks where applicable;

• an independent penetration test scoped across all externally exposed surfaces.

Critical/high findings are fixed or explicitly risk-accepted by authorized security leadership before GA; critical findings cannot be waived for schedule convenience.

# 27\. Anti-Abuse, Spam, Reputation and Deliverability Architecture

## 27.1 Reputation is a shared platform asset

Outbound IP/domain reputation is part of Karyalay's production infrastructure. A single compromised or malicious tenant can affect unrelated customers on shared sending pools. Anti-abuse controls are therefore a mandatory availability function, not an optional moderation feature.

## 27.2 Layered enforcement

Controls exist at:

message  
↓  
mailbox  
↓  
domain  
↓  
organisation  
↓  
SMTP/IP pool  
↓  
platform

Signals at a lower layer can trigger action at a higher layer where blast radius warrants.

## 27.3 Baseline outbound signals

At minimum, policy can consider:

• messages and recipients per rolling time window;

• unique-recipient growth;

• hard/soft bounce rates;

• recipient-provider temporary/permanent rejection patterns;

• spam/abuse complaint data where available;

• Rspamd outbound scores/signals;

• known malicious URL/domain intelligence integrations approved by Security;

• new account age;

• sudden divergence from a mailbox's normal sending baseline;

• new device/IP combined with volume change;

• authentication/session risk;

• unusually large BCC/recipient fan-out;

• repeated forbidden/bulk patterns;

• compromised-domain indicators.

Signals must not become an opaque automated permanent-deletion system. Enforcement states and reasons are reviewable/auditable.

## 27.4 Enforcement ladder

Typical actions, from low to high severity:

**1\.** observe/increase telemetry;

**2\.** slow or temporarily rate-limit;

**3\.** require additional authentication or user/admin confirmation;

**4\.** temporarily block outbound sending while preserving inbound/read access;

**5\.** restrict whole domain/organisation where coordinated abuse exists;

**6\.** suspend account/tenant under terms/policy;

**7\.** remove from shared sending infrastructure and investigate reputation impact.

Rules for automatic versus analyst-approved actions are defined in karyalay-mail-ops.

## 27.5 New-account protections

New organisations/mailboxes begin with conservative sending limits that expand based on age, verified domain state, legitimate usage and risk. Limits SHALL not encourage customers to perform "IP warming" through artificial unsolicited traffic.

## 27.6 IP pool architecture

The platform supports multiple outbound SMTP pools. Placement can account for:

• standard shared business mail;

• trusted/higher-volume business tenants;

• dedicated customer IP entitlement;

• transactional system mail if ever hosted separately;

• quarantine/reputation recovery pools only when deliberately designed.

Marketing/bulk mail is never placed in the ordinary business-mail pool.

IP pool changes are controlled operational actions because abrupt source changes can affect reputation and delivery.

## 27.7 Provider telemetry

Where recipient providers expose postmaster/feedback systems, Karyalay operations SHOULD integrate them through governed service accounts. Provider-specific spam/reputation metrics are normalized into an internal model while retaining source/raw status for diagnosis.

## 27.8 Complaint targets

Published provider limits are maximum failure thresholds, not Karyalay targets. Operations SHOULD aim for complaint/spam rates materially below 0.1% where comparable provider metrics exist and treat approach toward 0.3% as a serious reputation incident, consistent with current Gmail/Yahoo sender guidance.

## 27.9 Deliverability diagnostics

For an outbound message, authorized support/deliverability tooling SHOULD be able to retrieve without message-body access:

• submission identity and timestamp;

• queue ID/correlation ID;

• source IP/pool and EHLO name;

• DKIM selector/domain used;

• remote MX target;

• TLS outcome/policy;

• each SMTP attempt timestamp and sanitized response;

• final queue outcome/DSN class;

• relevant reputation/abuse restriction state;

• DNS/authentication configuration snapshot.

## 27.10 Inbound spam controls

Rspamd owns low-level classification; Karyalay owns product policy. User allowlists SHOULD NOT override high-confidence malware or mandatory platform block rules. Blocklists/allowlists are scoped and bounded to prevent unmanageable global exceptions.

## 27.11 Abuse reporting contact

Karyalay operates monitored abuse@ and postmaster@ contacts and documented abuse workflows. Reports are tracked as cases with evidence, customer notifications where appropriate and measurable response targets.

# 28\. Data Classification, Privacy, Retention and Deletion

## 28.1 Data classes

| **Class**              | **Examples**                                                                          | **Handling**                                                   |
| ---------------------- | ------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| Restricted content     | message bodies, attachments, drafts, private keys, authentication secrets             | strongest access restriction/encryption/telemetry minimization |
| Sensitive metadata     | addresses, subject lines, recipients, IPs, login/device data, message routing history | role-restricted, retained only as needed                       |
| Customer configuration | domains, aliases, quotas, policies, groups                                            | tenant-authorized, auditable                                   |
| Operational telemetry  | service metrics, sanitized logs, queue/provider outcomes                              | controlled operator access; avoid content                      |
| Audit evidence         | administrator/security lifecycle events                                               | append-oriented, tamper-resistant access controls              |
| Public configuration   | MX names, DKIM public keys, public MTA-STS policy                                     | intentionally public                                           |

## 28.2 Content minimization

General application logs, tracing spans, metrics labels and analytics MUST NOT contain message bodies or attachments. Subject lines and full recipient lists are excluded by default from broad telemetry because they are sensitive metadata. Diagnostic tools may expose them only under explicit controlled permissions if required.

## 28.3 Encryption

• external HTTPS/IMAPS/submission traffic uses modern TLS;

• server-to-server SMTP uses opportunistic TLS enhanced by MTA-STS/TLS policy where applicable;

• internal sensitive service connections use TLS where supported and practical;

• backups are encrypted independently;

• storage-at-rest encryption is implemented at disk/filesystem/volume and/or appropriate service layers according to Infra spec;

• key storage is separated from ciphertext where meaningful.

Encryption at rest does not eliminate the requirement for filesystem/service authorization because mail servers must decrypt data to operate.

## 28.4 Retention baseline

Unless product/legal requirements establish stronger values, the v1 engineering baseline is:

| **Data**                             | **Baseline engineering retention**                                          |
| ------------------------------------ | --------------------------------------------------------------------------- |
| Active mailbox content               | while account is active, user-controlled deletion semantics                 |
| Deleted mailbox recoverability       | 30 days after deletion, subject to published product policy                 |
| Control DB point-in-time recovery    | at least 35 days                                                            |
| Daily mailbox backup generations     | at least 35 days                                                            |
| Monthly backup generations           | up to 12 months where approved economics/policy permit                      |
| Security/audit events                | at least 365 days unless legal/privacy policy changes it                    |
| Routine high-volume operational logs | tiered, typically days/weeks hot + defined archive based on utility/privacy |
| Temporary uploads/preview files      | shortest practical period; aggressively cleaned                             |
| Migration source credentials         | only while needed; deleted immediately after job/retry window as defined    |

The eventual customer-facing privacy policy and contractual retention schedule SHALL be reconciled with these engineering capabilities before GA.

## 28.5 User deletion semantics

Deleting a message through IMAP/webmail follows mailbox protocol semantics, including Trash/expunge behavior. Backup copies may persist until backup expiry and are not treated as active searchable mailbox content. Restoration processes must not unintentionally resurrect messages deleted before the restore point without warning/defined behavior.

## 28.6 Organisation export/portability

The architecture SHALL preserve the ability to export mailboxes in standards-readable formats or IMAP-migrate out. Customer lock-in through proprietary-only message storage is not an architectural objective.

## 28.7 Legal requests

A full legal-hold/eDiscovery product is out of v1 scope. Any government/legal disclosure workflow is governed separately by company legal/privacy policy and cannot be implemented as an undocumented operator shortcut. The technical system must make privileged data access auditable.

# 29\. Auditability and Administrative Accountability

## 29.1 Audit log versus debug log

Audit events are durable evidence of security/business actions. They are not reconstructed from ephemeral application logs. Audit writes for critical control-plane changes occur transactionally or through a durable outbox tied to the committed change.

## 29.2 Required audit fields

Conceptual audit envelope:

{  
"audit_id": "uuid",  
"occurred_at": "RFC3339",  
"actor_type": "user|service|platform_operator",  
"actor_id": "uuid/string",  
"organisation_id": "uuid|null",  
"action": "mailbox.quota_changed",  
"resource_type": "mailbox",  
"resource_id": "uuid",  
"result": "success|denied|failure",  
"reason": "bounded operator/user reason where required",  
"request_id": "...",  
"trace_id": "...",  
"source": {"ip": "classified", "client": "bounded"},  
"changes": {"safe_before_after_fields": "..."}  
}

Secrets and message bodies are forbidden in audit payloads.

## 29.3 Actions that MUST be audited

• organisation/role/admin changes;

• domain add/verify/transfer/delete/suspend;

• mailbox create/delete/restore/restrict/suspend;

• alias/group/forwarding changes;

• quota/plan security-relevant changes;

• MFA/app-password/security reset actions;

• DKIM key rotation and domain security-policy changes;

• migration start/cancel/credential activation/completion;

• abuse restriction/release;

• restore/recovery actions;

• operator elevation/break-glass;

• any future customer-content access by staff;

• material infrastructure emergency overrides.

## 29.4 Audit tamper resistance

Audit storage must have access separation from ordinary application mutation. Append-only/WORM-like capabilities SHOULD be used where practical for privileged security evidence. Deleting an application row must not cascade-delete its audit history.

## 29.5 Customer audit access

Organisation admins SHOULD receive a tenant-scoped audit view/export for relevant administrative/security actions. Platform-internal abuse heuristics and unrelated operator data are not exposed indiscriminately.

# 30\. Observability: Logs, Metrics, Traces and Correlation

## 30.1 Observability contract

All Karyalay-owned services use structured telemetry compatible with OpenTelemetry concepts. The goal is correlation across browser/API/control/provisioning/mail operations without placing private mail content in general telemetry.

## 30.2 Structured log baseline

Conceptual common fields:

{  
"timestamp": "2026-08-16T01:00:00.123Z",  
"severity": "ERROR",  
"service": "mail-control",  
"environment": "production",  
"version": "...",  
"event": "mailbox.provision_failed",  
"request_id": "...",  
"trace_id": "...",  
"span_id": "...",  
"organisation_id": "...",  
"resource_type": "mailbox",  
"resource_id": "...",  
"error_code": "PROVISIONING_FAILED",  
"message": "sanitized operator-safe description"  
}

Fields are omitted when not applicable. Logs use structured values, not concatenated unparseable prose for essential fields.

## 30.3 Message correlation

SMTP daemons have their own queue/message identifiers. The platform SHALL establish a privacy-conscious correlation model linking submission/API events to Postfix queue IDs and relevant delivery attempts. Operators should trace a customer's reported message using known timestamp/sender/recipient/message ID without requiring message-body indexing in logs.

## 30.4 Metrics baseline

Metrics cover at minimum:

**SMTP:** connections, accepted/rejected/deferred, queue size/age, retry outcomes, provider response classes, TLS usage.

**Mailbox:** IMAP connections/auth failures, LMTP deliveries/failures/latency, active sessions, quota errors, storage/index latency.

**Filtering:** Rspamd latency/actions, spam distributions, malware detections, Redis health, DNS lookup health.

**Control plane:** request rate/error/latency, provisioning backlog, reconciliation drift, event outbox age, job failures, DB pool/replication.

**Infrastructure:** CPU/RAM/load, disk space/inodes/latency, network, certificates, node health, backup age/success.

**Business safety:** active mailboxes/domains by capacity dimension, sending volume, abnormal abuse indicators, provider rejection/complaint trends.

High-cardinality user/email fields MUST NOT be metric labels.

## 30.5 Tracing

Distributed traces cover Karyalay HTTP/service/job flows. Native SMTP/IMAP daemon logs may not propagate W3C trace context, so bounded correlation bridges are maintained through queue IDs/resource IDs rather than modifying Internet protocols.

## 30.6 Alert quality

Alerts are actionable. Every paging alert has:

• owner/team;

• severity;

• user/business impact statement;

• primary dashboard/query;

• first diagnostic steps/runbook;

• dedup/silence behavior;

• escalation path.

Alerts for symptoms are preferred over noisy internal metrics where possible. Repeated non-actionable alerts are engineering defects.

## 30.7 External monitoring

At least one monitoring/check path operates outside the primary production failure domain so a total site/network outage still pages operators. Synthetic probes cover SMTP connectivity, submission auth, IMAP login, HTTPS and representative end-to-end mail loops.

# 31\. Service Levels, Performance and Reliability Objectives

## 31.1 Initial service objectives

These are engineering SLOs for the mature v1/GA architecture; commercial SLAs may be set separately.

| **Capability**                             | **Initial SLO/target**                                                              |
| ------------------------------------------ | ----------------------------------------------------------------------------------- |
| Public inbound SMTP edge availability      | ≥ 99.95% monthly                                                                    |
| Authenticated SMTP submission availability | ≥ 99.95% monthly                                                                    |
| IMAP service availability                  | ≥ 99.95% monthly                                                                    |
| Webmail/control API availability           | ≥ 99.90% initial, architecture capable of 99.95%                                    |
| Local accepted-mail delivery latency       | p95 < 5 seconds under normal load                                                   |
| SMTP submission acceptance latency         | p95 < 1 second before remote delivery, excluding large upload time                  |
| Mailbox list/inbox API                     | p95 < 700 ms for normal cached/indexed mailbox operations                           |
| First usable webmail inbox view            | p95 < 1.5 seconds on representative broadband/device after auth/session established |
| Open ordinary cached/indexed message       | p95 < 500 ms server-side/API target, excluding large remote images/attachments      |
| Typical indexed search                     | p95 < 2 seconds                                                                     |
| Control API ordinary operations            | p95 < 300 ms excluding deliberate async operations                                  |

Exact load profiles and measurement boundaries are defined in repository performance specs; a target without a test workload is not considered verified.

## 31.2 Availability semantics

A service is not considered "available" merely because TCP accepts connections. SLI success requires the expected user/protocol operation to complete within a defined correctness/latency boundary.

## 31.3 Error budgets

SLOs SHALL produce error budgets and release/operational policy. Repeated exhaustion triggers reliability work rather than normalizing poor service. Planned maintenance handling is defined transparently and cannot be used to hide avoidable outages from internal engineering metrics.

## 31.4 Mail-specific reliability invariant

Temporary inability to reach a remote recipient MX is not a Karyalay availability failure if the message is durably queued and retried according to policy. Loss of an accepted queue entry is a severe reliability incident.

# 32\. Capacity, Scaling and Placement Strategy

## 32.1 Scaling philosophy

The first environment may be small, but core identities and placement abstractions SHALL support horizontal growth. Scale is achieved by adding SMTP/filter nodes, mailbox/storage nodes, application nodes and DB/read capacity rather than assigning a permanent server hostname into customer-visible semantics.

## 32.2 Capacity dimensions

Capacity planning tracks independently:

• active mailboxes;

• stored message bytes and inode/object counts;

• daily inbound/outbound message count;

• peak SMTP connections;

• concurrent IMAP sessions;

• search/index CPU/IO;

• Rspamd/DNS/Redis workload;

• database transactions and projection size;

• migration bandwidth/jobs;

• backup read/write/network load;

• outbound IP reputation/volume capacity.

Mailbox count alone is not a sufficient capacity metric.

## 32.3 Placement

A placement service/algorithm within control/infra boundaries selects storage/mail cluster using capacity, health, maintenance state, tenant policy and locality. Placement is stored explicitly and can be migrated through a governed process.

No new mailbox is placed on a node marked draining, unhealthy or above the no-new-placement disk threshold.

## 32.4 Disk-pressure policy

Baseline operational thresholds:

| **Utilization** | **Required behavior**                                                                                      |
| --------------- | ---------------------------------------------------------------------------------------------------------- |
| <70%            | normal                                                                                                     |
| 70–80%          | warning/capacity forecast; schedule expansion if trend warrants                                            |
| 80–90%          | high-capacity alert; throttle nonessential IO/background work as appropriate                               |
| 90–95%          | stop new mailbox placements; prioritize expansion/migration; stronger paging                               |
| \>95%           | emergency state; defer operations/delivery where necessary before filesystem exhaustion; incident response |

Thresholds may be tuned by filesystem/storage technology, but production must always preserve safety headroom.

## 32.5 Growth triggers

Capacity forecasting uses time-to-exhaustion, not only fixed percentages. Planned expansion should occur with enough lead time for hardware/provider procurement, storage rebalance, IP reputation considerations and migration testing.

## 32.6 No premature distributed-storage complexity

The architecture MAY begin with robust local redundant storage plus replication/backup rather than Ceph/Kubernetes-style complexity. A future distributed storage migration is allowed because applications depend on mailbox placement abstractions, not local paths.

# 33\. High Availability, Failover and Degraded Modes

## 33.1 Failure assumptions

The platform assumes processes, disks, VMs, nodes, links, DNS resolvers and entire sites can fail. HA is designed around explicit failure domains and recovery behavior rather than assuming "cloud" equals HA.

## 33.2 SMTP ingress HA

Customer MX records SHALL reference at least two independently fault-tolerant ingress endpoints before GA. Each ingress can validate recipient state from a sufficiently available/cached directory projection and queue accepted mail durably.

Remote SMTP retries naturally provide additional resilience; therefore if all safe local delivery paths are temporarily unavailable, the ingress may 4xx defer before final acceptance instead of accepting unsafely.

## 33.3 Submission HA

Submission endpoints use redundant nodes/load routing. Auth and policy dependency failures should return temporary failure, not accept mail that cannot be durably queued.

## 33.4 Mailbox/storage HA

Mailbox HA design MUST protect acknowledged writes. The Infra spec defines the selected Dovecot/storage replication pattern and failover mechanism. Failover cannot result in two divergent writable primaries for the same mailbox without a reconciliation/fencing strategy.

## 33.5 Database HA

Canonical control-plane DB has automated backups/PITR and production replication/failover appropriate to its SLO. Split-brain is prevented through the chosen database topology. Applications fail closed on writes if database consistency cannot be established.

## 33.6 Degraded modes matrix

| **Failure**                       | **Expected degraded behavior**                                                                   |
| --------------------------------- | ------------------------------------------------------------------------------------------------ |
| Control API unavailable           | existing SMTP/IMAP/submission continue from projections; admin changes unavailable               |
| Billing subsystem unavailable     | existing paid service continues within grace policy; no mail-plane outage                        |
| Rspamd unavailable on an edge     | follow explicit fail policy; do not silently bypass mandatory outbound/inbound security at scale |
| ClamAV unavailable                | policy-defined temporary deferral or marked degraded scanning; never claim scan occurred         |
| Redis unavailable                 | filtering/rate features degrade according to tested safe mode; alert immediately                 |
| DNS resolver degraded             | alternate local resolvers; SMTP delays rather than fabricated DNS answers                        |
| Mailbox node unavailable          | failover/temporary IMAP error; inbound may queue/defer safely                                    |
| Search index unavailable          | reading/sending works; search degraded/rebuildable                                               |
| Observability backend unavailable | services continue with bounded local buffering; alert through independent path                   |
| Backup target unavailable         | service continues; backup RPO alert escalates before protection window is exceeded               |

## 33.7 Maintenance/draining

Nodes support ACTIVE, DRAINING, MAINTENANCE, UNHEALTHY, RETIRED states. Draining stops new placements/connections as appropriate and allows graceful completion/migration before shutdown.

# 34\. Backup, Restore and Disaster Recovery

## 34.1 Backup philosophy

Replication is not backup. Snapshots are not sufficient alone. The service requires versioned, encrypted, independently accessible backups protected from the same credential/ransomware/operator failure domain as primary production.

## 34.2 Data protected

At minimum:

• mailbox message storage and required mailbox metadata/index state or rebuild instructions;

• canonical control databases and transaction/PITR logs;

• directory/provisioning state that cannot simply be regenerated;

• DKIM private keys and active/retired selector metadata;

• infrastructure configuration repositories/manifests;

• identity-service configuration and necessary secrets according to approved recovery model;

• Sieve/user filter rules and preferences;

• audit evidence;

• operational data required for recovery of queues/state where applicable;

• backup encryption/recovery metadata stored separately.

Postfix queue data is operationally protected by node/storage durability; queues in-flight at disaster time require explicit DR consideration and are not assumed reconstructable from control DB.

## 34.3 Recovery objectives baseline

| **Scenario**                                             | **RPO target**                                                              | **RTO target**                                        |
| -------------------------------------------------------- | --------------------------------------------------------------------------- | ----------------------------------------------------- |
| Single-disk failure with healthy mirror/replication      | 0 acknowledged messages                                                     | automatic/minutes                                     |
| Single mailbox/storage-node failure with healthy replica | ≤5 minutes or better, with design goal of 0 for acknowledged local delivery | ≤60 minutes for service restoration                   |
| Control database failure                                 | ≤5 minutes                                                                  | ≤60 minutes                                           |
| Accidental mailbox deletion within recovery window       | latest viable pre-deletion point; user understands point-in-time semantics  | ≤2 hours after approved restore initiation            |
| Primary-site disaster using backup-only recovery         | ≤24 hours worst case; target ≤1 hour where the hourly snapshot tier (Repo 3 §58) has completed off-site replication. Each deployment MUST publish its measured value rather than quoting the worst case. | priority service ≤8 hours; full restoration ≤24 hours |

The Infra repository may improve these objectives, but MUST NOT silently weaken them.

## 34.4 Restore hierarchy

Restoration capabilities include:

**1\.** single message/folder recovery where technically supported safely;

**2\.** mailbox point-in-time restore into a temporary/recovery namespace before merge;

**3\.** mailbox full replacement with explicit approval;

**4\.** database point-in-time restore;

**5\.** node rebuild from automation + data restore;

**6\.** site-level disaster reconstruction.

Directly overwriting a live mailbox during exploratory recovery is prohibited.

## 34.5 Restore verification

Backups are automatically checked for completion/integrity, but that is insufficient. Scheduled restore drills MUST create usable restored data in isolated environments and verify authentication-independent mailbox structure/message sampling, DB consistency and key/config recoverability.

## 34.6 Backup deletion protection

Production application credentials cannot erase all backup history. Backup repositories SHOULD use immutability/object-lock/WORM-like safeguards or independent append-only credentials where available. Destructive backup administration requires strong authorization and audit.

## 34.7 Disaster runbooks

karyalay-mail-ops owns executable runbooks for node loss, database loss, mailbox corruption, key loss, primary-site outage, DNS outage and mass credential compromise. Runbooks specify decision owner, prerequisites, commands/automation, validation and rollback—not merely "restore from backup."

# 35\. Environments, Deployment Topology and Configuration Management

## 35.1 Environment classes

The system SHALL have distinct development, CI/test, staging/pre-production and production environments. Production data is never copied wholesale into lower environments. If realistic message samples are required, use synthetic or rigorously sanitized fixtures.

| **Environment**   | **Purpose**                                     | **Data policy**                                                                              | **External mail behavior**                                   |
| ----------------- | ----------------------------------------------- | -------------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| Local development | fast engineer/agent iteration                   | synthetic only                                                                               | isolated test domains/sinks; no accidental Internet delivery |
| CI integration    | deterministic automated tests                   | generated fixtures                                                                           | protocol test harnesses/containerized peers                  |
| Staging           | production-like deployment/release verification | synthetic + approved test mailboxes                                                          | controlled real Internet test domains/IPs where necessary    |
| Production        | customer service                                | live customer data                                                                           | full Internet mail                                           |
| DR drill          | isolated recovery validation                    | restored encrypted production subsets under strict access or synthetic, as procedure permits | blocked from accidental outbound delivery                    |

## 35.2 Production topology baseline

The final topology may evolve, but GA SHALL logically provide:

PUBLIC INTERNET  
│  
┌────────────────┴────────────────┐  
│ │  
MX / EDGE A MX / EDGE B  
Postfix + Rspamd Postfix + Rspamd  
│ │  
└──────────────┬──────────────────┘  
│  
internal mail network  
│  
┌───────────┴───────────┐  
│ │  
Mailbox cluster A Mailbox cluster B...  
Dovecot + storage Dovecot + storage  
│ │  
└───────────┬───────────┘  
│  
Control / API application tier  
│  
DB / projection / jobs  
│  
Ops + observability + backup systems

MX A/B must not be two DNS records pointing to the same single failure domain and called "HA." Physical/provider/site independence increases by delivery phase, but failure domains are documented explicitly.

## 35.3 Configuration as code

All reproducible infrastructure configuration lives in version control and is applied via automation. This includes:

• OS hardening baseline;

• users/groups/service permissions;

• firewall policy;

• Postfix/Dovecot/Rspamd/ClamAV/Redis/Unbound/NSD/HAProxy config templates;

• systemd/service lifecycle;

• monitoring/exporters;

• backup clients;

• log rotation/collection;

• certificate automation;

• node role labels and inventories.

Production changes made outside automation are emergency exceptions and must be reconciled back into code immediately.

## 35.4 Configuration layering

Configuration separates:

upstream defaults  
↓  
Karyalay secure baseline  
↓  
environment values  
↓  
node/role values  
↓  
generated customer/resource projections  
↓  
emergency temporary override (explicit + expiring)

Customer-generated data SHALL not be interpolated into arbitrary config text without validated escaping/schema constraints.

## 35.5 Feature flags

Product feature flags MAY gate gradual rollout, but flags must have owner, purpose, default, expiry/review date and safe behavior. Security controls cannot be permanently disabled through undocumented flags.

## 35.6 Time synchronization

All production nodes use reliable time synchronization. Large clock skew affects TLS, DKIM/signature interpretation, OAuth tokens, logs, tracing, retries and incident analysis. Clock-offset monitoring is mandatory.

## 35.7 Host naming

Hostnames encode role/location/instance without customer identity. Example pattern:

mx-del-01  
mx-del-02  
mail-del-a-01  
api-del-01  
db-del-01  
mon-independent-01

The actual production naming convention is specified by Infra. Public EHLO/PTR names remain stable service identities and are not necessarily internal hostnames.

# 36\. CI/CD, Supply-Chain Security and Release Engineering

## 36.1 Release principle

A mail-service release must be reproducible, reviewable, testable and reversible. "Agent generated it and the smoke test passed" is not a release standard.

## 36.2 Mandatory CI categories

Every relevant repository pipeline SHALL include:

• formatting/lint/static type checks appropriate to the language;

• unit tests;

• contract/schema validation;

• integration tests;

• security/dependency scanning;

• secret scanning;

• license/SBOM generation;

• build artifact provenance/checksum;

• migration/config validation;

• repository-specific performance/regression tests;

• container/image scanning where containers are used.

Shared contract changes additionally run compatibility tests across all consumers.

## 36.3 Software bill of materials

Release artifacts SHALL have an SBOM containing direct/transitive dependencies where tooling supports it. Critical infrastructure image/package versions are recorded so a vulnerability advisory can identify affected production nodes quickly.

## 36.4 Dependency policy

• dependencies are pinned through lockfiles/package manifests;

• unmaintained or suspicious packages are not added for trivial functionality;

• automated update tools may propose upgrades, but security-critical changes are reviewed and tested;

• production packages/images come from approved repositories/builds;

• build systems shall not download arbitrary unverified scripts at runtime;

• dependency provenance and signatures/checksums are used where ecosystem support is mature.

## 36.5 Database migrations

Database migrations are forward-tested against representative production-scale datasets. They support rolling deployment where required. Long table locks/unbounded backfills are not executed synchronously during a normal deploy.

Breaking schema changes use expand-migrate-contract patterns:

**1\.** add compatible schema;

**2\.** deploy writers/readers supporting both;

**3\.** backfill/verify;

**4\.** switch canonical use;

**5\.** remove old schema only after rollback window.

## 36.6 Mail daemon configuration releases

Before deployment, generated Postfix/Dovecot/Rspamd/HAProxy/DNS configurations are syntax-validated using native validation commands and test harnesses. A config generation bug must fail CI/deployment before reloading a fleet.

## 36.7 Progressive rollout

Application and infrastructure changes SHOULD roll progressively: test/staging → canary/small production subset → broader fleet. Metrics/error budgets define automatic/manual halt criteria.

## 36.8 Rollback

Every release plan defines rollback compatibility. Rollback is not considered possible if a new irreversible DB/config/data mutation makes the old release unsafe. Such changes require an explicit roll-forward recovery strategy and additional approval.

# 37\. Testing and Verification Strategy

## 37.1 Test pyramid plus protocol/system tests

Unit tests alone are insufficient. The complete system uses:

unit tests  
component tests  
contract tests  
integration tests  
mail-protocol interoperability tests  
security/fuzz tests  
failure-injection tests  
performance/load tests  
end-to-end tests  
backup/restore/DR drills  
manual UX/accessibility validation

## 37.2 Shared contract tests

The canonical OpenAPI/event/error/auth schemas are compiled/validated in every consumer. Provider/consumer contract tests SHALL prove the exact payloads and error behavior expected by each repo.

A PR that changes a shared schema cannot merge while an affected consumer's compatibility suite fails unless the approved migration explicitly supports the transition.

## 37.3 SMTP test matrix

Tests cover at least:

• valid inbound delivery;

• nonexistent recipient at RCPT stage;

• temporary backend failure;

• malformed commands/line lengths;

• STARTTLS negotiation/failure;

• IPv4/IPv6 as supported;

• SPF/DKIM/DMARC pass/fail/temperror/permerror combinations;

• ARC-forwarding paths;

• malware and EICAR-like safe test patterns;

• spam/high-score policy;

• over-quota recipient;

• alias/group expansion;

• loop protection;

• DSN generation;

• remote 4xx retry;

• remote 5xx bounce;

• DNS timeout/NXDOMAIN;

• MTA-STS/TLS policy behavior where enabled;

• open-relay attempts.

## 37.4 IMAP/mailbox test matrix

Tests cover:

• login/OAuth/app-password policy;

• mailbox creation/special-use folders;

• message append/fetch/search;

• flags/read/unread/star;

• move/copy/delete/expunge;

• large folder pagination;

• concurrent clients;

• UID/UIDVALIDITY behavior;

• quota enforcement;

• Sieve filtering;

• server failover/reconnect;

• corrupt/rebuilt indexes;

• common client interoperability.

## 37.5 MIME/rendering corpus

Webmail/message gateway tests use a large corpus including:

• plain text;

• HTML;

• multipart alternative/mixed/related;

• inline CID images;

• nested messages;

• unusual charsets/encodings;

• Unicode filenames;

• malformed but common real-world MIME;

• huge headers/nested parts bounded by limits;

• malicious HTML/CSS/URLs;

• attachment filename traversal attempts;

• zip/archive bombs within safe test limits;

• cryptographically signed/encrypted MIME presented safely even if full feature support is deferred.

## 37.6 Failure injection

Staging tests intentionally kill/restart:

• API nodes during requests;

• provisioning workers mid-operation;

• Rspamd/Redis/ClamAV;

• Dovecot nodes during reads/delivery;

• database primary under controlled failover;

• DNS resolver;

• network route between major tiers;

• backup target;

• event transport/worker.

Success criteria focus on no silent mail/data loss, bounded duplicate work and recovery/reconciliation.

## 37.7 Performance tests

Load profiles reflect realistic distributions: small/large mailboxes, attachment uploads, IMAP idle clients, peak morning access, spam bursts, queue retry storms and migrations. Tests report latency percentiles, saturation, queue age, IO and failure rates—not only requests per second.

## 37.8 Accessibility and UX

Webmail/admin interfaces target WCAG 2.2 AA or later approved baseline. Keyboard navigation, screen reader labels, focus management, contrast, zoom/reflow and compose/inbox workflows are verified. Email rendering content cannot hijack keyboard/focus outside its container.

# 38\. Compatibility, Versioning and Upgrade Policy

## 38.1 Public API versioning

/api/v1 is backward-compatible within v1 except for security corrections where prior behavior is unsafe. Additive fields/endpoints are preferred. Removal/semantic breaking changes require a new major API path/version and migration/deprecation period.

## 38.2 Internal APIs

Internal APIs are also versioned because separate repositories deploy independently. "Internal" does not mean breaking at will. Deployment choreography must permit old/new versions to overlap during rollout.

## 38.3 Event compatibility

Event version is explicit in envelope/schema. Consumers declare supported versions. Event producers never reinterpret an existing field to mean something different without versioning.

## 38.4 Protocol compatibility

Postfix/Dovecot upgrades are tested against representative remote/client implementations. Deprecated cryptography/protocol features MAY be removed for security even if an old client breaks, but product documentation and telemetry should make such changes intentional.

## 38.5 Data migrations

Mailbox format/storage migrations are tested at realistic data volume with interruption/resume and rollback/forward recovery. A mailbox cannot be "half migrated" without an authoritative placement state and fencing.

## 38.6 Deprecation

Deprecated features have:

• announcement/documentation;

• telemetry measuring actual use where privacy permits;

• migration path;

• target removal version/date;

• support implications;

• explicit deletion of old code/config after the window.

# 39\. Incident Response and Emergency Control Plane

## 39.1 Incident classes

At minimum, incident taxonomy includes:

• availability outage;

• mail loss/corruption risk;

• deliverability/reputation incident;

• spam/abuse campaign;

• account takeover wave;

• credential/key compromise;

• cross-tenant/privacy/security breach;

• DNS/certificate failure;

• storage capacity emergency;

• backup/recovery protection failure;

• dependency/supply-chain vulnerability.

## 39.2 Severity baseline

| **Severity** | **Example**                                                                                                | **Response expectation**                                  |
| ------------ | ---------------------------------------------------------------------------------------------------------- | --------------------------------------------------------- |
| SEV-0        | confirmed cross-tenant message exposure, widespread irreversible mail loss, active critical key compromise | immediate executive/security/engineering incident command |
| SEV-1        | major sending/receiving outage, large-scale account compromise, severe reputation block                    | immediate paging and incident command                     |
| SEV-2        | partial cluster outage with redundancy, significant provider-specific delivery degradation                 | urgent same-shift response                                |
| SEV-3        | limited degradation, noncritical operational defect                                                        | normal prioritized remediation                            |

Exact staffing/on-call response times are an operations policy, but telemetry must support these distinctions.

## 39.3 Emergency controls

Authorized operators need predefined emergency actions such as:

• block outbound for mailbox/domain/org;

• remove an IP/pool from new outbound assignment;

• set node draining/maintenance;

• temporarily defer inbound delivery to unsafe backend;

• revoke all sessions/app passwords for a compromised scope;

• rotate a DKIM/service credential;

• disable a vulnerable feature flag;

• freeze destructive lifecycle operations during an incident.

Each action is authenticated, audited, reversible where possible and protected from accidental global use.

## 39.4 Break-glass

Break-glass accounts/credentials are stored and tested for scenarios where the primary IAM/control plane is unavailable. Use requires at least strong independent authentication, reason capture and post-use rotation/review. Break-glass is not a convenience login.

## 39.5 Incident evidence

During incidents, operators preserve relevant logs, queue state, hashes, configuration revisions and audit records while respecting content privacy. Evidence collection should be a documented tool/workflow rather than ad-hoc copying of entire customer mailboxes.

## 39.6 Post-incident review

SEV-0/1 and selected SEV-2 incidents require a blameless technical review documenting timeline, customer impact, detection gap, root/contributing causes, recovery, corrective actions, owners/deadlines and whether this master architecture requires revision.

# 40\. Operational Governance, ADRs and Change Management

## 40.1 Architecture Decision Records

Material architectural decisions use version-controlled ADRs containing:

Title / status / date  
Context and problem  
Decision  
Alternatives considered  
Security/privacy/deliverability impact  
Cross-repository impact  
Migration/rollback implications  
Operational implications  
References  
Approvers

"Agent preference" is not an architecture rationale.

## 40.2 Changes requiring ADR

Examples:

• replacing Postfix/Dovecot/Rspamd/key identity component;

• changing mailbox storage format/topology;

• adding a new event transport;

• changing identifier or tenant semantics;

• exposing direct JMAP/other client protocol;

• adding global content indexing outside mailbox storage;

• adding bulk marketing or transactional-relay product;

• changing authentication/session architecture;

• changing data retention/recovery guarantees;

• adding staff message-content access;

• adopting a new public API major version.

## 40.3 Ownership and code review

Each shared contract has named maintainers. Changes touching authentication, tenant isolation, delivery, DKIM/DNS, retention or backup require review by the relevant security/platform owner in addition to repository code review.

## 40.4 Documentation as release artifact

Repository specifications, runbooks and shared contracts are versioned with releases. A major operational behavior change that is not documented is incomplete work.

## 40.5 Manual production actions

Emergency/manual production changes are logged in an operational change record and reconciled into code/config. Periodic audits detect unmanaged drift.

# 41\. Cross-Repository End-to-End Flows

## 41.1 Create a domain

Admin UI (webmail/control UI)  
↓ POST /api/v1/domains  
karyalay-mail  
├─ authorize organisation admin  
├─ create domain REQUESTED/OWNERSHIP_PENDING  
├─ generate verification requirement  
├─ audit  
└─ outbox domain.created  
↓  
DNS verification job  
├─ resolve TXT  
├─ mark verification result  
└─ event domain.verified  
↓  
DKIM/DNS requirement generation  
↓  
provisioning desired state  
↓  
karyalay-mail-infra reconciles routing/signing projections  
↓  
observed generation/health  
↓  
Karyalay Mail marks READY_FOR_CUTOVER / ACTIVE according to DNS/MX state  
↓  
Ops monitors DNS/auth health

Failure anywhere after DB commit leaves a visible state and retry/reconciliation path; it does not require deleting/recreating the domain.

## 41.2 Create a mailbox

Admin → karyalay-mail  
↓  
validate entitlement/domain/address uniqueness  
↓  
DB transaction: mailbox REQUESTED + desired generation + audit/outbox  
↓  
placement selection  
↓  
Infra provisioning:  
directory + recipient routing + auth mapping + storage + quota + folders  
↓  
health validation / observed_generation == desired_generation  
↓  
mailbox.provisioned  
↓  
mailbox ACTIVE  
↓  
Webmail/API becomes usable

If provisioning fails, API surfaces structured status; retry uses the same mailbox ID.

## 41.3 Receive an Internet message

Remote MTA  
↓ SMTP  
Postfix MX  
↓ recipient projection  
Rspamd/ClamAV  
↓ accepted durable Postfix queue  
Dovecot LMTP  
↓ Sieve/quota  
Mailbox storage  
↓ indexes  
User Webmail/IMAP sees message  
↓  
telemetry: queue/delivery/filter state (no body in general logs)

## 41.4 Send from webmail

Browser compose  
↓  
Webmail API draft autosave  
↓  
POST send with Idempotency-Key  
↓  
Karyalay mailbox gateway validates mailbox + From identity  
↓  
server-side submission  
↓  
Rspamd outbound policy + DKIM  
↓  
Postfix queue accepted; queue correlation stored  
↓  
API returns accepted/submitted state  
↓  
Postfix direct-to-MX retry/delivery  
↓  
Ops telemetry receives sanitized outcome  
↓  
DSN delivered to sender if final remote failure requires it

## 41.5 Compromised mailbox restriction

Ops abuse/security signals  
↓  
risk threshold / analyst confirmation  
↓  
karyalay-mail-ops opens abuse/security case  
↓ authenticated API  
karyalay-mail sets mailbox RESTRICTED + reason class  
├─ revoke relevant sessions/tokens/app passwords according to action  
├─ disable outbound sender authorization  
├─ audit + event  
└─ desired-state projection  
↓  
Infra/submission enforcement converges  
↓  
Webmail displays safe recovery/support state

Inbound mail MAY continue so business data is not lost, depending on restriction reason/policy.

## 41.6 Mailbox migration

Admin starts migration  
↓  
karyalay-mail validates destination mailbox + entitlement  
↓  
karyalay-mail-ops migration engine gets time-limited source credential/reference  
↓  
source discovery + folder mapping  
↓  
initial IMAP sync in resumable batches  
↓  
checksum/UID/message reconciliation  
↓  
incremental delta sync(s)  
↓  
DNS/MX cutover coordination  
↓  
final delta sync  
↓  
verification report  
↓  
source credential destruction  
↓  
migration.completed event/audit

Migration cannot update canonical mailbox ownership/domain state behind karyalay-mail.

## 41.7 Restore deleted mailbox

Authorized admin requests restore  
↓  
karyalay-mail verifies mailbox DELETED_RECOVERABLE + retention window  
↓  
restore job created/audited  
↓  
karyalay-mail-ops + infra restore data into isolated recovery location  
↓  
validate mailbox integrity  
↓  
reconcile address/routing conflict  
↓  
controlled cutover/rebind to original mailbox_id or defined recovered identity  
↓  
new desired generation provisioned  
↓  
ACTIVE only after validation

## 41.8 DKIM rotation

Rotation scheduler  
↓  
generate new per-domain private/public key + selector  
↓  
publish/require DNS public key  
↓  
verify globally through independent resolvers  
↓  
activate new signing selector  
↓  
overlap old selector for safety window  
↓  
retire old signing key  
↓  
remove old DNS after verification horizon  
↓  
audit each transition

# 42\. Global Definition of Done and Production Acceptance

## 42.1 Master definition of done

A feature/workstream is not complete merely when its happy path works. At shared-platform level, Done means:

• contract/schema is defined and versioned;

• owning repository is unambiguous;

• authorization/tenant checks are implemented;

• security/privacy implications are addressed;

• failure/retry/idempotency semantics are implemented;

• audit requirements are implemented where applicable;

• logs/metrics/traces are present and sanitized;

• automated tests cover happy, edge and failure paths;

• performance/capacity implications are validated;

• operational runbook exists for material failure modes;

• documentation is current;

• rollback/migration behavior is known;

• cross-repository contract tests pass.

## 42.2 GA production acceptance checklist

☐ Two or more safe inbound MX paths are operational and tested from external networks.

☐ Direct outbound delivery from production IP pools has correct PTR/EHLO/SPF/DKIM/DMARC alignment and monitoring.

☐ SMTP open-relay test suite passes.

☐ DKIM per-domain generation/rotation and recovery are tested.

☐ Inbound/outbound SPF/DKIM/DMARC/ARC flows pass interoperability tests.

☐ Mailbox provisioning is idempotent and reconciles after worker/node failure.

☐ Dovecot/IMAP works with supported desktop/mobile clients.

☐ Webmail hostile-HTML/MIME security suite passes.

☐ Browser never receives reusable raw IMAP/SMTP credentials from the product architecture.

☐ Tenant-isolation security suite passes across all APIs.

☐ MFA, session revocation and app-password lifecycle work end to end.

☐ Quota behavior is tested before/during/after hard exhaustion.

☐ Search indexes can be rebuilt without message loss.

☐ Postfix queues survive/recover from expected restart/failure scenarios.

☐ Spam/malware filter failure modes are explicitly tested.

☐ Outbound anti-abuse limits/restrictions are active before real customers send mail.

☐ Provider reputation/postmaster monitoring is configured where available.

☐ Abuse/postmaster contacts and workflows are live.

☐ Backup jobs are current, encrypted and independently protected.

☐ At least one full mailbox restore, DB PITR restore and node rebuild drill has succeeded from production-like backups.

☐ External synthetic SMTP/IMAP/HTTPS monitoring pages operators from outside the primary site.

☐ SLO dashboards and paging alerts have owners/runbooks.

☐ Security scans and independent penetration testing have no unresolved release-blocking findings.

☐ SBOM/license inventory exists for production artifacts.

☐ DR and incident-response tabletop/drill has been completed.

☐ Customer support has message-tracing tools that do not require broad content access.

☐ Migration from at least generic IMAP plus priority providers has passed resumable cutover tests.

☐ Customer-facing DNS setup accurately diagnoses MX/SPF/DKIM/DMARC states.

☐ Privacy/terms/acceptable-use/retention policies are aligned with engineering behavior.

☐ All four repository specifications conform to this master contract and have no unresolved P0 integration questions.

## 42.3 No silent-gap rule

Before GA, each repository owner signs an interface-coverage matrix mapping every inbound/outbound dependency to a shared contract. A dependency described only informally in code comments is an integration gap.

# 43\. Phased Delivery Gates

## 43.1 Gate 0 — Architecture freeze

Required before parallel repo implementation:

• this master contract approved;

• four repository ownership boundaries agreed;

• canonical entity names/IDs fixed;

• auth and tenant model fixed;

• mail-flow and storage authority fixed;

• API/event/error envelopes fixed;

• baseline technology stack fixed;

• first machine-readable contract package created.

## 43.2 Gate 1 — Engineering lab

Goal: prove mail mechanics on Karyalay-owned test domains.

Exit criteria:

• Postfix/Dovecot/Rspamd/ClamAV/Redis/DNS baseline deployed from automation;

• test domain can send/receive with major providers;

• SPF/DKIM/DMARC pass;

• IMAP/submission work securely;

• basic control-plane provisioning creates a mailbox without manual daemon edits;

• logs/metrics/queue tracing work;

• backups exist and one test restore works.

## 43.3 Gate 2 — Internal alpha

Goal: Karyalay staff use the service for selected real mailboxes.

Exit criteria:

• usable webmail baseline;

• domain/mailbox admin UX;

• MFA/sessions/app passwords;

• migration from existing mailbox source;

• spam/Junk/Sieve/quota behavior;

• anti-abuse outbound controls;

• HA for public ingress/submission;

• routine support diagnostics;

• sustained operation with no unresolved message-loss defect.

## 43.4 Gate 3 — Trusted-customer private beta

Goal: small set of existing customers under controlled onboarding.

Exit criteria:

• self-service DNS onboarding with operator review fallback;

• production backup/restore drills;

• provider reputation monitoring;

• abuse/support runbooks and on-call readiness;

• billing/entitlement integration;

• webmail feature set suitable for normal daily work;

• contract/load/security test thresholds met;

• migration/cutover process repeatable.

## 43.5 Gate 4 — General availability

Goal: sell Karyalay Email as a dependable business service.

All Section 42 GA checklist items pass, policies/support/SLOs are operational, external pentest is resolved, capacity headroom is proven and no known architectural P0 gap remains.

## 43.6 Gate 5 — Scale hardening

Triggered by actual growth, not vanity architecture. Potential work:

• additional mailbox clusters/sites;

• more sophisticated placement/rebalancing;

• improved mailbox replication/RPO;

• dedicated IP tiers;

• search/index scaling;

• richer provider reputation automation;

• stronger multi-site control/data services;

• advanced support/diagnostic automation.

These changes preserve the canonical product contracts wherever possible.

# Appendix A. Canonical Entity Catalog

| **Entity**             | **Authority**                        | **Tenant-scoped**     | **Key relationships / purpose**                              |
| ---------------------- | ------------------------------------ | --------------------- | ------------------------------------------------------------ |
| Organisation           | \`karyalay-mail\`                    | n/a root              | customer tenant and commercial boundary                      |
| OrganisationMembership | \`karyalay-mail\`                    | yes                   | identity ↔ organisation roles                                |
| MailDomain             | \`karyalay-mail\`                    | yes                   | hosted customer DNS/mail namespace                           |
| DomainVerification     | \`karyalay-mail\`                    | yes                   | ownership challenge and observations                         |
| DomainPolicy           | \`karyalay-mail\`                    | yes                   | mail/security policy chosen by customer/platform constraints |
| DKIMKeySet             | control + infra security projection  | yes                   | selectors, lifecycle, public/private key references          |
| Mailbox                | \`karyalay-mail\`                    | yes                   | mailbox storage/security principal                           |
| MailboxIdentity        | \`karyalay-mail\`                    | yes                   | authorized From/display identity                             |
| Alias                  | \`karyalay-mail\`                    | yes                   | accepted address routing and optional send-as grant          |
| DistributionGroup      | \`karyalay-mail\`                    | yes                   | bounded address expansion/posting policy                     |
| ForwardingRule         | \`karyalay-mail\`                    | yes                   | external/internal forward configuration                      |
| FilterSet              | mailbox/control + Dovecot projection | yes                   | server-side Sieve rules desired state                        |
| VacationRule           | mailbox/control + Dovecot projection | yes                   | standards-aware auto-response                                |
| AppPassword            | identity/security authority          | yes                   | revocable protocol credential reference/verifier             |
| MailboxPlacement       | control/infra observed state         | yes                   | mailbox → cluster/storage assignment/generation              |
| MailNode               | \`karyalay-mail-infra\` inventory    | no                    | role/health/capacity node identity                           |
| StorageNode            | infra inventory                      | no                    | storage capacity/failure-domain identity                     |
| SMTPPool               | control/ops/infra                    | no/entitlement scoped | outbound reputation/source pool                              |
| IPAddress              | infra/ops                            | no                    | public source/ingress identity and PTR state                 |
| MigrationJob           | \`karyalay-mail-ops\`                | yes                   | resumable source → destination orchestration                 |
| AbuseCase              | \`karyalay-mail-ops\`                | yes/platform          | evidence, action and resolution workflow                     |
| RestoreJob             | \`karyalay-mail-ops\`                | yes                   | governed mailbox/data recovery                               |
| AuditEvent             | audit subsystem                      | yes/platform          | durable administrative/security evidence                     |
| SecurityEvent          | security/ops                         | yes/platform          | security signal stream                                       |
| ProvisioningOperation  | control/infra                        | yes/platform          | desired→observed reconciliation tracking                     |

# Appendix B. Role and Permission Baseline

## B.1 Permission naming

Permissions use resource.action naming, for example:

mail_domain.read  
mail_domain.create  
mail_domain.update  
mail_domain.delete  
mailbox.read  
mailbox.create  
mailbox.update  
mailbox.delete  
mailbox.restore  
mailbox.security_reset  
alias.manage  
group.manage  
mail_policy.manage  
security_event.read  
audit.read  
billing.manage

The detailed matrix SHALL be machine-readable. UI hiding is not authorization.

## B.2 Customer-role baseline matrix

| **Capability**                       | **Owner** | **Mail Admin**   | **Helpdesk**      | **Security Admin** | **Billing Admin** | **Auditor** | **User**                |
| ------------------------------------ | --------- | ---------------- | ----------------- | ------------------ | ----------------- | ----------- | ----------------------- |
| View organisation mail configuration | ✓         | ✓                | limited           | ✓                  | limited           | ✓           | own                     |
| Add/verify domain                    | ✓         | ✓                | —                 | —                  | —                 | read        | —                       |
| Delete/release domain                | ✓         | policy           | —                 | —                  | —                 | read        | —                       |
| Create/delete mailbox                | ✓         | ✓                | limited/no delete | —                  | —                 | read        | —                       |
| Reset mailbox security/session       | ✓         | ✓                | permitted subset  | ✓                  | —                 | read        | own                     |
| Manage aliases/groups                | ✓         | ✓                | limited           | —                  | —                 | read        | own aliases if entitled |
| Manage external forwarding policy    | ✓         | ✓                | —                 | ✓ policy           | —                 | read        | own if permitted        |
| View security events                 | ✓         | policy           | limited           | ✓                  | —                 | ✓           | own                     |
| View audit events                    | ✓         | ✓                | limited           | ✓                  | —                 | ✓           | own relevant            |
| Manage administrators                | ✓         | delegated subset | —                 | security subset    | —                 | —           | —                       |
| Billing/subscription                 | ✓         | read if allowed  | —                 | —                  | ✓                 | read        | —                       |

"Policy"/"limited" means exact permissions are defined in the machine-readable contract; this table is not sufficient for code generation.

# Appendix C. Event Catalog Baseline

The following events are reserved canonical names. Repo specs may add events without changing meanings below.

| **Event**                               | **Producer**         | **Consumers/examples**   | **Meaning**                                           |
| --------------------------------------- | -------------------- | ------------------------ | ----------------------------------------------------- |
| \`organisation.created\`                | mail/control         | ops, billing projections | organisation committed                                |
| \`organisation.suspended\`              | mail/control         | infra/ops                | organisation service state restricted                 |
| \`domain.created\`                      | mail/control         | DNS/provisioning/ops     | domain resource committed                             |
| \`domain.verification_requested\`       | mail/control         | DNS jobs/UI              | ownership challenge available                         |
| \`domain.verified\`                     | mail/control         | provisioning/ops         | ownership verification succeeded                      |
| \`domain.ready_for_cutover\`            | mail/control         | UI/ops                   | infrastructure ready before MX switch                 |
| \`domain.activated\`                    | mail/control         | infra/ops                | active mail service state                             |
| \`domain.suspended\`                    | mail/control         | infra/ops                | routing/sending state changed per policy              |
| \`domain.deleted\`                      | mail/control         | infra/ops                | logical deletion entered/completed per payload state  |
| \`mailbox.requested\`                   | mail/control         | provisioning             | mailbox desired state created                         |
| \`mailbox.provisioned\`                 | provisioning/control | webmail/ops              | required observed generation ready                    |
| \`mailbox.provisioning_failed\`         | provisioning         | mail/ops                 | actionable convergence failure                        |
| \`mailbox.restricted\`                  | mail/control         | submission/webmail/ops   | security/abuse restriction active                     |
| \`mailbox.restriction_lifted\`          | mail/control         | infra/webmail/ops        | restriction removed                                   |
| \`mailbox.suspended\`                   | mail/control         | infra/webmail            | stronger admin/commercial state                       |
| \`mailbox.deleted\`                     | mail/control         | infra/ops                | deletion lifecycle entered/advanced                   |
| \`mailbox.restored\`                    | mail/control/ops     | webmail/infra            | recoverable mailbox restored/activated                |
| \`quota.changed\`                       | mail/control         | provisioning/webmail     | desired quota changed                                 |
| \`dkim.rotation_started\`               | mail/ops             | infra/DNS                | new selector lifecycle began                          |
| \`dkim.selector_activated\`             | infra/control        | ops                      | signing switched to verified selector                 |
| \`migration.started\`                   | ops                  | UI/control               | migration actively running                            |
| \`migration.progressed\`                | ops                  | UI                       | bounded progress update; may be coalesced             |
| \`migration.completed\`                 | ops                  | control/UI               | migration verified complete                           |
| \`migration.failed\`                    | ops                  | UI/support               | migration needs retry/operator action                 |
| \`restore.started\`                     | ops                  | control/audit            | recovery job began                                    |
| \`restore.completed\`                   | ops                  | control/UI               | recovery verified                                     |
| \`abuse.case_opened\`                   | ops                  | security/control         | abuse workflow created                                |
| \`abuse.mailbox_restriction_requested\` | ops                  | control                  | governed restriction command/fact boundary as defined |
| \`security.session_revoked\`            | identity/control     | webmail/ops              | session invalidated                                   |
| \`security.credential_reset\`           | identity/control     | ops/audit                | security reset completed                              |

# Appendix D. Error Catalog Baseline

| **Code**                           | **HTTP class**    | **Retry**                  | **User-safe summary**                          |
| ---------------------------------- | ----------------- | -------------------------- | ---------------------------------------------- |
| \`AUTH_REQUIRED\`                  | 401               | after auth                 | Sign in is required.                           |
| \`AUTH_INVALID\`                   | 401               | no until credential fixed  | Authentication failed.                         |
| \`AUTH_MFA_REQUIRED\`              | 401/403 by flow   | yes after challenge        | Additional verification required.              |
| \`AUTHZ_FORBIDDEN\`                | 403               | no                         | You do not have permission.                    |
| \`MAIL_DOMAIN_NOT_FOUND\`          | 404               | no                         | Domain was not found.                          |
| \`MAIL_DOMAIN_NOT_VERIFIED\`       | 409               | after verification         | Verify the domain first.                       |
| \`MAIL_DOMAIN_NOT_ACTIVE\`         | 409               | conditional                | Domain is not active.                          |
| \`MAILBOX_NOT_FOUND\`              | 404               | no                         | Mailbox was not found.                         |
| \`MAILBOX_ALREADY_EXISTS\`         | 409               | no/change request          | Address/mailbox already exists.                |
| \`MAILBOX_NOT_ACTIVE\`             | 409               | conditional                | Mailbox is not active.                         |
| \`MAILBOX_RESTRICTED\`             | 403/409           | conditional                | Mailbox is temporarily restricted.             |
| \`MAILBOX_SUSPENDED\`              | 403               | conditional                | Mailbox is suspended.                          |
| \`MAILBOX_QUOTA_EXCEEDED\`         | 409               | after space/quota change   | Mailbox storage limit reached.                 |
| \`SENDER_IDENTITY_NOT_AUTHORIZED\` | 403               | no/change sender           | Sender address is not authorized.              |
| \`MESSAGE_TOO_LARGE\`              | 413               | change payload             | Message exceeds allowed size.                  |
| \`TOO_MANY_RECIPIENTS\`            | 422/429           | change payload             | Recipient count exceeds policy.                |
| \`PROVISIONING_IN_PROGRESS\`       | 409/202 status    | yes later                  | Configuration is still being prepared.         |
| \`PROVISIONING_FAILED\`            | 409/500 by caller | after repair               | Configuration could not be completed.          |
| \`MAIL_STORAGE_UNAVAILABLE\`       | 503               | yes/backoff                | Mailbox storage is temporarily unavailable.    |
| \`DEPENDENCY_UNAVAILABLE\`         | 503               | yes/backoff                | A required service is temporarily unavailable. |
| \`RATE_LIMIT_EXCEEDED\`            | 429               | yes after delay            | Too many requests/actions.                     |
| \`ABUSE_RESTRICTED\`               | 403/429           | policy                     | Sending is restricted for security/safety.     |
| \`IDEMPOTENCY_CONFLICT\`           | 409               | no/new key/correct request | Idempotency key was reused for different data. |
| \`CONCURRENCY_CONFLICT\`           | 409/412           | refresh/retry              | Resource changed; refresh and try again.       |
| \`VALIDATION_FAILED\`              | 422               | after correction           | One or more fields are invalid.                |
| \`INTERNAL_ERROR\`                 | 500               | bounded                    | An unexpected error occurred.                  |

# Appendix E. Port and Firewall Matrix Baseline

| **Source**                   | **Destination**                  | **Port/protocol**             | **Default**                 | **Purpose**                     |
| ---------------------------- | -------------------------------- | ----------------------------- | --------------------------- | ------------------------------- |
| Internet MTAs                | MX edge                          | 25/TCP                        | allow                       | inbound SMTP                    |
| Internet mail clients        | submission edge                  | 465,587/TCP                   | allow                       | authenticated submission        |
| Internet mail clients        | IMAP edge/backends through proxy | 993/TCP                       | allow                       | secure IMAP                     |
| Internet browsers            | HTTPS edge                       | 443/TCP                       | allow                       | webmail/APIs/autoconfig/MTA-STS |
| Internet                     | POP3S                            | 995/TCP                       | deny unless product enabled | optional POP                    |
| Internet                     | ManageSieve                      | 4190/TCP                      | deny unless product enabled | optional rule client access     |
| Internet                     | MariaDB                          | 3306/TCP                      | deny                        | never public                    |
| Internet                     | Redis                            | 6379/TCP                      | deny                        | never public                    |
| MX/filter                    | local/internal Redis             | configured internal           | allow scoped                | filtering state                 |
| MX                           | Dovecot LMTP                     | internal socket/TCP           | allow scoped                | local delivery                  |
| App/mailbox gateway          | Dovecot IMAP/admin endpoint      | internal                      | allow scoped/authenticated  | server-side mailbox operations  |
| Control/provisioning         | directory/provisioning services  | internal HTTPS/DB as designed | allow scoped                | desired-state application       |
| Monitoring                   | exporters/services               | internal                      | allow scoped                | metrics/health                  |
| Backup workers               | backup targets                   | internal/backup network       | allow scoped                | encrypted backup                |
| Management path              | nodes                            | SSH/management                | allow only approved sources | automation/emergency management |
| Any unlisted cross-zone flow | any                              | any                           | deny                        | default-deny principle          |

# Appendix F. DNS and Naming Baseline

## F.1 Public service names

The final exact brand/domain naming is an Infra/product decision, but service functions SHALL map cleanly to stable names such as:

mx1.mail.karyalay.in  
mx2.mail.karyalay.in  
smtp.mail.karyalay.in  
imap.mail.karyalay.in  
mail.karyalay.in  
autoconfig.mail.karyalay.in  
autodiscover.mail.karyalay.in  
mta-sts.mail.karyalay.in  
\_spf.mail.karyalay.in

Customer MX records should target MX-specific hostnames, not a vanity webmail hostname that may move independently.

## F.2 PTR/EHLO rule

Every outbound sending IP has a stable PTR pointing to a hostname that resolves forward to the same IP where provider policy expects it, and the Postfix EHLO identity is consistent with the configured sending identity. Changes are controlled because reputation may attach to IP/name history.

## F.3 DKIM selectors

Selectors are non-secret, bounded DNS labels with lifecycle metadata. They do not contain customer secrets. Rotation naming must avoid collisions and allow at least two overlapping active/published generations.

## F.4 Domain-verification TXT

Verification record names/tokens are random/scoped and documented in the DNS contract. Tokens do not grant mailbox access and should be invalidated after domain release/transfer.

# Appendix G. SLO and Alert Baseline

| **Signal**                   | **Warning**                                  | **Page/critical consideration**                             |
| ---------------------------- | -------------------------------------------- | ----------------------------------------------------------- |
| SMTP queue oldest age        | rising above normal/provider outage baseline | sustained age threatening queue expiry or broad user impact |
| SMTP queue depth             | trend anomaly                                | rapid growth + delivery failures/saturation                 |
| Inbound 4xx rate             | above normal                                 | broad internal deferrals across healthy external traffic    |
| Outbound 4xx/5xx by provider | provider anomaly                             | widespread authentication/reputation block                  |
| Disk utilization             | 70–80% forecast                              | ≥90% strong alert; >95% emergency                           |
| Disk IO latency              | sustained above workload baseline            | delivery/IMAP SLO impact                                    |
| LMTP delivery failures       | abnormal                                     | broad failure/queue buildup                                 |
| IMAP auth failures           | anomaly                                      | credential attack/account takeover wave                     |
| Rspamd unavailable/latency   | degradation                                  | mandatory filtering path unavailable                        |
| Redis/DNS resolver health    | redundancy loss                              | filtering/delivery correctness threatened                   |
| Control API p95/errors       | SLO burn                                     | sustained budget exhaustion                                 |
| Provisioning backlog age     | above expected                               | resources stuck / user onboarding blocked                   |
| Desired vs observed drift    | nonzero beyond convergence window            | widespread/stuck drift                                      |
| Backup age                   | missed expected run                          | approaching/exceeding RPO commitment                        |
| Certificate expiry           | <30 days unresolved                          | <14/<7 days escalating                                      |
| External SMTP/IMAP synthetic | intermittent failure                         | multi-region repeated failure                               |
| Spam complaint rate          | approach internal target                     | strong intervention well before 0.3%                        |

Actual numeric thresholds are calibrated from production baselines and SLOs; alerts MUST not encode provider policy numbers without versioned ownership.

# Appendix H. Data Retention Baseline

## H.1 Retention principles

• keep content only while required by product/customer retention and backup recovery promises;

• keep security/audit evidence long enough to investigate incidents and meet policy;

• minimize broad searchable routing metadata;

• expired temporary credentials and migration secrets are destroyed promptly;

• backups age out through automated, auditable retention rather than ad-hoc manual deletion;

• retention deletion jobs are idempotent and report failures.

## H.2 Recovery-window conflict

Customer-facing deletion wording must explicitly distinguish "deleted from active mailbox" from "may remain in encrypted backups until recovery-retention expiry." Engineering must not promise instant physical eradication where backup architecture cannot provide it.

# Appendix I. Standards and Authoritative References

This appendix establishes the baseline sources repository authors and coding agents should consult. It is intentionally weighted toward standards bodies and official upstream documentation rather than tutorials.

## I.1 Internet mail and API standards

• RFC Editor — RFC 5321, Simple Mail Transfer Protocol: \`<https://www.rfc-editor.org/info/rfc5321\`>

• RFC Editor — RFC 5322, Internet Message Format: \`<https://www.rfc-editor.org/info/rfc5322\`>

• RFC Editor — RFC 6409, Message Submission for Mail: \`<https://www.rfc-editor.org/info/rfc6409\`>

• RFC Editor — RFC 9051, IMAP Version 4rev2: \`<https://www.rfc-editor.org/info/rfc9051\`>

• RFC Editor — RFC 7208, Sender Policy Framework: \`<https://www.rfc-editor.org/info/rfc7208\`>

• RFC Editor — RFC 6376, DomainKeys Identified Mail: \`<https://www.rfc-editor.org/info/rfc6376\`>

• RFC Editor — RFC 9989, DMARC (May 2026; obsoletes RFC 7489 and RFC 9091): \`<https://www.rfc-editor.org/info/rfc9989\`>

• RFC Editor — RFC 9990, DMARC Aggregate Reporting: \`<https://www.rfc-editor.org/info/rfc9990\`>

• RFC Editor — RFC 9991, DMARC Failure Reporting: \`<https://www.rfc-editor.org/info/rfc9991\`>

• RFC Editor — RFC 8617, Authenticated Received Chain: \`<https://www.rfc-editor.org/info/rfc8617\`>

• RFC Editor — RFC 8461, SMTP MTA Strict Transport Security: \`<https://www.rfc-editor.org/info/rfc8461\`>

• RFC Editor — RFC 8460, SMTP TLS Reporting: \`<https://www.rfc-editor.org/info/rfc8460\`>

• RFC Editor — RFC 6530 family, internationalized email/SMTPUTF8.

• RFC Editor — RFC 9562, UUIDs: \`<https://www.rfc-editor.org/info/rfc9562\`>

• RFC Editor — RFC 9110, HTTP Semantics: \`<https://www.rfc-editor.org/info/rfc9110\`>

• RFC Editor — RFC 9457, Problem Details for HTTP APIs: \`<https://www.rfc-editor.org/info/rfc9457\`>

## I.2 Core upstream implementation references

• Postfix official documentation: \`<https://www.postfix.org/documentation.html\`>

• Postfix Virtual Domain Hosting Howto: \`<https://www.postfix.org/VIRTUAL_README.html\`>

• Dovecot Community Edition current documentation: \`<https://doc.dovecot.org/main/\`>

• Dovecot virtual users: \`<https://doc.dovecot.org/main/core/config/auth/users/virtual.html\`>

• Dovecot LMTP: \`<https://doc.dovecot.org/main/core/config/delivery/lmtp.html\`>

• Dovecot OAuth2 authentication: \`<https://doc.dovecot.org/main/core/config/auth/databases/oauth2.html\`>

• Dovecot quota plugin: \`<https://doc.dovecot.org/main/core/plugins/quota.html\`>

• Rspamd official documentation: \`<https://docs.rspamd.com/\`>

• Rspamd modules: \`<https://docs.rspamd.com/modules/\`>

• Rspamd rate limiting: \`<https://docs.rspamd.com/modules/ratelimit/\`>

• Rspamd DKIM signing: \`<https://docs.rspamd.com/modules/dkim_signing/\`>

• Keycloak documentation: \`<https://www.keycloak.org/documentation\`>

• OpenTelemetry documentation: \`<https://opentelemetry.io/docs/\`>

## I.3 Security references

• OWASP Application Security Verification Standard 5.0: \`<https://owasp.org/www-project-application-security-verification-standard/\`>

• OWASP Top 10:2025: \`<https://owasp.org/Top10/2025/\`>

• NIST SP 800-63-4 Digital Identity Guidelines: \`<https://pages.nist.gov/800-63-4/\`>

• NIST SP 800-63B-4 Authentication and Authenticator Management: \`<https://pages.nist.gov/800-63-4/sp800-63b.html\`>

## I.4 Major recipient sender-policy references

• Gmail Email Sender Guidelines: \`<https://support.google.com/mail/answer/81126\`>

• Yahoo Sender Hub / Best Practices: \`<https://senders.yahooinc.com/best-practices/\`>

• Microsoft 365 email authentication/DMARC documentation: \`<https://learn.microsoft.com/en-us/defender-office-365/email-authentication-dmarc-configure\`>

Provider policies change faster than RFCs; Ops must verify current official guidance before changing production thresholds or deliverability runbooks.

# Appendix J. Coding-Agent Handoff Rules

## J.1 Mandatory input package

Every coding agent receives:

1\. This Master Architecture & Integration Contract  
2\. Its repository-specific engineering specification  
3\. The exact shared contracts package/version  
4\. Approved ADRs affecting the repository  
5\. Development/test environment bootstrap instructions  
6\. Definition-of-done and repository acceptance test suite

An agent may not assume access to undocumented decisions from another agent's conversation.

## J.2 No contract invention

If a needed cross-repository endpoint/event/field is missing, the agent SHALL create a contract-gap issue/ADR proposal. It MUST NOT invent a local production contract and expect the other repo to discover it later.

## J.3 Mock-first parallel development

Each repository SHALL provide/use generated mocks/fakes from canonical contracts so parallel development does not require another repository to be finished. Mocks must emulate documented error/failure cases as well as happy paths.

## J.4 Cross-repository change procedure

A proposed shared change includes:

**1\.** reason/use case;

**2\.** affected schemas/endpoints/events;

**3\.** backward-compatibility analysis;

**4\.** affected repositories;

**5\.** security/privacy/deliverability impact;

**6\.** rollout order;

**7\.** migration/dual-read/dual-write/dual-publish period if needed;

**8\.** contract tests proving compatibility;

**9\.** approval before implementation becomes authoritative.

## J.5 Forbidden agent shortcuts

Agents MUST NOT:

• expose databases directly to another UI/repo to "save time";

• put browser IMAP/SMTP credentials into local storage;

• create a second outbound message queue after Postfix acceptance;

• disable TLS/auth/spam/tenant controls to make tests pass;

• use one shared DKIM private key for all customers;

• hard-code customer domains/IPs into application source;

• silently auto-create infrastructure resources without desired-state/audit tracking;

• catch broad errors and return success;

• log secrets/message bodies for debugging;

• rely on local filesystem paths across service boundaries;

• treat 200 HTTP as the only definition of business success for async provisioning;

• delete recoverable mailbox data synchronously on first delete click;

• change shared field names/types because a framework convention differs;

• introduce a commercial mail relay/white-label provider into the path without master-contract revision.

## J.6 Required completion report from each agent

Before its repo is accepted, the coding agent SHALL produce:

• implemented requirement matrix referencing spec section IDs;

• generated API/event contract conformance report;

• known limitations and intentionally deferred non-v1 items;

• dependency/SBOM/security scan summary;

• automated test coverage by behavior category, not only line percentage;

• performance test results for relevant SLOs;

• operational dashboards/runbooks delivered by the repo;

• migrations/upgrade/rollback instructions;

• unresolved risks (target: no P0/P1 integration gaps).

## J.7 Integration acceptance

The final four-repository integration exercise SHALL execute every Section 41 end-to-end flow plus failure variants. Integration is complete only when observed behavior matches this contract with no hand-edited production configuration or undocumented bridge code.

**End of Karyalay Email — Master Architecture & Integration Contract v1.0**

This document intentionally leaves detailed implementation mechanics to the four repository specifications while leaving no ambiguity about ownership, shared semantics, security/reliability invariants or integration boundaries. Any future feature that changes those boundaries must enter through the governed architecture-change process rather than through accidental code drift.