# Wave 3 — closure record

**Date:** 2026-08-22 · Companion to [BUILD-ORDER.md](BUILD-ORDER.md) §4 Wave 3.

Wave 3's entry condition was *"this is where mocks run out"*. It has been met.
Its **exit** condition has not, and the gap is two machines rather than any
amount of remaining work.

---

## 1. The four exit gates

| Gate | Owner | State | |
| --- | --- | --- | --- |
| T05.08 — real-Dovecot + adversarial suite | Repo 1 | ☑ | 29 tests / 203 assertions against production **Dovecot 2.4.1 on mx1**, over IMAPS with a master-user session and the doveadm HTTP API. Run on the host so the credential that opens every mailbox never left it. |
| T06.09 — duplicate/ambiguous-send suite | Repo 1 | ☑ | 121 tests over 43 injected Postfix faults, asserting against the persisted A.34 record rather than a return value. Eight sabotages, each confirmed failing and reverted. |
| T03.07 — control-plane + staging hosts | Repo 3 | ⛔ | Roles, playbook, firewall rows, inventory records and negative tests all exist. **No machine exists.** |
| T03.08 — OIDC identity provider host | Repo 3 | ⛔ | Same: `idp` role, `idp.yml`, realm generation, database with WAL archiving and probes. **No machine exists.** |

The two ⛔ rows are not partially done. They are complete as code and have never
run against hardware, because the hosts they describe carry RFC 5737
documentation addresses — `203.0.113.1` and `203.0.113.2` — chosen so the values
are unroutable and recognisable rather than plausible.

`tests/config/inventory.test.mjs` refuses to let either host leave
`maintenance_state: provisioning` while a documentation address is still there.
That refusal is the reason this is a visible blocker rather than a surprise
during a Wave 4 deploy.

---

## 2. The mail plane is real now, and proving it is what found the defects

Repo 3 Phase 2's headline exit criterion had never happened. It has now, on
mx1.karyalay.site from the public Internet:

```
Internet -> postscreen -> smtpd -> Rspamd/ClamAV -> LMTP
         -> global-before sieve -> mdbox on XFS -> IMAPS 993 read back
```

with the open-relay suite probed off-host, submission proven to refuse AUTH
before STARTTLS, and a message signed at submission (`d=karyalay.site;
s=s2026a`) whose signature this host then verified from public DNS —
`R_DKIM_ALLOW{karyalay.site:s=s2026a}`.

**Three defects surfaced, and every one of them failed open on a host reporting
healthy.** Full account in
[karyalay-mail-infra/evidence/phase-02/end-to-end-delivery.md](../../karyalay-mail-infra/evidence/phase-02/end-to-end-delivery.md).

| | What was true | What every signal said |
| --- | --- | --- |
| **Inbound dead 6h** | `postscreen_dnsbl_threshold = 0` is fatal; postscreen fronts port 25 and died on every start in a 60s throttle loop | `systemctl is-active` → active; port 25 open to a scan. Only tell was `Recv-Q 101` against `Send-Q 100` |
| **Global Sieve skipped** | `sievec` writes `root:root`; the delivery account could not read the compiled binaries | LMTP logged Permission denied for both scripts, **stored the message and answered 250** |
| **No sender authentication** | Rspamd pointed at `127.0.0.53` (systemd-resolved's stub) on hosts where §13 replaced it with Unbound | `dkim/spf/dmarc = temperror`. Temperror scores **zero** by design, so nothing fired and mail was delivered |

The common shape is worth carrying into Wave 4: **each defect passed every
structural gate in the repository, because each gate inspects a setting and none
asked whether the thing the setting describes actually happens.** The new checks
are all capability checks — does this resolver answer, can this account read
this file, does this port accept — not value checks.

---

## 3. Wave 4 entry

> *Entry condition: **Repo 1 serving a real API against a real mail plane.***

| Half | State |
| --- | --- |
| a real mail plane | ✅ **met** — proven end-to-end today, not asserted |
| Repo 1 serving a real API | ❌ **blocked** — there is no host to serve from, and no IdP to validate tokens against |

So Wave 4 is blocked on exactly two machines, and BUILD-ORDER already said so:
*"Wave 4 cannot open without them — Repo 1 has nowhere to serve from and no IdP
to validate against."*

### What each machine is for

**cp1.karyalay.site** — the control plane. Runs the Repo 1 API behind nginx and
terminates `api.karyalay.site`. Under ADR-INF-035 that name is DNS-only, so
**this host is the edge**: nothing upstream drops abusive traffic first, which
is why its Appendix C rows carry connection-rate and concurrency limits and why
T03.07 applies T01.03's limits to it.

**idp1.karyalay.site** — the OIDC provider, serving `id.karyalay.site`.
Established by ADR-INF-033 and made a full build by T00.08's disposition on
2026-08-21: the parent Karyalay platform operates no OIDC provider and mail is
to remain independent of it. It is a single point of failure for all browser and
API access to mail, which is why T03.08 includes its own database with backup,
PITR, a tested restore drill and availability alerting with a named pager owner.

Both are modelled as Hostinger hosts in separate failure domains. Neither
carries any mail data-plane role, and the `no-data-plane-on-platform-hosts` deny
row proves 25/465/587/143/993/4190 shut on both against the rendered ruleset —
so co-locating either on the mail plane is not an option the schema permits.
That refusal is deliberate: ADR-INF-024 keeps mail flowing through Dovecot
during an IdP outage, and a mail listener on the IdP host would delete that
mitigation.

### Promotion is mechanical once the machines exist

1. replace the two placeholder addresses in
   `inventory/environments/production.yml`;
2. flip `maintenance_state` to `active` (the inventory test then stops refusing);
3. `bootstrap.yml`, then `control-plane.yml` and `idp.yml`;
4. publish `api.karyalay.site` and `id.karyalay.site` as DNS-only A records.

Two constraints carried from earlier in the programme apply to the order:

- **Debian 13.** `bootstrap.yml` asserts it and refuses anything else — an
  Ubuntu image cost a reinstall on vps_server_4 already. Hardening written for
  one OS silently no-ops on another, which is worse than refusing.
- **A converge needs a working `--check` first.** Two read-only lookups in
  `mail_tls` were skipped under check mode and made every dry run fail; both are
  fixed, but 41 tasks repo-wide share the shape and they are **not** one fix —
  probes of existing state should run under `--check`, while "validate the
  staged candidate" tasks must not, because in check mode the candidate was
  never written.

---

## 4. Carried into Wave 4 — known, recorded, not fixed

Each of these is a real gap, none blocks Wave 4 entry, and none should be
discovered later as a surprise.

| | |
| --- | --- |
| **W-014 / W-015 / W-028 / W-033 unevidenced** | Every criterion needing a component killed **mid-transaction**: power loss during a 2xx, SIGSTOP of Rspamd during DATA, clamd stopped with mail in flight. Structurally gated, never observed. Needs a hypervisor that can hard-reset the host. |
| **DANE is configured and inert on both mail hosts** | `smtp_tls_security_level = dane` with `smtp_dns_support_level` empty, so Postfix logs `dane configured with dnssec lookups disabled` and falls back to opportunistic TLS. mx-out1 — the host that actually sends — carries no `dns-rec` role and so has no validating resolver. Ordering matters and is written down in T05.03. |
| **No `imap-edge` tier** | §25 puts public 993 on a tier no host carries, so **no mail client can reach IMAP**. The gateway reaches Dovecot over loopback; a human with Thunderbird cannot. |
| **The ACME contact is a mailbox nobody can open** | `hostmaster@karyalay.site` receives mail — it holds the probes from today — but `auth.passdb` is deliberately empty until the app-password projection lands in Phase 3, so there is no end-user credential to read it with. |
| **Neither Repo 1 exit gate runs in CI** | T05.08 and T06.09 were hand-run. Making either a gate needs a runner that can reach the private network and hold the backend credential. |
| **T03.06 is ◐** | The NATS row is blocked and the drift-alert half is unproven. |
| **`postscreen` defers the first contact from every new sender** | Correct and deliberate — an AFTER-220 test, and a compliant MTA retries. Worth knowing before someone reads a `450` in a log as an outage. |
