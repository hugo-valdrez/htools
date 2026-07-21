from argparse import ArgumentParser


TOOLS = {
    "weekly-meals": ("weekly_meals.planner", "main"),
    "file-converter": ("file_converter.file_converter", "main"),
    "data-visualizer": ("data_visualizer.main", "main"),
    "anki": ("anki.main", "main"),
}


def main(argv=None) -> None:
    args = list(argv) if argv is not None else None

    if args is None:
        import sys

        args = sys.argv[1:]

    if not args:
        parser = ArgumentParser(prog="htools")
        parser.add_argument("tool", choices=sorted(TOOLS.keys()))
        parser.print_help()
        return

    tool_name, tool_args = args[0], args[1:]
    if tool_name not in TOOLS:
        supported = ", ".join(sorted(TOOLS.keys()))
        raise ValueError(f"Unknown tool: {tool_name}. Supported: {supported}")

    module_name, function_name = TOOLS[tool_name]
    module = __import__(module_name, fromlist=[function_name])
    tool_main = getattr(module, function_name)
    tool_main(tool_args)
