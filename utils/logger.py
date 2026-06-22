"""Lightweight logging helper shared across the framework."""

import logging
import sys

_CONFIGURED = False


def get_logger(name: str = "lcdc") -> logging.Logger:
    """Return a process-wide configured logger.

    Logging is intentionally simple: a single stream handler to stderr so that
    the CSV/markdown outputs on stdout-adjacent files stay clean.
    """
    global _CONFIGURED
    logger = logging.getLogger(name)
    if not _CONFIGURED:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        )
        root = logging.getLogger("lcdc")
        root.addHandler(handler)
        root.setLevel(logging.INFO)
        root.propagate = False
        _CONFIGURED = True
    return logger
