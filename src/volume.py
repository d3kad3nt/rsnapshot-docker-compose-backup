class Volume:
    def __init__(self, name: str, path: str):
        self.name = name
        self.path = path

    def __lt__(self, other):
        return self.name < other.name
