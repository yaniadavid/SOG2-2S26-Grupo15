"""Verify HR records through Odoo's external API without printing secrets."""

import os
import subprocess
import xmlrpc.client


PROJECT = "soyg2-practica1-g15"
DB = "quetzalmart_db"
URL = "https://136.116.120.10"
LOGIN = "yania.david@gmail.com"
SECRET = "quetzalmart-integrante3-initial-password"

password = subprocess.check_output([
    "gcloud.cmd" if os.name == "nt" else "gcloud", "secrets", "versions", "access", "latest",
    f"--secret={SECRET}", f"--project={PROJECT}",
], text=True).strip()
common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common", allow_none=True)
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object", allow_none=True)
uid = common.authenticate(DB, LOGIN, password, {})
if not uid:
    raise RuntimeError("The initial password has changed; verify with the current account in Odoo")

counts = {}
for model in ("hr.department", "hr.job", "hr.employee"):
    counts[model] = models.execute_kw(DB, uid, password, model, "search_count", [[]])
assert counts["hr.department"] >= 5
assert counts["hr.job"] >= 6
assert counts["hr.employee"] >= 35
sample = models.execute_kw(DB, uid, password, "hr.employee", "search_read", [
    [("work_email", "=", "qm-hr-001@example.invalid")]],
    {"fields": ["name", "department_id", "job_id", "job_title"], "limit": 1})
assert len(sample) == 1 and sample[0]["department_id"] and sample[0]["job_id"]
print({"counts": counts, "sample_employee_has_department_and_job": True,
       "sample_job_title": sample[0]["job_title"]})
