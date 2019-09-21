import importlib.machinery
import sys


if __name__ == "__main__":
    file = sys.argv[-1]
    loader = importlib.machinery.SourceFileLoader("<py_compile>", file)
    source_bytes = loader.get_data(file)
    try:
        code = loader.source_to_code(source_bytes, file)
    except SyntaxError as e:
        print(":".join(("error", str(e.lineno), str(e.offset))), file=sys.stderr)
        print(e)
        sys.exit(1)
