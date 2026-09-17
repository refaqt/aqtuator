# 2026-09-17 — Downloads with `uv` fail on this network, and the error hides it

**What happened:** The FreeCAD bridge would not start. The session reported only
"Connection closed". The real error appeared when the download was run by hand:
`invalid peer certificate: UnknownIssuer` for `https://pypi.org/simple/`.

**Root cause:** Something on this network hands out its own certificates for secure
traffic — a company proxy or antivirus software that inspects it. `uv` carries its own
list of trusted certificate issuers and does not know that one, so every package
download fails. `git`, `pip` and the browser use the Windows list and keep working,
which makes the failure look like a problem with the one tool that broke.

**Fix applied:** Add `--system-certs` to the `uv` and `uvx` command. `uv` then uses the
Windows certificate list.

```bash
uv tool install --system-certs freecad-mcp
uvx --system-certs freecad-mcp --only-text-feedback
```

**Prevention rule:** On this computer, every `uv` or `uvx` command that downloads
something needs `--system-certs`. When a program that is started for you fails with
nothing but "Connection closed", run the same command by hand first and read the real
error. `--native-tls` is the older name of the same flag and is deprecated in uv
0.12.14.

**Affected files:** `.mcp.json` (machine-local, not committed),
[`docs/log/2026-09-17_freecad-mcp-bridge.md`](../log/2026-09-17_freecad-mcp-bridge.md)
