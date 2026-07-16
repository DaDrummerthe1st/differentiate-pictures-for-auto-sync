#!/usr/bin/env python3
"""Create one of photo-server's two accounts.

Usage (from server/, so the app package resolves):
    uv run python -m scripts.create_account --email joakim.reuterborg@gmail.com --role admin
    uv run python -m scripts.create_account --email elisabeth.reuterborg@gmail.com --role member

Password is read from the CREATE_ACCOUNT_PASSWORD env var if set,
otherwise prompted for interactively (not echoed) - never taken as a
CLI argument, which would leak it into shell history/process listings.
"""

import argparse
import getpass
import os
import sys

from app.accounts import create_account
from app.db import get_connection


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--email", required=True)
    parser.add_argument("--role", required=True, choices=["admin", "member"])
    args = parser.parse_args()

    password = os.environ.get("CREATE_ACCOUNT_PASSWORD") or getpass.getpass("Password: ")

    with get_connection() as conn:
        user_id = create_account(conn, email=args.email, password=password, role=args.role)
        conn.commit()

    print(f"Created user {user_id} ({args.email}, {args.role})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
