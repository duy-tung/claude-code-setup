# Example: Authentication API Design

## Decision

Choose the token and refresh flow for an existing API gateway.

## Evidence

- Verified: the gateway already validates signed short-lived access tokens.
- Verified: browser clients can store refresh credentials in secure HTTP-only
  cookies.
- Verified: the public contract requires explicit revocation within five minutes.
- Unknown: the identity provider's refresh-token rotation behavior.

## Alternatives

| Option | Fits current gateway | Meets revocation | Added operations |
|---|---:|---:|---:|
| Stateless access token only | yes | no | low |
| Access + rotating refresh token | yes | yes | medium |
| Stateful session for every request | partial | yes | high |

## Conclusion

Use short-lived access tokens plus rotating refresh credentials. Confirm provider
rotation semantics before finalizing replay handling. This meets the revocation
contract without replacing the existing gateway path.
