# 2026-09-17 — Downloads fail on this network, and the error hides it

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

**The same trap in the Windows installer `winget`.** On a second computer, 2026-09-18,
`winget install astral-sh.uv` stopped before it installed anything. It reported
`0x8a15005e : The server certificate did not match any of the expected values`, then listed the
package and asked which source to use. The Microsoft Store source checks its certificate against
a fixed list and refuses the replaced one. The `winget` source itself works. Naming it fixes the
command.

```powershell
winget install astral-sh.uv --source winget
```

**Prevention rule:** On this network, every `uv` or `uvx` command that downloads
something needs `--system-certs`, and every `winget install` needs `--source winget`.
Treat a certificate error in a new tool as this same cause, not as a broken tool. When
a program that is started for you fails with nothing but "Connection closed", run the
same command by hand first and read the real error. `--native-tls` is the older name of
the same flag and is deprecated in uv 0.12.14.

**Affected files:** `.mcp.json` (machine-local, not committed),
[`docs/log/2026-09-17_freecad-mcp-bridge.md`](../log/2026-09-17_freecad-mcp-bridge.md),
[`docs/log/2026-09-18_freecad-bridge-second-computer.md`](../log/2026-09-18_freecad-bridge-second-computer.md),
[`docs/onboarding.md`](../onboarding.md)
