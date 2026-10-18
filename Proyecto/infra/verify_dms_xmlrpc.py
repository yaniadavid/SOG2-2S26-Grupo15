"""Check DMS through Odoo's external API using team credentials in Secret Manager.

Run from the repository root with gcloud authenticated. Secrets are used only
in memory and are never printed. Initial-password secrets stop working once
team members change their passwords; in that case, use the Odoo UI instead.
"""

import base64
import os
import subprocess
import xmlrpc.client


PROJECT = "soyg2-practica1-g15"
DB = "quetzalmart_db"
URL = "https://136.116.120.10"
ACCOUNTS = (
    ("admin", "quetzalmart-odoo-admin-password", 15),
    ("yania.david@gmail.com", "quetzalmart-integrante3-initial-password", 15),
    ("javiermonjes007@gmail.com", "quetzalmart-integrante1-initial-password", 10),
)


def secret(name):
    return subprocess.check_output([
        "gcloud.cmd" if os.name == "nt" else "gcloud", "secrets", "versions", "access", "latest",
        f"--secret={name}", f"--project={PROJECT}",
    ], text=True).strip()


common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common", allow_none=True)
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object", allow_none=True)
for login, secret_name, expected in ACCOUNTS:
    password = secret(secret_name)
    uid = common.authenticate(DB, login, password, {})
    if not uid:
        print(f"{login}: password has changed; API check skipped")
        continue
    ids = models.execute_kw(DB, uid, password, "dms.file", "search", [[]])
    sample = models.execute_kw(DB, uid, password, "dms.file", "read", [ids[:1]],
                               {"fields": ["name", "content"]})[0]
    assert len(ids) == expected, (login, len(ids), expected)
    assert base64.b64decode(sample["content"]).startswith(b"%PDF-")
    print(f"{login}: {len(ids)} visible PDFs; sample download verified")
