# Empleados en Odoo Community

## Estado comprobado

El módulo **Empleados** de QuetzalMart ya cumple los mínimos de este bloque. En la base principal `quetzalmart_db` hay **35 empleados activos con cargo y departamento coincidentes**, **5 departamentos del proyecto** y **7 cargos del proyecto**. La base muestra 36 empleados activos y 6 departamentos activos en total porque Odoo conserva el registro automático `Administrator` en el departamento genérico `Administration`; ese registro no tiene cargo y **no se incluye entre los 35 empleados válidos del proyecto**. No se modificó ni archivó.

Antes de la carga ya existían 12 empleados de QuetzalMart con cargo y departamento, dos departamentos del proyecto y dos cargos. Se agregaron **23 empleados ficticios**, tres departamentos y cinco cargos. Cada empleado nuevo tiene correo no entregable en `example.invalid` y un identificador externo `quetzalmart_hr.employee_###`; no se usan datos de contacto reales. El [CSV conservado en el repositorio](../data/empleados_muestra.csv) enumera los 23 registros y su asignación.

| Departamento | Cargos | Empleados activos válidos |
| --- | --- | ---: |
| Operaciones de Tienda | Cajero de Sucursal; Supervisor de Tienda | 10 |
| Administracion y Compras | Analista de Compras | 9 |
| Logística e Inventario | Auxiliar de Almacén; Coordinador de Logística | 8 |
| Atención al Cliente | Agente de Atención al Cliente | 5 |
| Marketing y Comercio Digital | Especialista de Marketing Digital | 3 |
| **Total** | **7 cargos** | **35** |

La instancia tiene una sola empresa, `QuetzalMart`, y el modelo `hr.employee` no tiene un campo de sucursal. Por eso los empleados se asignaron a departamentos y cargos de esa empresa. Si el equipo añade sucursales más adelante, habrá que definir cómo relacionarlas con los empleados sin confundirlas con los departamentos.

## Cómo revisarlo en Odoo

1. Abre [Odoo](https://136.116.120.10/web/login) con `yania.david@gmail.com` y entra a **Empleados**. Si la sesión es antigua, cierra sesión y vuelve a entrar.
2. En **Configuración > Departamentos**, localiza las cinco áreas de la tabla. El área genérica `Administration` también aparecerá y explica por qué el total de departamentos activos es seis.
3. En **Configuración > Cargos de trabajo**, revisa los siete cargos y abre uno para comprobar su departamento.
4. En **Empleados**, abre por ejemplo `María Celeste Robles`; verifica que el cargo sea `Supervisor de Tienda` y el departamento `Operaciones de Tienda`. Puedes buscar `qm-hr-001@example.invalid` para identificar el registro de muestra.
5. Para el Manual 1, captura la lista de departamentos, la lista de cargos, una ficha de empleado con sus relaciones y el resultado de la consulta SQL. Oculta datos de acceso y contraseñas.

## Verificación técnica y repetición

La carga se hizo mediante el ORM de Odoo, sin escribir directamente en tablas internas de PostgreSQL. Se ejecutó primero con `HR_DRY_RUN=1`, que creó los registros dentro de una transacción y la revirtió. Después del respaldo manual de Cloud SQL `1792287063606` (`SUCCESSFUL`), se ejecutó la carga definitiva. Al repetirla, el resultado fue `created=0` y `already_loaded=23`.

La [consulta SQL de solo lectura](../sql/validar_empleados.sql) devolvió: 36 empleados activos, 35 con cargo y departamento coincidentes, 1 sin cargo (`Administrator`), 5 departamentos del proyecto, 7 cargos y 23 empleados de este lote. Con la cuenta del Integrante 3, la API de Odoo devolvió 36 empleados, 6 departamentos y 7 cargos; también permitió leer una ficha nueva con su cargo y departamento.

El procedimiento reproducible está en [`../infra/load_hr.py`](../infra/load_hr.py). Se ejecuta con `odoo shell` en la VM y lee `/tmp/empleados_muestra.csv`, que es una copia del CSV del repositorio. [`../infra/audit_hr.py`](../infra/audit_hr.py) permite inspeccionar el estado; [`../infra/verify_hr_xmlrpc.py`](../infra/verify_hr_xmlrpc.py) verifica el acceso por HTTPS mientras la contraseña inicial almacenada en Secret Manager siga vigente. Si se cambia la contraseña personal, la validación puede hacerse directamente en la interfaz con la nueva clave.
