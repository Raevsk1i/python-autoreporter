"""Точка входа приложения python-autoreporter."""

import logging
import sys

from ui.main_window import run_application


def main() -> int:
    """Запускает графический интерфейс приложения."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    return run_application()


if __name__ == "__main__":
    sys.exit(main())
