---
name: "skill-debug"
description: "Use when listing workspace skill-debug integration state, attaching skill-debug to a target skill, or maintaining target-local debug metadata."
---

# Skill Debug

Use this skill to inspect which workspace skills can use `skill-debug`, attach or repair target-local debug integration, and keep debug support isolated from a skill's business outputs.

## Supported Commands

- `/skill-debug list`
- `/skill-debug 接入 <skill-name>`

`/skill-debug 接入 <skill-name>` writes a single bare status token to stdout on success: `attached`, `already_aligned`, or `repaired`.

## Core Rules

- Discover skills from workspace `SKILL.md` files and treat frontmatter `name` as the canonical skill name.
- Report each discovered skill as `attachable`, `attached`, or `broken`, and include the target path plus any broken reason.
- Store target integration files under `<skill-root>/skill-debug/`.
- Store debug run artifacts under `<skill-root>/skill-debug-logs/`.
- Use the target-local integration files and managed `SKILL.md` block as the source of truth after attachment.
- `/skill-debug 接入 <skill-name>` must be safe to run repeatedly and repair broken target-local integration toward the canonical state.
