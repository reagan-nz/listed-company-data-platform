"""Tabular parsing helpers built on pandas.

Used to pull simple HTML tables (e.g. announcement lists, financial summaries)
into a compact, metadata-friendly form. Returns small previews only.
"""

from __future__ import annotations

import io


def read_html_tables(html: str, max_tables: int = 5) -> list:
    """Return a list of pandas DataFrames parsed from HTML, or []."""
    if not html:
        return []
    try:
        import pandas as pd  # noqa: F401

        tables = pd.read_html(io.StringIO(html))
        return tables[:max_tables]
    except Exception:
        return []


def first_table_preview(html: str, max_rows: int = 5, max_cols: int = 6) -> dict:
    """Return a compact preview {columns, rows, n_rows, n_cols} of the first table."""
    tables = read_html_tables(html, max_tables=1)
    if not tables:
        return {}
    df = tables[0]
    preview = df.iloc[:max_rows, :max_cols]
    return {
        "n_rows": int(df.shape[0]),
        "n_cols": int(df.shape[1]),
        "columns": [str(c) for c in preview.columns.tolist()],
        "rows": preview.astype(str).values.tolist(),
    }
