# Paso a paso del Integrante 3

Tu bloque abarca **Empleados**, **gestión documental**, **RPA con UiPath**, las capturas correspondientes del **Manual 1** y el **Manual 2 completo**. El [plan general](plan_de_trabajo.md) contiene los requisitos del equipo; el [diseño del RPA](diseno_rpa_excel.md) contiene las reglas de lectura y validación de Excel. Trabajarás sobre la misma instancia de Odoo Community y PostgreSQL en GCP que usarán los otros integrantes.

## A. Trabajo que puedes iniciar sin esperar a GCP

### 1. Acordar la interfaz con los otros integrantes

Odoo Community `18.0-20261017` ya está disponible en [https://136.116.120.10/web/login](https://136.116.120.10/web/login), y tu cuenta personal con permisos de Empleados y gestión documental ya existe. Recupera la contraseña inicial del secreto `quetzalmart-integrante3-initial-password` de GCP Secret Manager y cámbiala al entrar. Con el **Integrante 1**, acuerda el almacén en el que quedará el inventario importado, una cuenta de integración de permisos mínimos para UiPath y un método de consulta SQL de solo lectura. El gestor documental ya está instalado; avisa al equipo de sus categorías y permisos antes de incorporar documentos propios. El estado técnico está en [despliegue_odoo_gcp.md](despliegue_odoo_gcp.md).

Acuerda con el **Integrante 2** que el portal use el catálogo de la misma instancia de Odoo, cómo se publican los productos importados y qué pantalla demostrará que un producto nuevo está disponible. Registra el acuerdo en el plan antes de programar la carga.

**Terminado cuando:** conoces URL de prueba, versión, modelos disponibles, almacén y responsables de acceso y despliegue. No guardes credenciales en Git.

### 2. Preparar UiPath y los archivos de prueba

Instala UiPath Studio en el equipo donde ejecutarás el robot, crea un proyecto Windows y agrega las actividades de Excel y de solicitudes autenticadas que requiera la conexión elegida. Usa las [actividades Workbook](https://docs.uipath.com/activities/other/latest/productivity/workbook-activities) para leer Excel sin depender de automatización visual de la ventana de Microsoft Excel cuando sea posible.

Ya existe un [primer libro de prueba](../datos_prueba/rpa/README.md) con `clientes` en quinta posición, `productos` en sexta, filas válidas y errores intencionales. Úsalo para desarrollar la lectura y validación; todavía faltan libros adicionales con `productos` en quinta posición, hojas objetivo en otra posición y ningún objetivo.

Crea una carpeta de prueba fuera de Git con subcarpetas y Excel de nombres variables. Incluye un libro con `clientes` como quinta hoja, otro con `productos` como quinta, uno con ambas hojas, otro con hoja objetivo en otra posición, duplicados, una fila inválida y un libro sin hojas objetivo. Los encabezados esperados están en el [diseño del RPA](diseno_rpa_excel.md).

**Terminado cuando:** puedes repetir las pruebas sin depender de la estructura exacta de carpetas que entregará el auxiliar.

### 3. Construir primero la lectura, sin cargar datos

Haz que el robot solicite una carpeta raíz y recorra sus Excel recursivamente. Omite archivos temporales `~$*`. Enumera las hojas, detecta `clientes` y `productos` por nombre normalizado y registra si están en la quinta posición. Lee únicamente esas hojas, localiza los encabezados y produce un resumen por archivo y por fila. Si un libro falla, continúa con los demás.

**Terminado cuando:** el resumen distingue libros sin hojas relevantes, filas válidas, filas rechazadas y motivos concretos. Ejecutar la lectura no modifica Odoo.

### 4. Validar y transformar los datos

Para clientes, valida `Name`, correo y referencias; prepara país, estado, tipo de compañía, empresa relacionada y etiquetas. Para productos, valida `ID Externo`, nombre, tipo, referencias, precios, costo, peso, cantidad y el valor booleano de publicación. Usa el identificador externo o referencias únicas para evitar duplicados. Deja `Product Values` pendiente de mapeo definitivo hasta ver un ejemplo real: puede representar variantes y su formato no está descrito.

**Terminado cuando:** cada fila queda como registro preparado o error explicable, y correr dos veces el mismo archivo no genera dos candidatos de alta para la misma entidad.

## B. Trabajo sobre Odoo en GCP

### 5. Empleados cargados y verificados

La aplicación Empleados ya tiene **5 departamentos del proyecto, 7 cargos y 35 empleados con cargo y departamento coincidentes**. Se conservaron los 12 empleados previos con relaciones completas y se añadieron 23 empleados ficticios. Odoo también muestra el empleado automático `Administrator`, sin cargo, que no se cuenta entre los 35 válidos. La [guía de Empleados](empleados.md) registra la organización, los datos fuente, el respaldo, la consulta SQL y los pasos para revisar las fichas en Odoo.

La carga se comprobó en PostgreSQL y con tu cuenta por la API de Odoo. Una segunda ejecución creó cero duplicados. **Pendiente para el Manual 1:** abrir varias fichas en la interfaz y guardar capturas de departamentos, cargos, empleados y conteos SQL. La distribución por sucursal dependerá de que el equipo añada un modelo de sucursal; la instancia actual solo tiene la empresa QuetzalMart y el modelo de empleado no tiene un campo de sucursal.

### 6. Gestión documental instalada

[OCA/dms](https://github.com/OCA/dms) se probó en una base aislada y ya está instalado en la instancia principal. Hay tres categorías con cinco PDF ficticios y etiquetados cada una: facturas de proveedores, contratos de outsourcing y contratos de empleados. Los PDF se conservaron en [`../../output/pdf/gestion_documental`](../../output/pdf/gestion_documental) para que puedas revisarlos y preparar el manual.

La [guía de gestión documental](gestion_documental.md) explica los directorios, la búsqueda, las descargas, los permisos y las capturas recomendadas. Ya se comprobó mediante Odoo y su API que tu cuenta ve los 15 archivos y la del Integrante 1 ve 10 sin poder leer contratos de empleados ni editar archivos. Falta que hagas las capturas de la interfaz para el Manual 1.

### 7. Conectar UiPath con Odoo

Con el Integrante 1, prueba una llamada autenticada de consulta y después crea **un cliente y un producto de prueba** mediante la interfaz admitida por la instancia. Usa el [API externo de Odoo](https://www.odoo.com/documentation/18.0/developer/reference/external_api.html) o su importación con ID externo, según el mecanismo acordado. No escribas directamente en las tablas internas de PostgreSQL.

Después implementa el proceso completo: resolver relaciones de clientes; crear o actualizar contactos; crear o actualizar productos; tratar variantes si el formato de `Product Values` lo permite; ajustar la cantidad en el almacén acordado; publicar los productos marcados para la web. El [ajuste de inventario](https://www.odoo.com/documentation/18.0/applications/inventory_and_mrp/inventory/warehouses_storage/inventory_management/count_products.html) debe seguir el flujo de Odoo.

**Terminado cuando:** los registros aparecen en Odoo, en PostgreSQL mediante consultas de solo lectura y, para un producto publicado, en el portal del Integrante 2.

### 8. Hacer la carga repetible y visible

Procesa las filas de forma que una falla no detenga todo el lote. Registra archivos revisados, hojas detectadas, posición, creados, actualizados, omitidos y rechazados. Vuelve a ejecutar el mismo lote y comprueba que no duplique contactos ni productos. Ejecuta después un segundo lote desconocido para confirmar que no hay rutas o nombres fijos.

Prepara con el Integrante 1 una consulta SQL que encuentre los registros recién importados por su referencia o ID externo. Coordina con el Integrante 2 una búsqueda del producto publicado en el portal. **No expongas Cloud SQL a Internet para facilitar el robot:** UiPath necesita HTTPS hacia Odoo; la comprobación SQL puede hacerse por el acceso seguro que provea el Integrante 1.

**Terminado cuando:** puedes mostrar una ejecución en vivo, su resumen y el mismo dato en Odoo, portal y SQL.

## C. Manuales y demostración

### 9. Guardar evidencias mientras trabajas

Captura: instalación/configuración del gestor documental, sus tres categorías y etiquetas; creación de departamentos y cargos; empleados; diseño y ejecución de UiPath; resumen de importación; contacto y producto cargados; consulta SQL; producto publicado en el portal. Guarda cada captura con un nombre que indique el proceso y redacta una frase sobre qué demuestra. Oculta credenciales y datos sensibles.

**Terminado cuando:** cada requisito de tu bloque tiene una captura o consulta que lo verifica.

### 10. Redactar tu parte del Manual 1

Explica cómo se usa Empleados y el gestor documental. Para UiPath incluye el problema, las actividades y reglas de lectura, el mapeo, las validaciones, las decisiones ante errores y duplicados, la carga a Odoo y las ventajas del RPA. Usa capturas paso a paso de una ejecución real. Entrega tus secciones al responsable de unificar el Manual 1.

**Terminado cuando:** otra persona puede repetir tus pasos con la misma versión de Odoo y UiPath.

### 11. Preparar el Manual 2 completo

Dibuja y explica cinco flujos detallados: **RPA/UiPath**, **compra a proveedor**, **venta de producto**, **recorrido del producto desde recepción hasta venta** y **compra del cliente por web o en tienda física**. En el recorrido del producto incorpora almacenamiento por sector, defectos o mal estado, control de inventario, empaque y control de calidad. Pide a los integrantes 1 y 2 que validen los pasos de sus módulos para que los diagramas reflejen el sistema implementado.

**Terminado cuando:** cada decisión del diagrama tiene salida clara y los cinco flujos coinciden con las pantallas y procesos reales.

### 12. Ensayar tu parte de la calificación

Usa una carpeta de Excel que no hayas procesado antes. Inicia UiPath en pantalla, selecciona la carpeta y muestra la ejecución y el resumen. Enseña el cliente y producto creados, el producto en el portal, la consulta SQL, los empleados y los 15 documentos filtrables. Repite la carga para demostrar que no duplica datos. Ten los diagramas y capturas abiertos para explicar cada paso.

**Terminado cuando:** puedes completar la demostración sin editar archivos, SQL o configuración durante la prueba.

## Tu primer hito

La infraestructura de GCP, Odoo y la gestión documental ya está disponible. Puedes avanzar con Empleados y capturar la evidencia de Documentos; antes de cargar un lote grande del RPA, haz una prueba mínima con **un cliente y un producto**. Esa prueba fijará el mapeo real y la forma de mostrar la evidencia.
