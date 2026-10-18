"""Crea cuentas de integrantes con `odoo shell` sin enviar invitaciones.

Variables: ODOO_LOGIN, ODOO_NAME y ODOO_ROLE (1, 2 o 3).
No crea ni muestra contraseñas; se establecen después de forma privada.
"""

import os

login = os.environ["ODOO_LOGIN"]
name = os.environ["ODOO_NAME"]
role = os.environ["ODOO_ROLE"]
role_groups = {
    "1": (
        "sales_team.group_sale_manager",
        "purchase.group_purchase_manager",
        "account.group_account_manager",
    ),
    "2": (),  # CRM y tienda se asignan cuando sus módulos estén instalados.
    "3": ("hr.group_hr_user",),
}
if role not in role_groups:
    raise ValueError("ODOO_ROLE debe ser 1, 2 o 3")

users = env["res.users"].with_context(active_test=False)
existing = users.search([("login", "=", login)], limit=1)
if existing:
    print(f"user_exists id={existing.id} active={existing.active}")
else:
    xmlids = ("base.group_user", *role_groups[role])
    groups = [env.ref(xmlid) for xmlid in xmlids]
    user = users.with_context(no_reset_password=True).create(
        {
            "name": name,
            "login": login,
            "email": login,
            "groups_id": [(6, 0, [group.id for group in groups])],
        }
    )
    env.cr.commit()
    print(f"user_created id={user.id} active={user.active} role={role}")
    print(f"assigned_groups={','.join(xmlids)}")
