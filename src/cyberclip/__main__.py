"""CyberClip unified entry point.

Dispatches to TUI, GUI, or Web interface based on command-line arguments.
"""

import argparse
import sys


def main():
    """Main dispatcher for CyberClip interfaces."""
    parser = argparse.ArgumentParser(
        prog="cyberclip",
        description="CyberClip - Parse and enrich cybersecurity observables",
        epilog="Use 'cyberclip-tui', 'cyberclip-gui', or 'cyberclip-web' to launch directly.",
    )

    parser.add_argument(
        "interface",
        nargs="?",
        default="tui",
        choices=["tui", "gui", "web"],
        help="Interface to launch (default: tui)",
    )

    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host for web interface (default: 127.0.0.1)",
    )

    parser.add_argument(
        "--port", type=int, default=5001, help="Port for web interface (default: 5001)"
    )

    parser.add_argument(
        "--debug", action="store_true", help="Enable debug mode (web interface only)"
    )

    args = parser.parse_args()

    if args.interface == "tui":
        from cyberclip.app import main as tui_main

        sys.exit(tui_main())

    elif args.interface == "gui":
        from cyberclip.radialUI import main as gui_main

        sys.exit(gui_main())

    elif args.interface == "web":
        from cyberclip.flask_app import main as web_main

        sys.exit(web_main(host=args.host, port=args.port, debug=args.debug))


if __name__ == "__main__":
    main()
