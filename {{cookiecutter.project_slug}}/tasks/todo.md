# Task Plan

- [x] Review the current template structure and identify the right Poe integration point.
- [x] Add `poethepoet` and define three default Poe tasks in the backend project manifest.
- [x] Update generated project documentation to show how to install and run the new Poe commands.
- [x] Add a short review section summarizing the change and any follow-up notes.

## Review

- Added `poethepoet` to the backend dev extra so Poe is available in local development environments.
- Defined three starter commands: `poe dev`, `poe test`, and `poe frontend`.
- Documented both the recommended global install (`uv tool install poethepoet`) and the local fallback (`uv run poe ...`).
