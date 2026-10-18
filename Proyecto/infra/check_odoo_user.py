"""Comprueba una cuenta de Odoo sin modificarla; ejecutar con `odoo shell`."""

import os

login = os.environ["ODOO_LOGIN"]
user = env["res.users"].with_context(active_test=False).search([("login", "=", login)], limit=1)
print(f"user_exists={bool(user)}")
print(f"user_active={user.active if user else 'n/a'}")

for xmlid in (
    "base.group_user",
    "hr.group_hr_user",
    "hr.group_hr_manager",
    "sales_team.group_sale_manager",
    "purchase.group_purchase_manager",
    "account.group_account_manager",
):
    group = env.ref(xmlid, raise_if_not_found=False)
    print(f"group.{xmlid}={group.id if group else 'unavailable'}")
