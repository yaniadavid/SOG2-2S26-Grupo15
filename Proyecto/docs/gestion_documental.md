# Gestión documental de QuetzalMart

## Estado y acceso

El módulo comunitario [OCA/dms](https://github.com/OCA/dms) está instalado en Odoo Community 18 de GCP. Abre [Odoo](https://136.116.120.10/web/login), inicia sesión con tu cuenta y entra a **Documentos**. Si la sesión estaba abierta antes de asignar permisos, cierra sesión y vuelve a entrar. El módulo está fijado a la rama 18.0, revisión `779f8768d3328a3ae58ff74fc9300f120be2d0ee`, versión `18.0.1.2.3`, en `/opt/odoo/custom-addons/dms`. La configuración de Odoo añade `/opt/odoo/custom-addons` a `addons_path`.

Se eligió el almacenamiento `Filestore` de Odoo para los archivos. Los PDF quedan asociados a los registros `dms.file` en PostgreSQL y sus bytes en el filestore de la VM. Para restaurarlos hace falta **la base de datos y el filestore**. La copia local visible para preparar el manual está en [`../../output/pdf/gestion_documental`](../../output/pdf/gestion_documental); `manifest.json` relaciona cada referencia con su categoría. Estos son documentos ficticios sin validez fiscal o legal. Las cinco facturas de esta carpeta sirven para la gestión documental; no sustituyen las 50 facturas PDF del bloque del Integrante 1.

## Organización

| Categoría y directorio raíz | Referencias | Etiquetas | Archivos |
| --- | --- | --- | ---: |
| Facturas de proveedores | `QM-FP-2026-001` a `005` | Factura, Proveedor, Muestra | 5 |
| Contratos de outsourcing | `QM-CO-2026-001` a `005` | Contrato, Outsourcing, Muestra | 5 |
| Contratos de empleados | `QM-CE-2026-001` a `005` | Contrato, Empleado, Confidencial, Muestra | 5 |

Cada directorio tiene una categoría con el mismo nombre. Los nombres de archivo conservan la referencia y la extensión `.pdf`. La búsqueda por referencia, directorio o etiqueta permite identificar cada grupo.

## Usuarios y permisos

| Cuenta | Acceso |
| --- | --- |
| `yania.david@gmail.com` (Integrante 3) | Gestión de los tres directorios y los 15 archivos. Tiene rol de responsable del módulo. |
| `javiermonjes007@gmail.com` (Integrante 1) | Lectura y descarga de las cinco facturas y los cinco contratos de outsourcing. No puede leer contratos de empleados ni editar archivos. |
| `admin` | Administración de los tres directorios. |
| `dojuparupe1975@gmail.com` (Integrante 2) | Cuenta interna activa. No se le han asignado grupos de gestión documental; sus permisos funcionales se configurarán con CRM y tienda. |

La separación se configura con grupos de acceso propios de DMS. Los tres directorios son raíces independientes: el de empleados solo incluye el grupo de gestión; los otros dos incluyen también el grupo de lectura comercial. No se crearon enlaces públicos para los contratos. Si se incorporan documentos reales, revisa el acceso antes de subirlos y evita compartir enlaces por token sin necesidad.

## Cómo revisar y documentar

1. En **Documentos**, abre cada directorio y comprueba que haya cinco PDF. También puedes filtrar por categoría o buscar `QM-FP`, `QM-CO` y `QM-CE`.
2. Abre un PDF de cada categoría. Comprueba en la ficha su categoría y sus etiquetas; descarga uno y verifica que abra correctamente.
3. Con la cuenta del Integrante 1, comprueba que aparezcan facturas y contratos de outsourcing, que no aparezcan contratos de empleados y que los archivos sean de solo lectura. La cuenta del Integrante 3 ve los 15.
4. Para el Manual 1, captura el menú **Documentos**, las tres categorías, una búsqueda que devuelva cinco resultados, una ficha con etiquetas y una descarga. Oculta credenciales y evita capturar información personal si después reemplazas los ejemplos.
5. Explica en el manual qué es el almacenamiento, cómo se organizan categorías y etiquetas, quién puede consultar cada directorio y cómo se busca y descarga un archivo.

## Comprobaciones ejecutadas

Primero se instaló y probó el módulo en la base aislada `quetzalmart_dms_test`. Se verificó que la cuenta de gestión veía 15 archivos; la comercial, 10; la comercial no podía leer un contrato de empleado ni escribir sobre una factura, y podía descargar una factura. La versión utilizada incluye comprobaciones de permiso en el método de escritura de DMS; la prueba se hizo porque existía un [reporte previo sobre permisos en Odoo 18](https://github.com/OCA/dms/issues/434).

Antes de instalar en la base principal se creó el respaldo manual de Cloud SQL `1792286130527` (estado `SUCCESSFUL`) y una copia de `/etc/odoo/odoo.conf`. Luego se repitieron los conteos y las pruebas de permisos en `quetzalmart_db`. Por la API externa de Odoo y HTTPS se autenticaron las tres cuentas existentes: `admin` e Integrante 3 vieron 15 PDF, Integrante 1 vio 10, y cada cuenta descargó un PDF de muestra. `GET /web/login` respondió HTTP 200 con TLS válido. Al terminar, se eliminó la base aislada de prueba y su filestore; la base principal y la copia local de los PDF permanecen disponibles.

Archivos para repetir la configuración y la comprobación: [`../infra/configure_dms.py`](../infra/configure_dms.py), [`../infra/verify_dms_xmlrpc.py`](../infra/verify_dms_xmlrpc.py) y [`../scripts/generar_documentos_muestra.py`](../scripts/generar_documentos_muestra.py). El primero se ejecuta mediante `odoo shell` con `env` de Odoo y requiere los PDF y `manifest.json` en `/tmp/quetzalmart-dms-docs` en la VM. Es idempotente: no vuelve a cargar un archivo con igual nombre y directorio si su contenido coincide. No se almacenan contraseñas en el repositorio.
