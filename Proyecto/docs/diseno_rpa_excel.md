# Interpretación de los Excel y diseño del RPA

**Responsable:** Integrante 3. **Estado:** diseño propuesto; todavía no se han recibido archivos Excel reales del auxiliar. Este documento interpreta el requisito de las páginas 8 y 9 del enunciado y define cómo probarlo.

## Qué significa «quinta posición»

El enunciado habla de muchos libros Excel, con varias hojas, y pide importar únicamente las hojas llamadas `clientes` y `productos`, «las cuales siempre vendrán en la 5 posición». La lectura más consistente es **cada hoja objetivo ocupa la quinta posición en el libro donde aparece**. Dos hojas diferentes no pueden ser a la vez la quinta hoja de un mismo libro. Por eso el robot tratará `clientes` y `productos` como tipos de hoja alternativos: un libro puede contener una, la otra o ambas.

La **identidad de la hoja será su nombre**, no su posición ni el prefijo de carpeta o archivo. La posición 5 será una comprobación: se registrará `posición_correcta = sí/no` en el resumen. Si una hoja objetivo aparece en otra posición, se procesará igualmente y se mostrará la anomalía. Si aparecen ambas en un libro, se procesarán ambas y se registrará que al menos una no puede cumplir la quinta posición. Esta regla conserva los datos y permite explicar la ambigüedad durante la evaluación.

Se normalizarán los nombres de hoja y encabezados al compararlos: espacios externos e interiores repetidos, mayúsculas/minúsculas y acentos. Los **valores** de las celdas se conservarán; la normalización de identificadores se hará por separado. No se importarán hojas `proveedor`, `reclamos` o `registros`, aunque aparezcan en una carpeta o libro cuyo nombre contenga `clientes` o `productos`.

## Lectura de archivos

1. El usuario selecciona la carpeta raíz que entregue el auxiliar. UiPath la recorre de forma recursiva, sin fijar nombres de subcarpetas ni de archivos. Los prefijos antes del guion son pistas para el registro, no filtros de importación.
2. Se detectan archivos de Excel compatibles con las actividades instaladas (`.xlsx`, `.xls`, `.xlsm` si el entorno los permite); se omiten archivos temporales `~$*`. Un archivo dañado, protegido o no compatible se informa y no detiene el lote completo.
3. Para cada libro se obtiene la lista ordenada de hojas. En UiPath se puede usar [Get Workbook Sheets](https://docs.uipath.com/activities/other/latest/productivity/excel-get-workbook-sheets) o [For Each Excel Sheet](https://docs.uipath.com/activities/other/latest/productivity/for-each-sheet-x). Se buscan nombres normalizados iguales a `clientes` o `productos`; el índice 4 en una lista que empieza en 0 equivale a la quinta posición.
4. Cada hoja objetivo se lee como tabla con [Read Range Workbook](https://docs.uipath.com/activities/other/latest/productivity/read-range). La primera versión buscará los encabezados en las primeras filas no vacías; si no puede identificar de forma unívoca el encabezado, rechazará la hoja con una razón visible. No se supondrá que la columna A o la fila 1 siempre contienen los datos.
5. Se comprueban los encabezados y los tipos por fila. Las filas vacías se omiten; las inválidas van al reporte de errores con archivo, hoja, fila y motivo. Una fila inválida no bloquea otras filas válidas.
6. Se consolida cada tipo de dato, se detectan duplicados dentro del lote y se envían los registros válidos a Odoo. El resumen indica libros revisados, hojas relevantes, posiciones, filas creadas, actualizadas, omitidas y rechazadas.

## Campos esperados

| Hoja `clientes` | Hoja `productos` |
| --- | --- |
| Name | ID Externo |
| Company Type | Name |
| Related Company | Product Type |
| Email | Internal Reference |
| Phone | Barcode |
| Street | Sales Price |
| Street2 | Cost |
| City | Weight |
| State | Sales Description |
| Zip | Product Values |
| Country | Cantidad a la mano |
| Tax ID | Está publicado |
| Website |  |
| Tags |  |
| Reference |  |
| Notes |  |

**Reglas mínimas de validación:** `Name` no puede estar vacío; precios, costo, peso y cantidad deben ser números válidos y no negativos; `Está publicado` debe convertirse mediante una lista explícita de valores aceptados (`sí/no`, `true/false`, `1/0`). `Country` y `State` deben resolverse contra los catálogos de Odoo antes de crear contactos. No se sustituirán silenciosamente valores desconocidos por un país, estado, precio o tipo de producto predeterminado.

Para repetir una ejecución sin duplicados, los productos se identifican primero por `ID Externo`; si falta, se evalúan `Internal Reference` o `Barcode` solo cuando sean únicos. Para clientes se evalúan `Reference`, luego `Tax ID` y después `Email` solo si identifica de forma única al contacto. Una fila sin identificador confiable se marca para revisión; el nombre por sí solo no garantiza identidad. Se conserva la procedencia (archivo, hoja y fila) en el reporte.

## Destino y transformación en Odoo

**UiPath se ejecutará en el equipo del Integrante 3 y llamará a Odoo por HTTPS.** La VM y PostgreSQL estarán en GCP. Se usará una cuenta de integración de Odoo con permisos limitados, entregada por el Integrante 1. La [API externa de Odoo 18](https://www.odoo.com/documentation/18.0/developer/reference/external_api.html) permite consultar, crear y actualizar modelos. La alternativa de importación de Odoo también admite [IDs externos para actualizar registros](https://www.odoo.com/documentation/18.0/applications/essentials/export_import_data.html). La elección concreta se probará en la instancia instalada.

| Origen | Destino funcional propuesto | Precaución |
| --- | --- | --- |
| `clientes` | Contactos de Odoo (`res.partner`) | `Related Company` requiere resolver primero la empresa relacionada; `Tags`, país y estado son relaciones, no texto libre. |
| `productos` | Catálogo de Odoo (`product.template` y sus variantes cuando corresponda) | `Product Type`, `Product Values` y el identificador externo requieren mapeo confirmado en la versión y módulos instalados. |
| `Cantidad a la mano` | Inventario del producto y almacén acordado | Se aplica mediante el proceso de [ajuste de inventario](https://www.odoo.com/documentation/18.0/applications/inventory_and_mrp/inventory/warehouses_storage/inventory_management/count_products.html); no se trata como un simple campo editable del producto. |
| `Está publicado` | Visibilidad del producto en la tienda | Se comprueba en el [catálogo web de Odoo](https://www.odoo.com/documentation/18.0/applications/websites/ecommerce/products.html), no solo en la tabla de productos. |

`Product Values` es el campo menos definido del enunciado: podría contener atributos y variantes, pero no se especifica su formato. Se conservará el valor original y se definirá la transformación al recibir un ejemplo real. Odoo trata las [variantes como atributos y valores](https://www.odoo.com/documentation/18.0/applications/sales/sales/products_prices/products/variants.html); no debe inventarse un separador ni perder información.

**No se escribirán directamente tablas internas de Odoo en PostgreSQL.** La carga por Odoo permite respetar sus validaciones y relaciones y hace que el portal y el CRM vean los mismos registros. PostgreSQL se usará para comprobación con consultas de solo lectura. Como Cloud SQL tendrá IP privada, el Integrante 1 debe proporcionar un método de consulta segura para la demostración; el robot solo necesita el HTTPS público de Odoo. [Google Cloud documenta la conexión por IP privada desde Compute Engine](https://docs.cloud.google.com/sql/docs/postgres/connect-compute-engine).

## Dependencias entre integrantes

- **Integrante 1:** instancia Odoo estable, credencial de integración, módulos Contactos/Productos/Inventario/Empleados instalados, almacén objetivo y consulta SQL de comprobación.
- **Integrante 2:** tienda conectada al mismo catálogo; acordar qué productos importados se publican y cómo se comprueba su visibilidad.
- **Integrante 3:** flujo UiPath, validación y mapeo, gestor documental, módulo Empleados, evidencias del RPA y Manual 2.

## Pruebas necesarias antes de la evaluación

| Caso | Resultado esperado |
| --- | --- |
| Carpeta anidada y nombres con guiones variables | Se encuentran todos los Excel sin usar rutas fijas. |
| Hoja `clientes` o `productos` en posición 5 | Se procesa y se marca como conforme. |
| Hoja objetivo en otra posición | Se procesa y se registra la anomalía. |
| Ambas hojas en un libro | Se procesan ambas y se explica la contradicción de posición. |
| Libro sin hojas objetivo | Se omite, con motivo en el resumen. |
| Encabezado ausente o ambiguo, fila inválida, archivo dañado | Se reporta el error sin detener el lote. |
| Mismo lote ejecutado dos veces | La segunda ejecución actualiza o ignora registros; no duplica. |
| Producto publicado con cantidad disponible | Aparece en Odoo, en el portal y en SQL. |

La validación final debe hacerse con **archivos nuevos**, similares a los que entregará el auxiliar, y mostrar en pantalla el flujo de UiPath, el resumen, los registros en Odoo y la consulta SQL. Hasta recibir un Excel de muestra, quedan pendientes la ubicación exacta del encabezado, los formatos de `Product Values`, `Company Type` y `Product Type`, y el catálogo de países/estados que traigan los datos.
