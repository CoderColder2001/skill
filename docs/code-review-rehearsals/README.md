# code-review rehearsals

This directory stores local rehearsal targets used while developing the `code-review` skill.

## Included rehearsal targets

- `demo-target-propagation`: TypeScript field propagation omission rehearsal
- `demo-target-react`: React hook dependency and form-state drift rehearsal
- `demo-target-node`: Node service path drift rehearsal

Each rehearsal target is a tiny static project snapshot representing intentionally incomplete changes and their resulting review artifacts. They preserve the source shape and generated `code-review-docs/` output used during rehearsal without carrying nested git repositories inside the main workspace.

These rehearsal assets are intentionally kept outside the `code-review/` skill directory so they do not get packaged into the distributable `.skill` archive.
