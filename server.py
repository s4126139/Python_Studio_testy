from __future__ import annotations

import argparse
from pathlib import Path
from wsgiref.simple_server import make_server

from pid_app import create_app


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Preventable Infectious Diseases Atlas.")
    parser.add_argument("--host", default="127.0.0.1", help="Host interface to bind to.")
    parser.add_argument("--port", type=int, default=8051, help="Port to listen on.")
    parser.add_argument("--source-db", type=Path, default=None, help="Optional path to the immutable source SQLite database.")
    parser.add_argument("--app-db", type=Path, default=None, help="Optional path to the writable working SQLite database.")
    args = parser.parse_args()

    application = create_app(source_db=args.source_db, app_db=args.app_db)

    with make_server(args.host, args.port, application) as httpd:
        print(f"Serving Preventable Infectious Diseases Atlas on http://{args.host}:{args.port}")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
