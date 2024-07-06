from re import Match, Pattern
from typing import Optional


class CaseInsensitiveMatch:
    def __init__(self, match: Match[str]):
        self.match = match

    def group(self, name: str) -> str:
        return self.match.group(name).lower()


class CaseInsensitiveRe:
    def __init__(self, regex: Pattern[str]):
        self.regex = regex

    def match(self, text: str) -> Optional[CaseInsensitiveMatch]:
        m: Optional[Match[str]] = self.regex.match(text)
        if m:
            return CaseInsensitiveMatch(m)
        return None
