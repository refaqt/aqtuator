# 2026-03-23 — Handshake framing via READY/ACK/NACK and DATA_END

**Context:** Serial transport is text-based, may include debug/info chatter, and large payloads (CSV upload, data blocks) require strict framing.
**Decision:** Use explicit handshake stages (`READY`, then `ACK/NACK`) and a framed data payload (`DATA:...` header + samples + `DATA_END` terminator). Host reads until expected framing markers are received, skipping debug/info lines.
**Alternatives considered:** Implicit framing based on timeouts only, or binary streaming without clear delimiters.
**Consequences:** Higher correctness of upload/download; host code becomes stateful around expected markers.
