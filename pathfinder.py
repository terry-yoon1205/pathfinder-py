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

                print(f'Unreachable {paths} found at {lines} {nums}.')
    except IOError:
        print('Error: couldn\'t read file. Is there a file named code.txt in the root?')
    except SyntaxError as e:
        print(f'Error: {e.msg} at line {e.lineno}. Make sure the code contains no compilation errors.')
    except Exception:
        print('Error: analysis failed. Make sure the code only contains supported constructs.')


if __name__ == '__main__':
    analyze('code.txt')
