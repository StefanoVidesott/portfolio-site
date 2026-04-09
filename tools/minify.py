"""Asset minification script — runs during the Docker image build.

Usage (called automatically by the Dockerfile RUN step):
    python tools/minify.py
"""

import sys
from pathlib import Path

try:
    import rjsmin
    import rcssmin
except ImportError:
    print(
        "ERROR: rjsmin and rcssmin are required for minification. "
        "Run: pip install rjsmin rcssmin",
        file=sys.stderr,
    )
    sys.exit(1)

BASE = Path(__file__).resolve().parent.parent / "app" / "static"

TARGETS = [
    (
        BASE / "js" / "main.js",
        BASE / "js" / "main-min.js",
        rjsmin.jsmin,
        "JS",
    ),
    (
        BASE / "css" / "style.css",
        BASE / "css" / "style-min.css",
        rcssmin.cssmin,
        "CSS",
    ),
]


def minify() -> None:
    for src, dst, minifier, label in TARGETS:
        if not src.exists():
            print(f"ERROR: source file not found: {src}", file=sys.stderr)
            sys.exit(1)

        original = src.read_text(encoding="utf-8")
        minified = minifier(original)

        dst.write_text(minified, encoding="utf-8")

        original_kb = len(original.encode()) / 1024
        minified_kb = len(minified.encode()) / 1024
        reduction = 100 * (1 - minified_kb / original_kb) if original_kb else 0

        print(
            f"[minify] {label}: {src.name} → {dst.name} "
            f"({original_kb:.1f} KB → {minified_kb:.1f} KB, -{reduction:.0f}%)"
        )


if __name__ == "__main__":
    minify()
