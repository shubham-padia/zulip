"""Copy each case's bot input into its own otherwise empty scratch folder."""
import json, shutil, sys
from pathlib import Path
root = Path(__file__).resolve().parents[2]
scratch = Path(sys.argv[1])
for case in json.loads((root / "eval2/cases.json").read_text()):
    for r in (1, 2):
        d = scratch / "bot" / f"{case['id']}-r{r}"
        d.mkdir(parents=True, exist_ok=True)
        shutil.copy(root / f"eval2/inputs/{case['id']}.cutoff.md", d / "input.md")
