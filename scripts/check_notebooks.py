"""Execute notebooks to ensure they run cleanly in CI."""

from __future__ import annotations

from pathlib import Path

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS_DIR = ROOT / "notebooks"


def main() -> int:
    """Execute every starter notebook from the repository root."""
    notebooks = sorted(NOTEBOOKS_DIR.glob("*.ipynb"))
    if not notebooks:
        raise FileNotFoundError(f"No notebooks found in {NOTEBOOKS_DIR}")

    for notebook_path in notebooks:
        print(f"Executing {notebook_path.name}")
        notebook = nbformat.read(notebook_path, as_version=4)
        client = NotebookClient(
            notebook,
            timeout=120,
            kernel_name="python3",
            resources={"metadata": {"path": str(ROOT)}},
        )
        client.execute()

    print(f"Executed {len(notebooks)} notebooks successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
