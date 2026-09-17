from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path
    from re import Match, Pattern


class CaseInsensitiveRe:
    def __init__(self, regex: Pattern[str]):
        self.regex = regex

    def match(self, text: str) -> CaseInsensitiveMatch | None:
        m: Match[str] | None = self.regex.match(text)
        if m:
            return CaseInsensitiveMatch(m)
        return None


class CaseInsensitiveMatch:
    def __init__(self, match: Match[str]):
        self.match = match

    def group(self, name: str) -> str:
        return self.match.group(name).lower()


def command(
    cmd: str | list[str], path: Path | None = None
) -> subprocess.CompletedProcess[str]:
    if isinstance(cmd, list):
        split_cmd = cmd
    else:
        split_cmd = cmd.split()
    if path is not None:
        res = subprocess.run(
            split_cmd,
            cwd=path,
            text=True,
            stdout=subprocess.PIPE,
            check=False,
        )
    else:
        res = subprocess.run(
            split_cmd,
            text=True,
            stdout=subprocess.PIPE,
            check=False,
        )
    return res
