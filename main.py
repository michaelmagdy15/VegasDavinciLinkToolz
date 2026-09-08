import argparse
import os
import sys

# Reconfigure standard streams to UTF-8 on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Ensure the project root is on the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.converter import convert_vegas_to_resolve, convert_resolve_to_vegas


def _cli_log(level: str, message: str) -> None:
    symbols = {"info": "[INFO]", "success": "[OK]", "warning": "[WARN]", "error": "[ERROR]"}
    symbol = symbols.get(level, "*")
    print(f"{symbol} {message}")


def _run_cli(args):
    mode = args.mode
    input_file = args.input
    output_file = args.output
    remap_src = args.remap_src or ""
    remap_dst = args.remap_dst or ""

    if not input_file:
        print("[ERROR] An input XML file must be specified in CLI mode.", file=sys.stderr)
        sys.exit(1)

    if not os.path.isfile(input_file):
        print(f"[ERROR] File not found: {input_file}", file=sys.stderr)
        sys.exit(1)

    print(f"Starting conversion: {input_file} (mode: {mode})...\n")
    if mode == "vegas_to_resolve":
        result = convert_vegas_to_resolve(
            input_file,
            output_path=output_file,
            remap_src=remap_src,
            remap_dst=remap_dst,
            log_fn=_cli_log,
        )
    else:
        result = convert_resolve_to_vegas(
            input_file,
            output_path=output_file,
            remap_src=remap_src,
            remap_dst=remap_dst,
            log_fn=_cli_log,
        )

    if result.success:
        print(f"\n[OK] Successfully converted -> {result.output_path}")
        sys.exit(0)
    else:
        errors = "; ".join(result.errors) if result.errors else "Unknown error"
        print(f"\n[ERROR] Conversion failed: {errors}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Vegas <-> DaVinci Resolve Timeline Bridge (FCP XML / XMEML Converter)"
    )
    parser.add_argument(
        "input",
        nargs="?",
        default=None,
        help="Path to the XML file to convert (or preload into GUI)",
    )
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Run in command-line mode without opening the GUI",
    )
    parser.add_argument(
        "-m",
        "--mode",
        choices=["vegas_to_resolve", "resolve_to_vegas"],
        default="vegas_to_resolve",
        help="Conversion direction (default: vegas_to_resolve)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Custom output file path (optional)",
    )
    parser.add_argument(
        "--remap-src",
        default="",
        help="Path prefix to find/replace (optional)",
    )
    parser.add_argument(
        "--remap-dst",
        default="",
        help="Path prefix replacement (optional)",
    )

    args = parser.parse_args()

    if args.cli:
        _run_cli(args)
    else:
        from gui.app import TimelineBridgeApp
        app = TimelineBridgeApp(initial_file=args.input)
        app.run()


if __name__ == "__main__":
    main()
