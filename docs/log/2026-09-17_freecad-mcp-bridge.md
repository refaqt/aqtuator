# 2026-09-17 — An agent can now work in the open FreeCAD window

**Role(s):** engineering, software, cad

## What happened

FreeCAD on this computer is now connected to the agent. You open a model, press one
button in FreeCAD, and the agent can measure and change the geometry in front of you.
It can never save the file. Saving stays yours, exactly as
[`doqs/docs/agent-cad.md`](../../doqs/docs/agent-cad.md) describes.

Two pieces were missing, and both are now in place.

**The add-on inside FreeCAD.** FreeCAD needs a small add-on before anything outside it
can reach an open model. It is not in the FreeCAD add-on list, so it was copied in by
hand from [neka-nat/freecad-mcp](https://github.com/neka-nat/freecad-mcp), version
0.1.23.

**The bridge program on the computer.** It would not download. Every attempt failed
with a certificate error, and the session simply reported "Connection closed", which
says nothing about the real cause. Something on this network hands out its own
certificates — a company proxy or antivirus software that inspects secure traffic.
The download tool `uv` ships its own list of trusted certificate issuers and does not
know that one. Telling it to use the Windows list instead fixes it. That is a
machine-wide trap, not a FreeCAD one, so it is written up in
[`docs/mistakes/2026-09-17_uv-download-certificate.md`](../mistakes/2026-09-17_uv-download-certificate.md).

## The Windows folder in the guides is wrong

Both the add-on's own guide and [`doqs/docs/agent-cad.md`](../../doqs/docs/agent-cad.md)
say to put the add-on in `%APPDATA%\FreeCAD\Mod`. On FreeCAD 1.1 for Windows that folder
does not exist and the add-on is never loaded.

FreeCAD 1.1 keeps a separate folder per version. Asked directly, FreeCAD 1.1.1 on this
computer answers `C:\Users\niels\AppData\Roaming\FreeCAD\v1-1\`, and the two add-ons
installed earlier through the FreeCAD Addon Manager sit in `v1-1\Mod` as well. The
correct folder is therefore:

```
%APPDATA%\FreeCAD\v1-1\Mod\FreeCADMCP
```

A correction was proposed to the shared tooling repository, so the next person does not
lose the same hour.

## Decisions

- **The bridge stays off until you switch it on.** The add-on can run any command inside
  FreeCAD, so it should only listen while you actually want help. It offers an automatic
  start; we leave that off. It listens on this computer only, on port 9875. Leave
  "Remote Connections" off.
- **The two file-writing commands stay blocked.** `.claude/settings.json` already hides
  them, and the project checks fail if anyone removes them. Nothing about that changed.
- **Pictures stay off by default.** A screenshot costs roughly 2,700 tokens and still
  cannot tell you whether a rail is 500 mm long. The agent can still ask for one view
  when a question is genuinely visual.

## Next Steps

There is still no CAD model in this repository. The first one belongs under
`modules/<module>/cad/`, started from the seed file `doqs/templates/cad/build_model.py`.

<details>
<summary>Notes for reviewers</summary>

- Repository files changed: this entry, the row in `docs/log/README.md`, the mistake
  entry and its row, a new section in `docs/onboarding.md`, and one line in
  `cad/README.md`. No code.
- `.mcp.json` is gitignored and machine-local. It now reads
  `uvx --system-certs freecad-mcp --only-text-feedback`. The `--system-certs` flag is
  the only difference from the doqs template `doqs/templates/agent-cad/mcp.json`, and it
  is needed because of the certificate interception described above.
- `uv tool install --system-certs freecad-mcp` was run as well, so the first connection
  does not have to wait for a download. `--native-tls` does the same thing and is
  deprecated in uv 0.12.14.
- Verified without the FreeCAD window: a handshake sent to the server over standard
  input returned a valid answer, and the server reported that FreeCAD itself was not
  reachable, which was correct at that moment. `FreeCADCmd` confirmed the user folder
  and that `FreeCADMCP` reached FreeCAD's Python path.
- `FreeCADCmd` loads `Init.py` only. The RPC server lives in `InitGui.py` and needs the
  graphical FreeCAD, so the final step can only be confirmed with FreeCAD open.
- Add-on defaults, read from its source: remote access off, allowed address `127.0.0.1`,
  automatic start off.

</details>
