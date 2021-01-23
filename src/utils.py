from __future__ import annotations

import subprocess


class CaseInsensitiveRe:
    def __init__(self, regex):
        self.regex = regex

    def match(self, text):
        m = self.regex.match(text)
        if m:
            return CaseInsensitiveMatch(m)
        return None


class CaseInsensitiveMatch:
    def __init__(self, match):
        self.match = match

    def group(self, name):
        return self.match.group(name).lower()


def command(cmd: str, path: str = ".") -> subprocess.CompletedProcess:
    res = subprocess.run(cmd.split(" "), cwd=path, encoding="UTF-8", capture_output=True)
    return res
