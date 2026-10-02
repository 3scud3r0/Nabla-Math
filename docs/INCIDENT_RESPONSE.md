# Incident response baseline

Report suspected vulnerabilities privately through `SECURITY.md`. Do not include private
data, live credentials or exploit payloads in public issues.

## Severity and actions

1. **Critical:** active arbitrary execution, signing-key compromise or material private-data
   exposure. Disable affected distribution paths, revoke keys, publish a minimal advisory
   and prepare a fixed release.
2. **High:** remotely triggered denial of service, policy bypass or dataset poisoning.
   Quarantine affected objects/peers and suspend vulnerable processing.
3. **Moderate/low:** integrity, availability or documentation defects without active
   compromise. Track and fix through the normal release process.

Every incident records detection time, affected versions and object IDs, containment,
recovery, notification, evidence preservation and follow-up owners. Retractions and key
revocations are additive signed records. They cannot guarantee deletion from independent
peers. Recovery requires clean installation, integrity audit and explicit re-enablement;
workers never restart contribution merely because a server requests it.
