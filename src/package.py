#!/usr/bin/env python3

import ast
import os
from typing import List

import astor

shebang = "#!/usr/bin/env python3"
imported = []
imported_files = []

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
        # manually add shebang for python3
        output.writelines([shebang, "\n\n"])
        import_file("backup-planer.py", output)


def import_file(file: str, output):
    if file in imported_files:
        return
    imported_files.append(file)
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


class TypeHintRemover(ast.NodeTransformer):

    def visit_FunctionDef(self, node):
        # remove the return type definition
        node.returns = None
        # remove all argument annotations
        if node.args.args:
            for arg in node.args.args:
                arg.annotation = None
        self.generic_visit(node)
        return node

    def visit_AnnAssign(self, node):
        if node.value is None:
            return None
        return ast.Assign([node.target], node.value)

    def visit_Import(self, node):
        node.names = [n for n in node.names if n.name != 'typing']
        return node if node.names else None

    def visit_ImportFrom(self, node):
        return node if node.module != 'typing' else None


def remove_type_hints(source: str):
    # parse the source code into an AST
    parsed_source = ast.parse(source)
    # remove all type annotations, function return type definitions
    # and import statements from 'typing'
    transformed = TypeHintRemover().visit(parsed_source)
    # convert the AST back to source code
    return astor.to_source(transformed)


def main():

    source_name = "backup-docker-compose.py"
    dest_name = "backup-docker-compose-withoutTypes.py"
    with open(source_name, "r") as sourceFile:
        source = "".join(sourceFile.readlines())
        dest = remove_type_hints(source)
        with open(dest_name, "w") as destFile:
            # manually add shebang for python3
            destFile.writelines([shebang, "\n\n"])
            destFile.write(dest)


if __name__ == "__main__":
    package()
    main()
