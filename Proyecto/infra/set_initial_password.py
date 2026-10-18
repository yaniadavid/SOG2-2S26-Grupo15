"""Asigna una contraseña inicial de Odoo y la guarda en GCP Secret Manager.

No muestra contraseñas ni tokens. Ejemplo:
python set_initial_password.py LOGIN NOMBRE_DEL_SECRETO
"""

import base64
import json
import secrets
import shutil
import subprocess
import sys
import urllib.request
import xmlrpc.client


PROJECT = "soyg2-practica1-g15"
BASE_URL = "https://136.116.120.10"
DATABASE = "quetzalmart_db"
ADMIN_SECRET = "quetzalmart-odoo-admin-password"


def gcloud_output(*args: str) -> str:
    gcloud = shutil.which("gcloud")
    if not gcloud:
        raise RuntimeError("gcloud no está disponible")
    result = subprocess.run(
        [gcloud, *args], capture_output=True, text=True, check=False
    )
    if result.returncode:
        raise RuntimeError(f"gcloud falló en {args[0]}")
    return result.stdout.strip()


def post_json(url: str, token: str, data: dict) -> dict:
    request = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("Uso: set_initial_password.py LOGIN NOMBRE_DEL_SECRETO")
    login, target_secret = sys.argv[1:]
    if not target_secret.startswith("quetzalmart-"):
        raise ValueError("El secreto debe pertenecer a QuetzalMart")

    admin_password = gcloud_output(
        "secrets", "versions", "access", "latest",
        f"--secret={ADMIN_SECRET}", f"--project={PROJECT}",
    )
    common = xmlrpc.client.ServerProxy(f"{BASE_URL}/xmlrpc/2/common")
    admin_uid = common.authenticate(DATABASE, "admin", admin_password, {})
    if not admin_uid:
        raise RuntimeError("La contraseña de administrador no autentica")

    object_api = xmlrpc.client.ServerProxy(f"{BASE_URL}/xmlrpc/2/object")
    user_ids = object_api.execute_kw(
        DATABASE, admin_uid, admin_password, "res.users", "search",
        [[("login", "=", login)]], {"limit": 2},
    )
    if len(user_ids) != 1:
        raise RuntimeError("Se esperaba una sola cuenta de Odoo con ese login")

    # Evita sobrescribir una credencial que pudiera estar ya en uso.
    gcloud = shutil.which("gcloud")
    exists = subprocess.run(
        [gcloud, "secrets", "describe", target_secret, f"--project={PROJECT}"],
        capture_output=True, check=False,
    )
    if exists.returncode == 0:
        raise RuntimeError("El secreto ya existe; no se cambió la contraseña")

    password = secrets.token_urlsafe(32)
    token = gcloud_output("auth", "print-access-token")
    base = f"https://secretmanager.googleapis.com/v1/projects/{PROJECT}/secrets"
    post_json(
        f"{base}?secretId={target_secret}", token,
        {"replication": {"automatic": {}}},
    )
    post_json(
        f"{base}/{target_secret}:addVersion", token,
        {"payload": {"data": base64.b64encode(password.encode()).decode()}},
    )

    updated = object_api.execute_kw(
        DATABASE, admin_uid, admin_password, "res.users", "write",
        [user_ids, {"password": password}],
    )
    if not updated:
        raise RuntimeError("Odoo no confirmó el cambio de contraseña")
    member_uid = common.authenticate(DATABASE, login, password, {})
    if member_uid != user_ids[0]:
        raise RuntimeError("No se pudo verificar el nuevo inicio de sesión")
    print(f"login_ready=true user_id={member_uid} secret={target_secret}")


if __name__ == "__main__":
    main()
