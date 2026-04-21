"""Ascend-Bench rendering library.

Expose une API publique pour générer les livrables xlsx + docx à partir d'un
`bench.json` canonique (voir schemas/bench.schema.json).

Usage:
    from lib.render import render_xlsx, render_docx, render_all
"""

from lib.render import render_all, render_docx, render_xlsx

__all__ = ["render_xlsx", "render_docx", "render_all"]
