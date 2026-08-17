# Karyalay Email — Infrastructure and Deployment Plan

**Status:** Phase A in progress · **Last updated:** 2026-08-18 · **Owner:** Narmesh Nigam

Companion to the five repositories of the Karyalay Email programme. The
repository specifications define *what* is built; this document records *where
it runs* and *in what order*. Deployment decisions that deviate from a
repository specification are listed in [Deviations](#deviations-to-record) and
must be ratified in the starter-profile ADR before Phase B.

> **Custody, not authority.** Kept in `karyalay-mail-contracts` because every
> repository already consumes it — see the same note in
> [BUILD-ORDER.md](BUILD-ORDER.md). This is an operational record, not a
> contract; it sits below the repository specs and ADRs in Master Contract §0.3
> precedence, and it is not a release artifact.

**See also:** [BUILD-ORDER.md](BUILD-ORDER.md) — the repository build sequence
and the cross-repo blocking matrix. This document covers infrastructure; that one
covers code. They meet at Wave 1 (contracts tag) and Wave 3 (real mail plane).

**Revised 2026-08-18** after the build-order audit (BUILD-ORDER §11): the three
hosts this plan named but no task tree owned — control plane, staging and the
IdP — are now Repo 3 T03.07/T03.08 under ADR-INF-033, and the two-origin
Cloudflare Pages setup moved from an implicit Phase 6 concern to Wave 0.

---

## 1. Domain and naming plan

`karyalay.site` is the **test and pilot domain** — this satisfies Repo 3 §6,
which requires staging to use "public test domains/IPs isolated from production
reputation." `karyalay.in` (the live business domain) stays on its current mail
provider until Phase B, and migrates only once the platform is proven.

| Hostname | Points to | Purpose | Cloudflare proxy |
| --- | --- | --- | --- |
| `mx1.karyalay.site` | Hetzner IP | SMTP (25/465/587), IMAP, PTR target | **DNS-only (grey)** |
| `mail.karyalay.site` | Cloudflare Pages project A | Webmail UI | Proxied (orange) |
| `api.karyalay.site` | Hostinger vps_server_1 | Repo 1 control-plane API | **DNS-only (grey)** — ADR-INF-035 |
| `content.karyalay.site` | Cloudflare Pages project B | Sandboxed message rendering | Proxied (orange) |
| `mta-sts.karyalay.site` | `mta-sts-policy` service (Repo 3 T05.03) | MTA-STS policy host | Proxied (orange) |

> **Critical Cloudflare rule:** any record involved in SMTP must be **DNS-only**.
> Cloudflare's proxy handles HTTP/HTTPS only — proxying `mx1` breaks mail
> delivery entirely. This is the single most common self-hosted mail mistake.

`content.karyalay.site` exists because Repo 2 §14 renders hostile HTML in a
sandboxed iframe. Serving that content from a **separate origin** means
same-origin policy still protects the session even if sandboxing is bypassed.
This cannot be retrofitted cheaply — provision it now.

Both application origins are provisioned by **Repo 3 T01.07** under
**ADR-INF-034** (`karyalay-mail-infra/docs/adr/`):
**two separate Pages projects, static assets only, no Pages Functions.** One
project with two custom domains would serve both names with identical headers
from a single deployment and reduce the split to cosmetic. The no-Functions rule
is what keeps migration to a CNAME change and a file copy; every dynamic concern
in this architecture already belongs to Repo 1 or Repo 3, so needing a Function
means something was placed in the wrong repository.

**`mta-sts` was corrected on 2026-08-18.** It was listed as a Pages origin.
Spec §47 requires an `mta-sts-policy` service serving per-customer-domain policy
at `https://mta-sts.<domain>/.well-known/mta-sts.txt` with a generated tenant
mapping — request-time multi-tenant behaviour that Pages cannot express, and
that breaks at the second customer domain. Repo 3 T05.03 builds it.

### Third-party TLS termination — decided 2026-08-18 (ADR-INF-035)

`api.karyalay.site` was planned as proxied. That was never a decision, it was
inherited from "everything goes behind Cloudflare" — reasonable for a website,
consequential for a mail platform, because a proxied hostname means **Cloudflare
terminates TLS** and reads message bodies, attachment metadata and session
tokens at the edge.

**The rule now in force:** no Karyalay hostname may terminate TLS at a third
party while carrying message content, credentials or session tokens **in a form
that third party can read.** It is a rule rather than a hostname choice so that
future endpoints are decided by it instead of by whoever provisions them.

That permits the static origins (no content), the MTA-STS policy host (a public
document) and R2 (backups are encrypted client-side per spec §1617, so
Cloudflare receives ciphertext only). It forbids proxying the API. Repo 4's ops
console falls under it when it gets a hostname.

Two things made this decidable now rather than later. **No customer data exists
yet**, so a clean boundary is free today and never cheaper — and unlike most of
this plan, a year of customer mail through an edge is not undone by changing your
mind. And the protection forfeited is partial anyway: `mx1` must stay DNS-only
forever because Cloudflare cannot proxy SMTP, so the platform already runs a
permanently exposed public address.

**The honest cost:** no volumetric DDoS absorption for the control plane. Stated
here rather than discovered in an incident, and no customer-facing document may
claim otherwise. The origin becomes the edge, so T01.03 gains host-layer
connection-rate limiting and T03.07 gains the ACME certificate and applies those
limits. Neither existed before — the old plan had *neither* Cloudflare lockdown
*nor* origin hardening, which is the state ADR-INF-035 actually removes.

**Reversal is cheap but must be done properly.** Flipping the proxy on is not
sufficient; that reproduces the incoherent state where Cloudflare sees content
and an attacker reaching the origin address bypasses the edge anyway. Any move to
proxied requires all three: 443 admitted only from Cloudflare's published ranges,
Authenticated Origin Pull, and a signed processor agreement before customer
content flows. Amend the ADR to do it.

### DNS record set for `karyalay.site`

| Type | Name | Value |
| --- | --- | --- |
| A | `mx1` | *(Hetzner IP)* — DNS-only |
| MX | `@` | `10 mx1.karyalay.site` |
| TXT | `@` | `v=spf1 ip4:<hetzner-ip> -all` |
| TXT | `<selector>._domainkey` | *(DKIM public key, generated at build)* |
| TXT | `_dmarc` | `v=DMARC1; p=none; rua=mailto:dmarc@karyalay.site` |
| TXT | `_mta-sts` | `v=STSv1; id=<timestamp>` |
| TXT | `_smtp._tls` | `v=TLSRPTv1; rua=mailto:tlsrpt@karyalay.site` |
| CNAME | `mail`, `content` | *(two separate Cloudflare Pages projects — Repo 3 T01.07)* |
| CNAME | `mta-sts` | *(`mta-sts-policy` service — Repo 3 T05.03, not Pages)* |
| A | `api` | *(Hostinger vps_server_1 IP)* |

Start DMARC at `p=none` and tighten to `quarantine` then `reject` only after
reports confirm alignment (AK-07).

---

## 2. Phase model

| | **Phase A — Pilot** | **Phase B — First commercial** | **Phase C — Scale** |
| --- | --- | --- | --- |
| Users | 25–50 (staff, friends) | 50–150 | 150+ |
| Domain | `karyalay.site` | `karyalay.in` migrates in | Both |
| Entry trigger | — (now) | First paying customer outside the friendly circle **and** clean AK evidence | §63 headroom: any capacity dimension forecast to cross 60–65% within 30 days |
| Monthly cost | ≈ $27 (Hetzner + volume; Hostinger already paid, Cloudflare free tier) | ≈ $90–140 | ≈ $250–400 |

*Costs revised 2026-08-18 after the June 2026 Hetzner price increase. If cost
becomes binding at Phase C, OVH and Contabo also leave port 25 open and are
materially cheaper — Contabo caps sending at ~25/min, which is 5× Hostinger but
still a ceiling worth checking against projected volume.*

Exit from Phase C's storage model is governed by ADR-KEM-003's triggers: shard
count above 20, standby idle cost exceeding an agreed spend fraction, or
Pacemaker incident rate exceeding an agreed threshold.

---

## 3. Phase A — inventory and allocation

| Resource | Spec | Role |
| --- | --- | --- |
| **Hetzner CPX22** | 2 vCPU / 4 GB / 80 GB, $22.99/mo + $0.60 IPv4 | Repo 3 mail data plane — the only box needing port 25 |
| **Hetzner volume** | **25 GB** attached 2026-08-18, ~$2/mo | Mail root (`/var/mail` or equivalent), mounted before any mail lands. Resizable in place; 50 GB was the pre-purchase estimate |
| **Hostinger vps_server_1** | existing | Existing app + Repo 1 control plane + MariaDB. Provisioned by Repo 3 **T03.07** per ADR-INF-033 |
| **Hostinger vps_server_3** | existing | Existing app + staging / deliverability testing. Repo 3 **T03.07** |
| **OIDC identity provider** | TBD | Keycloak-compatible, required from BUILD-ORDER Wave 4. Repo 3 **T03.08** — *first check whether the parent Karyalay system already runs one to federate against* |
| **Cloudflare Pages** | free | Repo 2 webmail + content origin |
| **Cloudflare DNS** | free | `karyalay.site` zone, DNSSEC |
| **Cloudflare R2** | free tier | Backups, bucket lock enabled |

**Pricing note:** Hetzner raised cloud prices substantially in June 2026. The CX
line was unavailable at purchase time; CPX is the current x86 shared-vCPU line.
Check the Arm64 (CAX) tab before buying — ARM is consistently cheaper per GB and
all mail-stack packages have solid Debian arm64 builds.

**Location — a one-way decision.** Changing region later means a new IP, which
restarts reputation warm-up from zero. Singapore (~50–80 ms from India) is
preferred over Falkenstein or Nuremberg (~150 ms) because IMAP is chatty and
latency is felt directly. Worth a price premium rather than relocating later.

**Why 4 GB is acceptable for Phase A:** ClamAV alone wants 1.5–3 GB, so at 4 GB
it must be deferred. That is an acceptable trade while the user population is
staff and friends — Rspamd alone is a reasonable posture for a trusted group,
and upgrading RAM later is a *reboot, not a migration*. Turn ClamAV on (and
upsize) the day an external paying customer is accepted.

### Phase A memory budget (4 GB, ClamAV deferred)

| Service | Realistic |
| --- | --- |
| Rspamd | 0.5–1 GB |
| Dovecot + indexes | 0.5 GB |
| Projections MariaDB | 0.5 GB |
| Redis, NATS, OpenBao, Postfix | ~0.75 GB |
| **Subtotal** | **~2.25–2.75 GB**, leaving ~1.2 GB for OS and page cache |
| *ClamAV, when enabled at Phase B* | *+1.5–3 GB → requires 8 GB box* |

---

## 4. Phase A — ordered checklist

Order matters. Steps 1–6 must complete before any mail is sent or received.

Legend: ☑ done · ◐ in progress · ☐ not started

| # | Step | Status | Rationale |
| --- | --- | --- | --- |
| 1 | Create Hetzner CPX22, Debian 13, Singapore, SSH key auth — `mx-sin-1`, **5.223.63.67** | ☑ 2026-08-18 | |
| 2 | **Blocklist-check the assigned IP** | ☑ 2026-08-18 | See AK-11 finding below |
| 3 | Attach 25 GB volume | ☑ 2026-08-18 | Mount as mail root in step 6 |
| 4 | Verify outbound port 25 egress from the server | ⛔ **BLOCKED** 2026-08-18 | AK-01 — see finding below |
| 4a | File Hetzner limit request for SMTP unblock; pay first invoice when issued | ☐ | Gating condition for all outbound mail |
| 5 | Cloudflare: add `karyalay.site` zone, change nameservers at registrar, publish records, enable DNSSEC | ☑ 2026-08-18 | Nameservers `amit`/`connie.ns.cloudflare.com`. DNSSEC live and validating |
| 5a | Set PTR in Hetzner → `mx1.karyalay.site`; verify both directions | ☑ 2026-08-18 | AK-02, AK-03 confirmed |
| 5b | File Barracuda delisting request | ☐ **deliberately deferred** | File only once Postfix is listening, TLS is in place, DKIM is published and warm-up is imminent (≈ Sept, with the Hetzner unblock). Barracuda investigates each request and **ignores repeat submissions** — a request against a dormant IP wastes the single credible attempt. Listing costs nothing meanwhile, since outbound is blocked regardless |
| 6 | Mount the volume as Dovecot mail root (XFS) | ☐ | Relocating a mail root later is a migration, not a config change |
| 7 | Offline custody: OpenBao unseal keys, DKIM private key escrow | Never in the R2 bucket the server can write to |
| 7a | **Hetzner cloud firewall + nftables baseline (§12) — HARD GATE** | Deferrable only while sshd alone is listening. Must be in place **before Redis, MariaDB, OpenBao or any other service binds a port** — an exposed unauthenticated Redis is among the most reliably exploited misconfigurations on the internet, and OpenBao holds the DKIM keys |
| 8 | Build Repo 3 (Hetzner) → Repo 1 (vps_server_1) → Repo 2 (Pages) → staging (vps_server_3) | Host provisioning for everything except the Hetzner box is Repo 3 T03.07/T03.08 (ADR-INF-033) — it had no owner before 2026-08-18 |
| 8a | Create the Cloudflare Pages projects and DNS for `mail.karyalay.site` **and** `content.karyalay.site` | ☐ **do this in Wave 0** — now owned by **Repo 3 T01.07** (ADR-INF-034). Two separate projects, static only, no Functions. Webmail Phase 0 (T00.06, T00.08) builds against the split from its first commit, and §7 item 3 makes it retrofit-impossible |
| 9 | R2 backups running with bucket lock, **and one restore actually tested** | `VERIFIED` ≠ backup job exited zero |
| 10 | Route real mail through `karyalay.site`; begin AK checklist; enable §63 monitoring | Reputation accrues only with calendar time |

Full deliverability procedure: `docs/runbooks/deliverability-readiness.md` in
**karyalay-mail-infra** (28 items, AK-01…AK-28). Cross-repository references in
this document are paths, not links — they do not resolve from a standalone
clone of this repository.

### DNS identity established — verified 2026-08-18

All records confirmed live from public validating resolvers (1.1.1.1, 8.8.8.8,
9.9.9.9), not merely present in the Cloudflare panel.

| Item | Value | Status |
| --- | --- | --- |
| **AK-02** PTR control | `5.223.63.67` → `mx1.karyalay.site` | ☑ |
| **AK-03** Forward confirmation | `mx1.karyalay.site` → `5.223.63.67` | ☑ FCrDNS confirmed |
| **AK-05** SPF authorization | `v=spf1 ip4:5.223.63.67 -all` — single record | ☑ |
| **AK-12** DNS identity stability | Records published early and held stable | ☑ |
| MX routing | `10 mx1.karyalay.site` → `5.223.63.67`, unproxied | ☑ |
| DMARC policy | `v=DMARC1; p=none; rua=mailto:dmarc@karyalay.site` | ☑ published (alignment testing is AK-07, needs outbound) |
| DNSSEC | DS `2371 13 2 E3A37…B85B20` at the `.site` registry; **AD flag set by all three public validating resolvers** | ☑ chain validates |

**Two defects caught by verification, both fixed:**

1. **Duplicate DMARC record.** Cloudflare's import scan pulled in GoDaddy's
   existing `p=quarantine … onsecureserver.net` record alongside the intended
   one. Publishing two DMARC records invalidates the entire record set — the
   domain would have had *no* effective DMARC policy while appearing correctly
   configured. Removed.
2. **Cache masking.** Both fixes initially appeared unapplied when queried
   through a caching resolver. Querying the authoritative servers directly
   (`amit.ns.cloudflare.com`, `ns1.your-server.de`) proved they had saved
   correctly. **Verify against authoritative servers, not a cached view.**

Apex and `www` remain proxied to Cloudflare from GoDaddy's parking import.
Harmless — MX points at `mx1`, not the apex — and left in place deliberately,
since a resolving apex is a marginally better signal to receivers than NXDOMAIN.

### AK-01 outbound SMTP — BLOCKED, recorded 2026-08-18

Tested from `mx-sin-1` (5.223.63.67) against Gmail, Outlook and Zoho MX hosts,
over both IPv4 and IPv6:

| Port | Result |
| --- | --- |
| 80, 443 (control) | **Open** — general outbound connectivity and DNS are fine |
| 25, 465, 587, 2525 | **Blocked**, IPv4 and IPv6 alike |

**Cause: Hetzner policy, not misconfiguration.** Hetzner blocks outbound SMTP
ports on all new Cloud accounts as anti-abuse. Removal requires a limit request,
which they generally only consider after roughly one month of account history
and a paid first invoice, assessed case by case.

**Impact is low at this point in the programme.** Outbound sending is not needed
until Repo 3 is built and configured, which is more than a month of work.
Inbound port 25, all DNS/PTR/DKIM work, and the entire build proceed unaffected.
The reputation clock cannot start before there is a mail system to send from.

**Confirmed with Hetzner 2026-08-18:** the unblock cannot be requested until the
first invoice is generated *and paid*. Expected timeline — invoice issued
~1 Sep 2026 (covering 18–31 Aug), paid same day, limit request filed
immediately after, decision typically within days. **Target: outbound SMTP
available early September 2026.** This is not on the critical path; contracts
Gate 0 and the Repo 3 build both run longer than that.

**Actions:** pay the first invoice the day it is issued and file the limit
request the same day — do not let this slip, because everything downstream of
reputation warm-up depends on it.

**Testable without the unblock:** the entire inbound path (external sender →
MX → Postfix → Rspamd → Dovecot → IMAP retrieval) and all internal
mailbox-to-mailbox delivery, since neither leaves the host. Only AK-07 (DMARC
alignment on outbound), AK-23 (warm-up ramp) and AK-24 (seed monitoring) are
genuinely gated. **Contingency:** if the request is refused, the mail
data plane relocates to a provider that permits port 25 (OVH, Contabo at ~25/min,
RackNerd). That would mean a new IP, so the decision must be taken *before* any
reputation warming begins — i.e. before Repo 3 goes live, not after.

**Related config note:** the server currently prefers IPv6 for outbound. AK-28
requires outbound IPv6 stay disabled until it has PTR and reputation evidence
equal to IPv4 — set that in the Postfix configuration when the data plane is built.

### AK-11 blocklist baseline — recorded 2026-08-18

IP `5.223.63.67` (Hetzner SIN, `mx-sin-1`), checked at provisioning before any
mail was sent.

| Blocklist | Result |
| --- | --- |
| **zen.spamhaus.org** | **Not listed** — control test against Spamhaus's `127.0.0.2` test address confirmed the resolver queries successfully, so this result is trustworthy |
| bl.spamcop.net · dnsbl.sorbs.net · psbl.surriel.com · cbl.abuseat.org · dnsbl-1.uceprotect.net · all.s5h.net | Not listed |
| b.barracudacentral.org | **Listed (127.0.0.2)** |

**Barracuda assessment: range-wide policy listing, not IP reputation.** Six of
seven sampled neighbours across `5.223.63.0/24` return the identical code,
while the same neighbours are clean on Spamhaus. Control queries confirmed
Barracuda answers `not listed` for known-clean addresses (8.8.8.8, 1.1.1.1), so
the lookup mechanism is sound and the listing is genuine — it simply applies to
the whole Hetzner Singapore block by policy.

**Decision: retain the IP.** Reallocating within the same region would land on
another listed address. Delisting to be requested via
`barracudacentral.org/rbl/removal-request` once PTR is in place. Re-check all
lists after delisting and again before Phase B.

---

## 5. Phase B and C estimates

| | **Phase B** | **Phase C** |
| --- | --- | --- |
| Hetzner mail | Upsize to 16 GB; volume → 250 GB | Split roles: 2× MX/submit edge, dedicated mailbox shard node(s) |
| Mailbox storage | Still 1 shard, vertical growth | 2nd shard **by steering new mailboxes**, never rebalancing; standby per shard once fencing is proven |
| Datastores | Single instances, or form the trio if downtime starts hurting | Quorum trio — 3 hosts each running Galera + NATS + OpenBao |
| Hostinger | KVM4 (16 GB) control plane | KVM8 (32 GB), workers scaled out |
| Networking | WireGuard + mTLS between providers (CONTROL zone crosses public internet) | Same, plus edge load balancing |
| R2 | ~$2–8/mo | ~$10–25/mo |
| **Cost/mo** | **≈ €50–80** | **≈ €150–250** |

**Scaling behaviour to remember:** the edge (MX, submission, IMAP) scales
horizontally and cheaply — but every new outbound IP needs its own warm-up, so
add submission capacity *before* it is needed. Mailbox storage does **not**
scale horizontally: Dovecot CE 2.4 removed director, so capacity is added by
bringing up a new shard and letting placement policy steer new mailboxes to it
(Repo 3 §12.2). Existing mailboxes never move unless a migration explicitly
changes their `storage_key`. Quorum services (Galera, NATS, OpenBao) are
availability tiers, not capacity tiers — scale them vertically; go 3 → 5 nodes
only when the failure budget demands it, never because load grew.

---

## 6. Deviations to record

To be ratified in a starter-profile ADR in `karyalay-mail-infra` before Phase B.

| Deviation | Spec requirement | Justification | Reverts at |
| --- | --- | --- | --- |
| Cloudflare DNS instead of self-hosted NSD | §44 | Anycast, DNSSEC, TLSA support, zero cost. In-house NSD matters once infra-controller generates zones from desired state | Phase C or when controller-generated zones ship |
| Single MariaDB / NATS / OpenBao | §7 minimum posture (3 nodes each) | Availability, not throughput, is what quorum buys; single instances with proven restore are defensible at pilot scale | Phase B/C when downtime becomes commercially unacceptable |
| Single mailbox shard, no standby | §7 (1 active + 1 standby per shard) | Permitted by ADR-KEM-003: without proven fencing, run single-node and publish measured RPO/RTO | When fencing capability is proven |
| Repo 4 deferred except migration tooling | Repo 4 phase plan | Its own §3 invariant states mail flows with every ops process stopped. Postmaster/SNDS dashboards replace collectors at this scale | Phase B/C |
| Reduced Repo 1 worker count | §3.1 process roles | RAM constraint on shared Hostinger box | On control-plane upsize |
| Public `karyalay.site` zone managed by panel, not as-code | §53 (no hand-configuration) | The as-code path does not exist yet; the zone is small and its records are reviewed in T01.07 | When zone generation from desired state ships (same trigger as the NSD row) |
| Application origins on Cloudflare Pages | §5 self-hosted posture | Static assets only, no Functions, no message content at the edge — the renderer is client-side with a zero-network proof. Reversible by CNAME change while the no-Functions rule holds (ADR-INF-034) | If an origin ever needs compute, or a customer requires no third-party CDN |

---

## 7. Cannot be retrofitted — do these in Phase A

1. **Clean, dedicated IP, warmed from day one.** Reputation is the only thing
   here that money cannot buy back. Blocklist-check before committing.
2. **PTR and forward-confirmed DNS** before the first message leaves.
3. **`content.karyalay.site` as a separate rendering origin** — retrofitting
   origin isolation into a shipped client is genuinely painful.
4. **Mail root on the volume from day one**, so growth is a volume resize
   rather than a data migration.
5. **OpenBao unseal keys and DKIM private keys held offline** — bucket locks
   are defeated if the compromised server holds credentials to the bucket
   containing the keys that would rebuild it.
6. **Restores actually tested**, not merely backup jobs succeeding.
7. **§63 monitoring from day one**, so growth signals the next phase rather
   than an outage doing it.

---

## 8. What object storage is and is not for

R2 holds **backups only**. Mailbox storage cannot live on object storage with
Dovecot CE: mdbox requires POSIX semantics — `fsync()`, file locking, partial
writes, atomic rename — none of which S3-compatible APIs provide, and IMAP's
interactive round-trips would be intolerable over object-storage latency.
Object-backed mailboxes are Dovecot Pro `obox`, which ADR-KEM-003 already names
as the first candidate successor at the storage exit trigger. Do not attempt
`s3fs` or `rclone mount` for mail: they fake `fsync` and have unreliable
locking, which for a mail store means silent corruption discovered weeks later.

---

## 9. Economics

| At 100 mailboxes | Monthly |
| --- | --- |
| Revenue at ₹150/mailbox | ₹15,000 |
| Revenue at ₹250/mailbox (premium positioning) | ₹25,000 |
| Infrastructure (Phase B) | ₹5,000–9,500 |
| **Gross** | **₹5,500 – ₹20,000** |

Costs step roughly 5× between Phase A and B, and 3× again between B and C,
while revenue grows linearly. Phase B is where unit economics begin working.
Phase A is deliberately cheap because its real job is not serving 50 people —
it is accumulating clean sending reputation and honest evidence while there is
still time to be patient about both.
