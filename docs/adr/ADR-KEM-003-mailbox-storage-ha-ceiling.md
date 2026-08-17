# ADR-KEM-003 — Mailbox storage HA: record the ceiling, define the exit

| Field | Value |
| --- | --- |
| Status | **ACCEPTED** |
| Date | 2026-08-16 (proposed) · 2026-08-17 (accepted) |
| Amends | Repo 3 ADR-INF-004, ADR-INF-006, §57, §61; Master §33.4, §34.3 |
| Approvers | Architecture owner (Narmesh Nigam), 2026-08-17 |

## Decision record

Accepted by the architecture owner on 2026-08-17. The honesty rule is now
binding: no deployment claims HA without proven fencing capability
(Appendix AG drill evidence); deployments without fencing run single-node
and publish measured RPO/RTO instead. The named exit triggers govern when
the DRBD/CE stage is replaced by a successor architecture. The first
deployment's fencing capability remains to be established against the
actual hosting environment (tracked in Repo 3 tasks T07.04/T07.08).

## Context and problem

Dovecot CE 2.4 **removed the replication plugin and removed director.** Repo 3
ADR-INF-004 acknowledges the constraint honestly — "honors CE single-server
support posture; avoids pretending unsupported shared cluster" — and selects
DRBD Protocol C with Pacemaker fencing as the consequence.

That reasoning is sound. What no document records is the **ceiling it imposes**:

**Idle standby cost.** Every shard requires a dedicated standby. At scale roughly
half of all mailbox-node capacity exists solely to receive replication — a
permanent tax on the largest infrastructure line item.

**Cluster manager limits.** Pacemaker membership, fencing configuration and
split-brain recovery all degrade in manageability well before a hundred nodes.

**HA and DR do not compose.** Protocol C is synchronous and therefore
latency-bound; Repo 3 §78 already mandates tests to "determine maximum safe
synchronous distance." Master §34.3 concedes the result: backup-only site
recovery "until mature multi-site replication exists." There is no path from
this design to multi-region without replacing the storage layer.

**Director removal is unpriced.** Repo 3 §25 specifies IMAP-edge routing to the
active shard via generated placement state. With director gone from CE that is
now first-party code on the on-call rotation, not upstream software.

**STONITH may be unavailable on the target hardware.** Repo 3 §57 makes fencing
mandatory and `cluster.stonith_enabled` MUST be true in production, with
promotion blocked when fencing cannot be proven. STONITH requires an independent
BMC/IPMI or a cloud fencing API. Typical VPS products expose neither. On such
hardware **mailbox HA is not implementable**, and the Appendix AL launch gate
would correctly refuse to pass.

## Decision (proposed)

**1. Record the ceiling.** DRBD active/standby on Dovecot CE is adopted as a
deliberate *stage*, not the destination. Repo 3 ADR-INF-006 is annotated
accordingly.

**2. Publish fencing capability before claiming HA.** Every deployment MUST
record whether an independent fencing path exists. Where it does not, the
deployment runs single-node mailbox storage with a **published RPO and RTO**
derived from its backup tier, and MUST NOT describe itself as highly available
in any customer-facing or internal readiness statement.

**3. Define exit triggers now.** Re-evaluate the storage layer when any of:
- shard count exceeds 20, or
- a multi-region RPO below one hour becomes a product requirement, or
- standby idle capacity cost exceeds an agreed fraction of infrastructure spend, or
- Pacemaker operational incidents exceed an agreed rate.

**4. Name the candidate successors,** so the exit is an evaluation rather than a
redesign: Dovecot Pro `obox` on object storage; shared storage with the
community director replacement; or a maintained third-party CE replication
plugin. Each is a licensing, cost and support decision, not merely technical.

## Alternatives considered

**Adopt shared storage now.** Rejected for v1. Master §32.6 explicitly defers
distributed-storage complexity, and the placement abstraction already preserves
the option.

**Dovecot Pro from the start.** Not rejected on merit — deferred as a commercial
decision that should be taken deliberately at an exit trigger rather than
implicitly at v1.

**Leave the ceiling undocumented.** Rejected. An undocumented ceiling is
discovered during a capacity emergency.

## Impact

**Security / privacy.** None.

**Deliverability.** Indirect. Mailbox unavailability causes inbound deferral
rather than loss, but sustained deferral affects sender perception of the
platform.

**Cross-repository.** Repo 3 §57, §61, Appendix AL. Repo 4 capacity forecasting
(§82) should treat shard count as a tracked threshold against the exit triggers.

**Migration / rollback.** None now. The purpose of this ADR is to keep migration
cost bounded later by preserving the `mailbox_id` + opaque `storage_key`
addressing that Repo 3 §23 already mandates.

**Operational.** Deployments without fencing must state their real RPO/RTO. This
is a documentation obligation, and it prevents a false HA claim reaching a
customer contract.

## References

- Repo 3 ADR-INF-004, ADR-INF-006, §23, §25, §57, §61, §78, Appendix AG, AL
- Master Contract §32.6, §33.4, §34.3
- Dovecot v2.4.0 release notes — replication and director removal
