# Integration validation · 整合验证

Verified on macOS during repository integration (2026-09-29):

- Eight dependency-free `unittest` tests passed. They cover all six stage commands, subprocess dispatch/cwd, full-finetune selection, explicit checkpoint serving, paths containing spaces, camera roles, radians flag, action index validation and missing configuration. Subprocesses for robot/GPU execution were mocked.
- All six CLI `--dry-run` invocations ran from outside the repository without importing ML dependencies.
- Both submodule revisions and source licenses were inspected. Training/data/client contracts were reviewed statically.
- All eight provided phone videos were screened with contact sheets; selected grasp/lift/release frames were visually checked. The published MP4 decoded fully. See [media provenance](media.md).

Not rerun here: GPU environment installation, dataset conversion, normalization on the original dataset, H20 training, checkpoint loading, remote policy inference or robot motion. Historical test counts in the source repositories refer to earlier work, not this integration run. The 120-demonstration / H20 experiment is the author's confirmed prior work.

Re-run the integration checks:

```bash
python3 -m unittest discover -s tests -v
```
