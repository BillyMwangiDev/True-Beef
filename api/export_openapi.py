import json
from pathlib import Path

from app.main import app

out = Path(__file__).resolve().parent.parent / "mobile" / "openapi.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(app.openapi(), indent=2))
print(f"wrote {out}")
