"""Read-only audit for the QuetzalMart HR minimums; run with odoo shell."""

import json


departments = env["hr.department"].search([], order="id")
jobs = env["hr.job"].search([], order="id")
employees = env["hr.employee"].search([], order="id")
companies = env["res.company"].search([], order="id")

report = {
    "database": env.cr.dbname,
    "departments": [{"id": d.id, "name": d.name, "company": d.company_id.name or None,
                     "active": d.active} for d in departments],
    "jobs": [{"id": j.id, "name": j.name, "department": j.department_id.name or None,
              "company": j.company_id.name or None} for j in jobs],
    "employees": [{"id": e.id, "name": e.name, "job": e.job_id.name or None,
                   "department": e.department_id.name or None,
                   "company": e.company_id.name or None,
                   "active": e.active} for e in employees],
    "companies": [{"id": c.id, "name": c.name} for c in companies],
    "hr_employee_branch_fields": [f for f in env["hr.employee"]._fields if "branch" in f or "sucursal" in f],
    "hr_employee_available_fields": [f for f in ("work_email", "work_location", "job_title", "user_id", "barcode")
                                     if f in env["hr.employee"]._fields],
    "administrator_user": employees.filtered(lambda e: e.name == "Administrator").mapped("user_id.login"),
}
print(json.dumps(report, ensure_ascii=False, indent=2))
