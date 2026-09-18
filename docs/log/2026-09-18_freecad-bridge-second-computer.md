# 2026-09-18 — The FreeCAD bridge now runs on the second computer

**Role(s):** engineering, software, cad

## What happened

FreeCAD on this computer is now connected to the agent, the same way it already works on the
first one. You open a model, press one button in FreeCAD, and the agent can measure and change
the geometry in front of you. It can never save the file. Saving stays yours, exactly as
[`doqs/docs/agent-cad.md`](../../doqs/docs/agent-cad.md) describes.

This computer had nothing of the setup yet. It has all of it now: the add-on inside FreeCAD, the
bridge program next to it, and the project configuration that connects the two.

Two things cost time, and both are now written down so the next person does not lose the same
hour.

**The certificate problem is not limited to one computer or one tool.** Downloads with `uv`
failed here with the same certificate error as before. The Microsoft Store source of the Windows
installer `winget` fails for the same reason. Something on this network replaces the
certificates that protect secure traffic, and every tool that carries its own list of trusted
issuers breaks. The two fixes are short and are now both in
[`docs/mistakes/2026-09-17_uv-download-certificate.md`](../mistakes/2026-09-17_uv-download-certificate.md).

**FreeCAD had no add-on folder at all.** FreeCAD 1.1 creates that folder only when you install
your first add-on through its own Addon Manager, and this computer had never done that. The
short instructions in [`docs/onboarding.md`](../onboarding.md) then copied the add-on into a
folder that did not exist, which quietly put the files one level too high, where FreeCAD never
reads them. The onboarding page now creates the folder first.

## Decisions

- **Both halves are pinned to the same version, 0.1.24.** The add-on inside FreeCAD and the
  bridge program talk to each other over their own private protocol, so they have to match. The
  add-on comes from the matching release tag, and the project configuration names the exact
  version. Until now only the add-on was fixed and the bridge quietly followed whatever was
  newest. This is one step stricter than the shared template, on purpose.
- **The bridge stays off until you switch it on, and it listens on this computer only.** The
  add-on can run any command inside FreeCAD. Its automatic start stays off, and "Remote
  Connections" stays off. The reasoning is in the entry for the first computer,
  [2026-09-17](2026-09-17_freecad-mcp-bridge.md), and nothing about it changed.
- **The two file-writing commands stay blocked, and pictures stay off by default.** Both guards
  were already in the project and were left alone.

## Next Steps

The last step needs the FreeCAD window and cannot be checked without it. Start FreeCAD, choose
the **MCP Addon** workbench, and click **Start RPC Server** in the **FreeCAD MCP** toolbar. Do
this before you start an agent session, because the connection is made once, at the start.

There is still no CAD model in this repository. The first one belongs under
`modules/<module>/cad/`, started from the seed file `doqs/templates/cad/build_model.py`.

<details>
<summary>Notes for reviewers</summary>

- Repository files changed: this entry, its row in `docs/log/README.md`, two lines in
  `docs/onboarding.md`, and one paragraph in `docs/mistakes/2026-09-17_uv-download-certificate.md`.
  No code.
- Machine state before this work: no `%APPDATA%\FreeCAD\v1-1\Mod` at all, no `uv` anywhere on the
  machine, nothing listening on port 9875. FreeCAD 1.1.3 installed. Python 3.14.7 on `PATH`.
- `uv` 0.12.16 installed with `winget install astral-sh.uv --source winget`. Without
  `--source winget` the command aborts: the `msstore` source fails its certificate pinning check
  with `0x8a15005e`, and winget then refuses to choose between the two sources.
- `uv tool install freecad-mcp==0.1.24` failed with `invalid peer certificate: UnknownIssuer`.
  With `--system-certs` it succeeded. The same flag is in `.mcp.json`, which is machine-local and
  not committed. It reads
  `uvx --system-certs freecad-mcp==0.1.24 --only-text-feedback`.
- The add-on was cloned at tag `v0.1.24`, commit `7519746`, verified against `git ls-remote`
  before copying, and placed at `%APPDATA%\FreeCAD\v1-1\Mod\FreeCADMCP`.
- Verified without the FreeCAD window: a handshake sent to the bridge over standard input
  returned a valid answer and listed all 17 tools. `freecadcmd` then confirmed FreeCAD 1.1.3, the
  user folder `C:\Users\niels\AppData\Roaming\FreeCAD\v1-1\`, `InitGui.py` in place, the add-on
  folder on FreeCAD's Python path, and `rpc_server` importable from it.
- `freecadcmd` loads `Init.py` only. The RPC server lives in `InitGui.py` and needs the graphical
  FreeCAD, so the final step can only be confirmed with FreeCAD open.
- Add-on defaults, read from the copied source: remote access off, allowed address `127.0.0.1`,
  automatic start off. No settings file is written until you change something, so the defaults
  apply.
- `uv tool update-shell` added `C:\Users\niels\.local\bin` to the user `PATH`. Both that and the
  winget package folder are new `PATH` entries, so a program that was already running when they
  were added will not see them until it restarts.

</details>
