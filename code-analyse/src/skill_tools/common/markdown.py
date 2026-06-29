from __future__ import annotations

from textwrap import dedent


def render_bullet_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def replace_managed_block(document: str, marker: str, body: str) -> str:
    start = f"<!-- {marker}:managed:start -->"
    end = f"<!-- {marker}:managed:end -->"
    managed = dedent(
        f"""\
        {start}
        {body}
        {end}
        """
    ).rstrip()
    if start in document and end in document:
        prefix = document.split(start, 1)[0].rstrip()
        suffix = document.split(end, 1)[1].lstrip()
        return f"{prefix}\n{managed}\n{suffix}".rstrip() + "\n"
    return document.rstrip() + "\n\n" + managed + "\n"
