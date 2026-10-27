"""Command-line entry point for the Mechman WhatsApp bot."""

from __future__ import annotations

import argparse
import logging

from .config import Settings
from .whatsapp import WhatsAppBot


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the Mechman Solutions WhatsApp bot using Neonize."
    )
    parser.add_argument(
        "--pair-phone",
        default="",
        metavar="COUNTRYCODEPHONE",
        help="Pair by phone link code (digits only). Omit to use terminal QR pairing.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    settings = Settings.from_environment()
    logging.basicConfig(
        level=getattr(logging, settings.log_level, logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    bot = WhatsAppBot(settings, pair_phone=args.pair_phone)
    bot.run()


if __name__ == "__main__":
    main()
