"""Execute the read-only HR SQL checks from an Odoo shell on the VM."""

import json
import os
from pathlib import Path


sql_path = Path(os.environ.get("HR_SQL", "/tmp/validar_empleados.sql"))
for number, statement in enumerate(sql_path.read_text(encoding="utf-8").split(";"), 1):
    if not statement.strip():
        continue
    env.cr.execute(statement)
    columns = [column.name for column in env.cr.description]
    rows = [dict(zip(columns, values)) for values in env.cr.fetchall()]
    print(json.dumps({"query": number, "rows": rows}, ensure_ascii=False, default=str))
