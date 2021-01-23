import os
from typing import List

imported = []


def find_python_files() -> List[str]:
    cwd = os.getcwd()
    return [file.strip(".py") for file in os.listdir(cwd)]


files = find_python_files()


def already_imported(line):
    if line in imported:
        return True
    else:
        imported.append(line)
        return False


def package():
    name = "backup-docker-compose.py"
    with open(name, "w") as output:
        import_file("backup-planer.py", output)


def import_file(file: str, output):
    with open(file, "r") as python_file:
        for line in python_file:
            if line.strip().startswith("from") or line.strip().startswith("import"):
                statement = line.strip()
                local = False
                if not already_imported(statement):
                    for local_file in files:
                        if local_file in statement:
                            import_file(local_file + ".py", output)
                            local = True
                    if not local:
                        output.write(line)
            else:
                output.write(line)


if __name__ == "__main__":
    package()
