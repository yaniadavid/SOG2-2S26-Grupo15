"""Run through ``odoo shell`` with ``env`` already provided by Odoo.

The script is idempotent. It configures OCA/dms, uploads the 15 sample PDFs,
and validates visibility and edit rights for the two existing team accounts.
On a separate test database it creates disposable test users.
"""

import base64
import hashlib
import json
import os
from pathlib import Path

from odoo.exceptions import AccessError


docs_dir = Path(os.environ.get("DMS_DOCUMENT_DIR", "/tmp/quetzalmart-dms-docs"))
manifest = json.loads((docs_dir / "manifest.json").read_text(encoding="utf-8"))
assert len(manifest) == 15
assert env["ir.module.module"].search([("name", "=", "dms")], limit=1).state == "installed"

testing = env.cr.dbname.endswith("_dms_test")
if testing:
    for login in ("dms.hr.test@example.invalid", "dms.commercial.test@example.invalid"):
        if not env["res.users"].search([("login", "=", login)], limit=1):
            env["res.users"].with_context(no_reset_password=True).create({
                "name": login.split("@")[0], "login": login,
                "email": login, "groups_id": [(4, env.ref("base.group_user").id)],
            })
    hr_login = "dms.hr.test@example.invalid"
    commercial_login = "dms.commercial.test@example.invalid"
else:
    hr_login = "yania.david@gmail.com"
    commercial_login = "javiermonjes007@gmail.com"

hr = env["res.users"].search([("login", "=", hr_login)], limit=1)
commercial = env["res.users"].search([("login", "=", commercial_login)], limit=1)
admin = env.ref("base.user_admin")
assert hr and commercial and admin
hr.write({"groups_id": [(4, env.ref("dms.group_dms_manager").id)]})
commercial.write({"groups_id": [(4, env.ref("dms.group_dms_user").id)]})

storage = env["dms.storage"].search([("name", "=", "QuetzalMart - archivo documental")], limit=1)
if not storage:
    storage = env["dms.storage"].create({"name": "QuetzalMart - archivo documental", "save_type": "file"})
assert storage.save_type == "file"

full = env["dms.access.group"].search([("name", "=", "QuetzalMart - gestion documental")], limit=1)
if not full:
    full = env["dms.access.group"].create({
        "name": "QuetzalMart - gestion documental", "perm_create": True,
        "perm_write": True, "perm_unlink": True,
        "explicit_user_ids": [(6, 0, [admin.id, hr.id])],
    })
else:
    full.write({"explicit_user_ids": [(6, 0, [admin.id, hr.id])]})

commercial_read = env["dms.access.group"].search([("name", "=", "QuetzalMart - lectura comercial")], limit=1)
if not commercial_read:
    commercial_read = env["dms.access.group"].create({
        "name": "QuetzalMart - lectura comercial", "explicit_user_ids": [(6, 0, [commercial.id])],
    })
else:
    commercial_read.write({"explicit_user_ids": [(6, 0, [commercial.id])]})
assert not commercial_read.perm_create and not commercial_read.perm_write and not commercial_read.perm_unlink

categories = {
    "Facturas de proveedores": ("Factura", "Proveedor", "Muestra"),
    "Contratos de outsourcing": ("Contrato", "Outsourcing", "Muestra"),
    "Contratos de empleados": ("Contrato", "Empleado", "Confidencial", "Muestra"),
}
directories = {}
tags = {}
for label, tag_names in categories.items():
    category = env["dms.category"].search([("name", "=", label)], limit=1)
    if not category:
        category = env["dms.category"].create({"name": label})
    root = env["dms.directory"].search([
        ("name", "=", label), ("storage_id", "=", storage.id),
        ("is_root_directory", "=", True),
    ], limit=1)
    access_ids = [full.id]
    if label != "Contratos de empleados":
        access_ids.append(commercial_read.id)
    if not root:
        root = env["dms.directory"].create({
            "name": label, "is_root_directory": True, "storage_id": storage.id,
            "category_id": category.id, "group_ids": [(6, 0, access_ids)],
        })
    else:
        root.write({"category_id": category.id, "group_ids": [(6, 0, access_ids)]})
    directories[label] = root
    tags[label] = []
    for name in tag_names:
        tag = env["dms.tag"].search([("name", "=", name), ("category_id", "=", category.id)], limit=1)
        if not tag:
            tag = env["dms.tag"].create({"name": name, "category_id": category.id})
        tags[label].append(tag.id)

created = 0
for item in manifest:
    data = (docs_dir / item["file"]).read_bytes()
    assert data.startswith(b"%PDF-")
    directory = directories[item["category"]]
    existing = env["dms.file"].search([
        ("name", "=", item["file"]), ("directory_id", "=", directory.id),
    ], limit=1)
    if existing:
        assert hashlib.sha256(base64.b64decode(existing.content)).digest() == hashlib.sha256(data).digest()
        continue
    env["dms.file"].create({
        "name": item["file"], "directory_id": directory.id,
        "category_id": directory.category_id.id,
        "tag_ids": [(6, 0, tags[item["category"]])],
        "content": base64.b64encode(data),
    })
    created += 1

env.cr.commit()
counts = {label: env["dms.file"].search_count([("directory_id", "=", directory.id)])
          for label, directory in directories.items()}
assert counts == {label: 5 for label in categories}, counts
hr_files = env["dms.file"].with_user(hr).search_count([
    ("directory_id", "in", [d.id for d in directories.values()])])
commercial_files = env["dms.file"].with_user(commercial).search_count([
    ("directory_id", "in", [d.id for d in directories.values()])])
employee_file = env["dms.file"].search([
    ("directory_id", "=", directories["Contratos de empleados"].id)], limit=1)
invoice_file = env["dms.file"].search([
    ("directory_id", "=", directories["Facturas de proveedores"].id)], limit=1)
assert hr_files == 15, hr_files
assert commercial_files == 10, commercial_files
assert not env["dms.file"].with_user(commercial).search([("id", "=", employee_file.id)])
try:
    env["dms.file"].with_user(commercial).browse(employee_file.id).content
except AccessError:
    denied_employee_content = True
else:
    denied_employee_content = False
assert denied_employee_content, "Commercial user was able to read employee contract"

# A no-op write still exercises record-rule enforcement without changing a document.
try:
    invoice_file.with_user(commercial).write({"name": invoice_file.name})
except AccessError:
    denied_commercial_write = True
else:
    denied_commercial_write = False
assert denied_commercial_write, "Read-only commercial user was able to edit a file"

download = base64.b64decode(invoice_file.with_user(commercial).content)
assert download.startswith(b"%PDF-") and len(download) > 1000
print(json.dumps({
    "database": env.cr.dbname, "created": created, "counts": counts,
    "hr_visible": hr_files, "commercial_visible": commercial_files,
    "commercial_employee_read_denied": denied_employee_content,
    "commercial_write_denied": denied_commercial_write,
    "commercial_invoice_download_bytes": len(download),
}, ensure_ascii=False))
