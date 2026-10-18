"""Idempotent sample HR load; execute with Odoo shell and an ``env`` variable.

Run from the VM with HR_CSV=/tmp/empleados_muestra.csv. Set HR_DRY_RUN=1 to
exercise the whole import and roll it back. All new employees are fictional
and use the non-deliverable example.invalid domain.
"""

import csv
import json
import os
from pathlib import Path


source = Path(os.environ.get("HR_CSV", "/tmp/empleados_muestra.csv"))
rows = list(csv.DictReader(source.open(encoding="utf-8-sig", newline="")))
assert len(rows) == 23, len(rows)
assert len({r["codigo"] for r in rows}) == len(rows)
assert len({r["nombre"] for r in rows}) == len(rows)
company = env["res.company"].search([("name", "=", "QuetzalMart")], limit=1)
assert company, "QuetzalMart company is missing"

department_names = [
    "Operaciones de Tienda",
    "Administracion y Compras",
    "Logística e Inventario",
    "Atención al Cliente",
    "Marketing y Comercio Digital",
]
job_departments = {
    "Cajero de Sucursal": "Operaciones de Tienda",
    "Analista de Compras": "Administracion y Compras",
    "Supervisor de Tienda": "Operaciones de Tienda",
    "Coordinador de Logística": "Logística e Inventario",
    "Auxiliar de Almacén": "Logística e Inventario",
    "Agente de Atención al Cliente": "Atención al Cliente",
    "Especialista de Marketing Digital": "Marketing y Comercio Digital",
}
assert set(r["departamento"] for r in rows) <= set(department_names)
assert all(job_departments[r["cargo"]] == r["departamento"] for r in rows)

departments = {}
for name in department_names:
    matches = env["hr.department"].search([("name", "=", name), ("company_id", "=", company.id)])
    assert len(matches) <= 1, f"Duplicate department: {name}"
    department = matches or env["hr.department"].create({"name": name, "company_id": company.id})
    assert department.active
    departments[name] = department

jobs = {}
for name, dept_name in job_departments.items():
    matches = env["hr.job"].search([("name", "=", name), ("company_id", "=", company.id)])
    assert len(matches) <= 1, f"Duplicate job: {name}"
    job = matches or env["hr.job"].create({
        "name": name, "company_id": company.id,
        "department_id": departments[dept_name].id,
    })
    assert job.department_id == departments[dept_name], f"Wrong department for job: {name}"
    jobs[name] = job

created = 0
existing = 0
for row in rows:
    code = row["codigo"]
    assert code.startswith("QM-HR-") and code[-3:].isdigit()
    xml_name = f"employee_{code[-3:]}"
    external_id = env["ir.model.data"].search([
        ("module", "=", "quetzalmart_hr"), ("name", "=", xml_name),
    ], limit=1)
    expected_department = departments[row["departamento"]]
    expected_job = jobs[row["cargo"]]
    if external_id:
        assert external_id.model == "hr.employee"
        employee = env["hr.employee"].browse(external_id.res_id).exists()
        assert employee and employee.name == row["nombre"]
        assert employee.department_id == expected_department and employee.job_id == expected_job
        assert employee.active
        existing += 1
        continue
    collision = env["hr.employee"].search([
        ("name", "=", row["nombre"]), ("company_id", "=", company.id),
    ], limit=1)
    assert not collision, f"Employee name already exists without external ID: {row['nombre']}"
    employee = env["hr.employee"].create({
        "name": row["nombre"],
        "company_id": company.id,
        "department_id": expected_department.id,
        "job_id": expected_job.id,
        "work_email": f"{code.lower()}@example.invalid",
    })
    env["ir.model.data"].create({
        "module": "quetzalmart_hr", "name": xml_name,
        "model": "hr.employee", "res_id": employee.id,
    })
    created += 1

employees = env["hr.employee"].search([("active", "=", True), ("company_id", "=", company.id)])
valid = employees.filtered(lambda e: e.department_id and e.job_id and
                           e.job_id.department_id == e.department_id)
assert len(valid) >= 35, (len(employees), len(valid))
assert all(d in env["hr.department"].search([("active", "=", True)]) for d in departments.values())
assert len(jobs) >= 6
assert len([e for e in valid if e.name != "Administrator"]) >= 35
administrator_without_job = employees.filtered(
    lambda e: e.name == "Administrator" and not e.job_id).ids
dry_run = os.environ.get("HR_DRY_RUN") == "1"
if dry_run:
    env.cr.rollback()
else:
    env.cr.commit()
print(json.dumps({
    "database": env.cr.dbname,
    "dry_run": dry_run,
    "created": created,
    "already_loaded": existing,
    "active_employees": len(employees),
    "active_with_matching_job_and_department": len(valid),
    "project_departments": len(departments),
    "project_jobs": len(jobs),
    "automatic_administrator_without_job": administrator_without_job,
}, ensure_ascii=False))
