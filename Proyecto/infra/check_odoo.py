"""Consultas de solo lectura para ejecutar con `odoo shell` en la VM."""

print(f"database={env.cr.dbname}")
print(f"active_users={env['res.users'].search_count([('active', '=', True)])}")
print(f"departments={env['hr.department'].search_count([])}")
print(f"jobs={env['hr.job'].search_count([])}")
print(f"employees={env['hr.employee'].search_count([])}")
print(f"employees_with_department={env['hr.employee'].search_count([('department_id', '!=', False)])}")
print(f"employees_with_job={env['hr.employee'].search_count([('job_id', '!=', False)])}")
print(f"employees_with_both={env['hr.employee'].search_count([('department_id', '!=', False), ('job_id', '!=', False)])}")

for module_name in (
    "base",
    "sale_management",
    "purchase",
    "account",
    "hr",
    "stock",
    "crm",
    "website",
    "website_sale",
    "documents",
    "dms",
):
    module = env["ir.module.module"].search([("name", "=", module_name)], limit=1)
    print(f"module.{module_name}={module.state if module else 'unavailable'}")
