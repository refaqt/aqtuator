# 2026-10-22 — The wrap command crashed the open FreeCAD window, twice

**What happened:** An agent added the ACE TA17-7 damper to the parts library. It ran
`doqs wrap` against the FreeCAD window the user had open. FreeCAD closed at once, with no
message. The user restarted FreeCAD, and the agent ran the same command again. FreeCAD closed
again. Any work the user had not saved in that window was at risk both times.

**Root cause:** `doqs wrap` sends its macro to the open window with the add-on's background
call, `execute_code_async`. The add-on runs that call on a worker thread, not on the main
thread of FreeCAD. Its code says that document changes from there must go through a `commit()`
helper. The wrap macro creates a document, imports the STEP file and saves it directly from the
worker thread. FreeCAD does not allow window and document work off its main thread, so it
crashed. The add-on's normal call, `execute_code`, runs on the main thread and works.

**Why it was missed:** The doqs log of 2026-10-07 checked `doqs wrap` only with a FreeCAD window
started for the job, because the open window had no RPC server that day. The path through the
open window was never run against a real FreeCAD. After the first crash, the agent blamed the
step before it, and did not read the error well: it came from the status poll, after the macro
had started.

**Fix applied:** The damper wrapper was built with the add-on's normal call. The doqs bug is
reported for a fix in the doqs repository.

**Prevention rule:** Do not run `doqs wrap --mode rpc` or `--mode auto` against a FreeCAD window
that holds the user's work, until doqs runs the macro on the main thread. If FreeCAD closes during
a command, stop. Find the cause before you run anything against FreeCAD again.
