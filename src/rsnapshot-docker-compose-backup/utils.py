from __future__ import annotations
from re import Match, Pattern

import subprocess


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


def command(cmd: str, path: str = ".") -> subprocess.CompletedProcess[str]:
    res = subprocess.run(
        cmd.split(" "),
        cwd=path,
        universal_newlines=True,
        stdout=subprocess.PIPE,
        check=False,
    )
    return res
