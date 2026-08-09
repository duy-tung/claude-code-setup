# Example: Frontend State Architecture

## Decision

Choose state ownership for a dashboard with server data and two local UI panels.

## Evidence

- Verified: server data already uses a query cache with invalidation.
- Verified: panel state is local and does not cross routes.
- Verified: no offline mutation queue or cross-tab synchronization is required.
- Inferred: future dashboard modules will follow the same server-data contract.

## Alternatives

| Option | Contract fit | Complexity | Reversibility |
|---|---:|---:|---:|
| Local state + existing query cache | high | low | high |
| New global store for all state | low | high | medium |
| Global store only for shared client state | medium | medium | high |

## Conclusion

Keep server data in the existing query cache and panel state local. Introduce a
global client store only after a concrete cross-route state contract appears.
This meets current requirements and avoids a speculative migration.
