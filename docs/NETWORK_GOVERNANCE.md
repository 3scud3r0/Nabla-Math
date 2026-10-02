# Network governance baseline

The NablaMath network is opt-in. Local limits, consent, licenses and deny rules always
win over remote requests. No node is required to accept, execute, retain or relay an
object. A hash proves byte integrity, a signature proves control of a key, and neither
proves scientific truth.

## Roles

- **Maintainers** version protocols and publish signed releases.
- **Node owners** select policies and can stop or remove local data at any time.
- **Curators** publish immutable snapshot manifests and selection rationales.
- **Verifiers** issue scoped receipts; disagreement is preserved.
- **Incident responders** publish advisories, revocations and recovery instructions.

Protocol changes require a versioned proposal, compatibility fixtures, security review,
a migration or explicit incompatibility statement, and a rollback plan. Emergency blocks
may be shipped immediately but require a public retrospective. Public metrics must name
the snapshot, definition and observation interval. There is no token or pay-for-consensus
mechanism in the baseline protocol.
