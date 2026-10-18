# Despliegue de Odoo Community en GCP

## Acceso

- URL: **https://136.116.120.10/web/login**
- Proyecto: `soyg2-practica1-g15`.
- Cuenta activa de `gcloud`: `3020696740101@ingenieria.usac.edu.gt`.
- Acceso administrativo a la VM: `gcloud compute ssh quetzalmart-odoo --zone=us-central1-a --project=soyg2-practica1-g15 --tunnel-through-iap`.
- La contraseña del usuario `admin` de Odoo está en Secret Manager, secreto `quetzalmart-odoo-admin-password`. La del gestor de bases de datos está en otro secreto, `quetzalmart-odoo-master-password`. No compartirlas por chat ni añadirlas al repositorio.
- Integrante 1: contraseña inicial en `quetzalmart-integrante1-initial-password`. Integrante 3: contraseña inicial en `quetzalmart-integrante3-initial-password`. Cada integrante debe cambiarla después de entrar. Para verla de forma privada: `gcloud secrets versions access latest --secret=NOMBRE_DEL_SECRETO --project=soyg2-practica1-g15`.

## Estado verificado el 17 de octubre de 2026 y actualizado tras la instalación documental

| Componente | Estado |
| --- | --- |
| Facturación | Habilitada. Los recursos activos generan cargos. |
| VM | `quetzalmart-odoo`, Ubuntu 22.04, zona `us-central1-a`, `e2-standard-2`, disco equilibrado de 50 GB. |
| Dirección pública | `136.116.120.10`, reservada como `quetzalmart-odoo-ip`. |
| Cloud SQL | `quetzalmart-postgres`, PostgreSQL 16, `db-f1-micro`, IP privada `172.18.0.3`, sin IP pública. Base `quetzalmart_db` y usuario `odoo`. Respaldos automáticos habilitados. |
| Odoo | Community `18.0-20261017`, instalado como paquete y servicio `systemd`; servicio activo y habilitado. Base inicializada. |
| Módulos | `sale_management`, `purchase`, `account`, `hr` y `dms` (OCA) instalados. `crm`, `website` y `website_sale` aún sin instalar. |
| Cuentas | `admin` más cuentas personales para los integrantes 1 y 3. Ambas contraseñas iniciales se guardaron por separado en Secret Manager y se verificó el inicio de sesión. |
| Red | Nginx recibe 80/443 públicos; Odoo escucha solo en `127.0.0.1:8069` y `127.0.0.1:8072`; SSH 22 limitado a IAP. |
| HTTPS | Certificado público de Let's Encrypt para la IP, válido hasta el 24 de octubre de 2026. Certbot 5.8.0 tiene temporizador de renovación y un gancho que comprueba y recarga Nginx. La simulación de renovación pasó. |
| Adjuntos | Filestore en `/var/lib/odoo/.local/share/Odoo/filestore/quetzalmart_db`, dentro del disco de la VM. Instantánea inicial `quetzalmart-odoo-initial-20261017` lista; política diaria `quetzalmart-odoo-daily` con retención de siete días. |

La petición externa `HEAD /web/login` devolvió HTTP 200 con verificación TLS normal. `odoo shell` cargó los 71 módulos de la base y conectó como `odoo@172.18.0.3:5432`. El certificado para IP usa el perfil de corta duración de [Let's Encrypt](https://letsencrypt.org/2026/03/11/shorter-certs-certbot). Se validó la emisión de prueba y la de producción. Los archivos de Nginx y el gancho de renovación están en [`../infra`](../infra/).

## Trabajo realizado en esta sesión

1. Se reutilizaron la VM, Cloud SQL, la base, el usuario y las reglas de red que ya existían. No se crearon una segunda VM ni otra base.
2. Se comprobó por SSH que Odoo estaba instalado y que Nginx lo atendía localmente. Se guardó una copia de la configuración anterior de Nginx en `/etc/nginx/sites-available/odoo.before-ip-cert-20261017`.
3. Se configuró `/.well-known/acme-challenge/`, se probó su acceso público y se emitió un certificado de Let's Encrypt para la IP. Nginx usa ahora ese certificado.
4. Se instaló Certbot 5.8.0 y el gancho de recarga de Nginx. `certbot renew --dry-run` y la ejecución del gancho terminaron correctamente.
5. Se programaron instantáneas diarias del disco y se creó una instantánea inicial. Cloud SQL ya tenía sus respaldos habilitados.
6. Se crearon los usuarios de los integrantes 1 y 3. El primero tiene permisos de Ventas, Compras y Facturación; el tercero, de Empleados. No se enviaron invitaciones por correo. Sus contraseñas iniciales se generaron de forma aleatoria, se guardaron en Secret Manager y se comprobaron mediante la API de Odoo.
7. Se instaló [OCA/dms](gestion_documental.md), se cargaron 15 PDF ficticios y se verificaron categorías, etiquetas, descarga y permisos con las cuentas existentes. Los PDF originales se conservaron en el repositorio para el manual.
8. Se completó [Empleados](empleados.md): 35 empleados con cargo y departamento coherentes, 5 departamentos del proyecto y 7 cargos. Se creó el respaldo de Cloud SQL `1792287063606` antes de la carga y se comprobó que repetirla no genera duplicados.

## Pendiente para que trabaje todo el equipo

1. Cada integrante debe recuperar su contraseña inicial de Secret Manager, entrar a Odoo y cambiarla. También se comprobó que la contraseña de `admin` almacenada en Secret Manager permite iniciar sesión.
2. Crear la cuenta del integrante 2 cuando se conozca su correo o usuario. Para UiPath, crear después una cuenta de integración separada con acceso limitado a clientes y productos.
3. El responsable del portal debe instalar y configurar `crm`, `website` y `website_sale`. El módulo `documents` de Odoo Enterprise no está disponible en Community; la gestión documental ya se resolvió con [OCA/dms](gestion_documental.md).
4. Crear un usuario PostgreSQL de solo lectura y comprobar las consultas SQL de demostración. No publicar el puerto 5432. Realizar una restauración de prueba de Cloud SQL y del filestore antes de la entrega.
5. Completar datos de ventas, compras, empleados y documentos según [plan_de_trabajo.md](plan_de_trabajo.md), y documentar capturas para los manuales.

## Costos y operación

La VM y Cloud SQL activos cuestan aproximadamente **USD 56 al mes** encendidos todo el mes en `us-central1`, antes de discos, instantáneas, tráfico y otros cargos: [precio de `e2-standard-2`](https://cloud.google.com/products/compute/pricing/general-purpose) y [precio de `db-f1-micro`](https://cloud.google.com/sql/pricing). `db-f1-micro` [no tiene SLA de Cloud SQL](https://docs.cloud.google.com/sql/docs/postgres/instance-settings). Supervisar rendimiento y facturación durante la carga del proyecto.

La renovación del certificado depende de que la IP reservada siga apuntando a la VM y de que el puerto 80 sirva `/.well-known/acme-challenge/`. Comprobar periódicamente `sudo /snap/bin/certbot certificates` y `systemctl status snap.certbot.renew.timer`.
