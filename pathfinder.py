import ast
from path_visitor import UnreachablePathVisitor


def analyze(path):
    try:
        with open(path, 'r') as file:
            visitor = UnreachablePathVisitor()
            code = file.read()

            tree = ast.parse(code)
            output = visitor.visit(tree)

            if len(output) == 0:
                print('No unreachable paths found.')
            else:
                paths = 'paths' if len(output) > 1 else 'path'
                lines = 'lines' if len(output) > 1 else 'line'
                nums = ', '.join(map(str, output))

                print(f'Unreachable {paths} found in {lines} {nums}.')
    except IOError:
        print('Error: Couldn\'t read file. Is there a file named code.txt in the root?')


if __name__ == '__main__':
    analyze('code.txt')
