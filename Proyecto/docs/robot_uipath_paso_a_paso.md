# Robot de Excel a Odoo con UiPath: paso a paso

**Responsable:** Integrante 3. **Estado:** el [proyecto de UiPath](../uipath/RobotExcelValidacion/README.md) ya contiene validación y carga por JSON-RPC; pasó pruebas locales con un Odoo simulado. Falta ejecutarlo en Studio y probar una escritura controlada en Odoo real. Sigue las reglas de [interpretación de Excel](diseno_rpa_excel.md) y usa el [libro de prueba](../datos_prueba/rpa/README.md). Odoo Community 18 está en `https://136.116.120.10`; la base se llama `quetzalmart_db`. El 23 de octubre de 2026 se comprobó que `/jsonrpc` responde con la versión `18.0-20261017`. Una revisión de solo lectura confirmó CRM, sitio, tienda e inventario instalados, el almacén `WH/Stock` y los campos principales de contactos y productos. No encontró una cuenta interna específica para el robot.

`Main.xaml` contiene dos actividades **Invoke Code** con código VB.NET en `ProcesarExcel.vb` y `CargarOdoo.vb`. El modo predeterminado `VALIDAR` no modifica Odoo; `RPA_MODO=CARGAR` activa la carga con una credencial cifrada localmente. El primer paso produjo los conteos esperados y el segundo, contra un simulador JSON-RPC, creó seis registros y omitió los mismos seis en la segunda ejecución. Los campos `x_rpa_external_id` y `x_rpa_product_values` ya se agregaron a Odoo para conservar ambos valores del Excel. La cuenta de integración y la prueba real siguen pendientes. El proyecto vacío `Proyecto/uipath/Gerenciales` se conservó sin cambios.

## 0. Preparar los accesos

1. En este equipo ya están instalados **UiPath Studio 2021.10.10** y Microsoft Excel. Abre el proyecto [RobotExcelValidacion](../uipath/RobotExcelValidacion/project.json), de tipo **Process**, compatibilidad **Windows - Legacy** y lenguaje VB. El flujo actual usa **Invoke Code** con Excel Interop y solicitudes HTTPS de .NET; sus dependencias instaladas son `UiPath.Excel.Activities` y `UiPath.System.Activities`. Si después quieres separar el código en actividades visuales, usa **Excel Application Scope** + **Get Workbook Sheets** + **Read Range** y una versión compatible de **HTTP Request (legacy)** + **Deserialize JSON**. `Get Sheets Workbook` apareció en un paquete de Excel de 2026; no lo incluyas en Studio 2021 sin comprobar compatibilidad. [Compatibilidad de Studio 2021.10](https://docs.uipath.com/studio/standalone/2021.10/user-guide/about-automation-projects), [Get Workbook Sheets](https://docs.uipath.com/activities/other/latest/productivity/excel-get-workbook-sheets), [HTTP Request legacy](https://docs.uipath.com/activities/other/latest/developer/http-client).
2. Pide al Integrante 1 una **cuenta de integración de Odoo**, distinta de tu cuenta personal, con permisos de lectura y escritura sobre contactos y productos. La revisión del 23 de octubre confirmó que todavía no existe. Acuerden aparte los permisos de inventario y publicación web. El almacén `WH/Stock` ya existe; confirma con el responsable que allí quedarán los productos importados.
3. Genera una **clave de API** para esa cuenta en Odoo o recibe una credencial por un canal privado. Guarda usuario y clave en **Windows Credential Manager** o como activo de credenciales de Orchestrator. No los escribas en archivos XAML, Excel o JSON, capturas ni Git. Usa **Get Username and Password** o **Get Secure Credential** para recuperarlos durante la ejecución. Para serializar la petición JSON tendrás que convertir el `SecureString` a `String` **solo en memoria y justo antes de llamar a Odoo**; marca las actividades como privadas y no registres esa variable. Odoo admite usar una clave de API en lugar de la contraseña para las llamadas externas. [Claves de API de Odoo 18](https://www.odoo.com/documentation/18.0/developer/reference/external_api.html#api-keys), [credenciales de UiPath](https://docs.uipath.com/activities/other/latest/workflow/get-username-password-x).
4. Crea en tu equipo una carpeta de entrada fuera del repositorio, por ejemplo `C:\RPA\Entrada`, y otra para reportes, `C:\RPA\Reportes`. Copia el Excel de prueba a la carpeta de entrada. Al principio ejecuta el robot en **modo solo lectura**, sin crear datos en Odoo.

## 1. Organizar el proyecto de UiPath

Crea estas secuencias o workflows; cada una debe recibir argumentos explícitos y devolver un resultado:

| Workflow | Entrada | Salida |
| --- | --- | --- |
| `Main.xaml` | Carpeta raíz, modo `SoloValidar` | Resumen final |
| `LeerLibro.xaml` | Ruta del Excel | Hojas objetivo y posición |
| `ValidarClientes.xaml` | Tabla de la hoja y número de encabezado | Clientes preparados y errores |
| `ValidarProductos.xaml` | Tabla de la hoja y número de encabezado | Productos preparados y errores |
| `LlamarOdoo.xaml` | Servicio, método, argumentos | Resultado o error de Odoo |
| `CargarCliente.xaml` / `CargarProducto.xaml` | Registro preparado | Creado, actualizado, omitido o rechazado |
| `GuardarReporte.xaml` | Eventos y contadores | CSV/JSON en `Reportes` |

En el proyecto actual, `RPA_ENTRADA` indica la carpeta raíz y `RPA_MODO` controla `VALIDAR` (predeterminado) o `CARGAR`. Usa una lista de eventos que conserve **ruta, libro, hoja, posición, fila, tipo, clave, acción y motivo**. Nunca escribas la clave de API en ese registro.

## 2. Encontrar los libros sin depender de nombres

1. Solicita la carpeta raíz al usuario o pásala como argumento. Comprueba que exista.
2. Enumera archivos recursivamente. Una expresión VB posible en una actividad **Assign** es:

   ```vb
   archivos = System.IO.Directory.EnumerateFiles(CarpetaRaiz, "*.*", System.IO.SearchOption.AllDirectories).
       Where(Function(ruta) {".xlsx", ".xls", ".xlsm"}.Contains(System.IO.Path.GetExtension(ruta).ToLowerInvariant()) AndAlso
                            Not System.IO.Path.GetFileName(ruta).StartsWith("~$", StringComparison.OrdinalIgnoreCase)).ToArray()
   ```

3. Itera `archivos` con **For Each**. Encierra el procesamiento de **cada libro** en **Try Catch**. Si uno está dañado, protegido o no es compatible, registra el error y continúa con el siguiente. No uses el nombre de carpeta o archivo para decidir qué hojas importar.
4. En `LeerLibro.xaml`, abre cada archivo con **Excel Application Scope** en modo de lectura y sin guardar cambios. Dentro, usa **Get Workbook Sheets** y guarda la lista de hojas en su orden real. Registra `posición = índice + 1`. Una hoja es objetivo cuando su nombre normalizado equivale a `clientes` o `productos`; `posición = 5` solo es una comprobación. Si está en otra posición, **se procesa y se informa la anomalía**. Si no hay hojas objetivo, informa `sin_hojas_objetivo`.

Normaliza **solo para comparar**: quita espacios exteriores, reduce espacios repetidos, pasa a minúsculas y elimina acentos. Conserva el texto original de las celdas para el reporte y el mapeo. No importes `proveedor`, `reclamos` ni `registros`.

## 3. Leer cada hoja y localizar encabezados

1. Para cada hoja objetivo usa **Read Range** dentro del mismo **Excel Application Scope**, con el nombre real de la hoja, rango desde `A1` y **AddHeaders desactivado**. La actividad devuelve un `DataTable`. Comprueba con el libro de prueba que la primera fila de la tabla corresponda a la fila 1 de Excel antes de calcular los números de fila del reporte. [Read Range de Excel](https://docs.uipath.com/activities/other/latest/productivity/excel-read-range).
2. Inspecciona las primeras diez filas no vacías. Compara sus celdas normalizadas con las columnas del [diseño](diseno_rpa_excel.md#campos-esperados). Selecciona como encabezado la **única** fila que contenga al menos los campos obligatorios: `Name` y un identificador confiable para clientes; `Name` y `ID Externo`, `Internal Reference` o `Barcode` para productos. Si no existe o hay dos candidatas, rechaza la hoja con el motivo preciso. La posición del encabezado es una regla provisional: cámbiala al recibir el Excel real del auxiliar.
3. Crea un diccionario `encabezadoNormalizado -> índice de columna`. Si un encabezado aparece dos veces tras normalizarlo, rechaza la hoja. Recorre las filas posteriores. El número de fila de Excel es `índice del DataRow + 1` cuando la lectura comenzó en `A1`.
4. Omite filas totalmente vacías. Para cada fila restante, guarda primero sus valores y procedencia; después valida. Un error de una fila no detiene las otras.

## 4. Validar antes de cargar

**Clientes:** exige `Name` y una clave de identidad. Prefiere `Reference`; si falta, `Tax ID`; finalmente `Email` solo cuando sea único. Valida formato de correo si viene informado. No uses `Name` como clave. Convierte `Company Type` únicamente cuando el valor corresponda a una opción conocida de Odoo. Resuelve `Related Company`, `Country`, `State` y `Tags` mediante consultas al catálogo; si una relación no existe o es ambigua, registra error. No crees países, estados o etiquetas sin acuerdo del equipo.

**Productos:** exige `Name` y una clave confiable. Prioriza `ID Externo`; si falta, `Internal Reference` o `Barcode` cuando sea único. Comprueba que `Sales Price`, `Cost`, `Weight` y `Cantidad a la mano` sean números no negativos. Acepta para `Está publicado` únicamente `sí/no`, `true/false` y `1/0`, ignorando mayúsculas y acentos. Rechaza otros valores. El mapeo de `Product Type` debe confirmarse contra `fields_get` de la instancia; no asumas el código interno a partir del texto visible.

En ambos tipos detecta **claves repetidas dentro del mismo lote** antes de llamar a Odoo. Si dos filas tienen la misma clave pero valores distintos, envíalas a revisión; no dejes que el orden de los archivos decida cuál gana. Conserva `Product Values` original en el reporte. **No crees variantes** hasta recibir un ejemplo real y acordar su formato.

## 5. Conectar UiPath con Odoo por JSON-RPC

El endpoint `https://136.116.120.10/jsonrpc` respondió a una consulta de versión. En **HTTP Request (legacy)** selecciona `POST`, `BodyFormat = "application/json"`, coloca el JSON en `Body` y habilita **Enable SSL certificate verification**. Usa `ContinueOnError = False` para que **Try Catch** registre los fallos. Guarda `Response content` en una variable y no uses **Preview** con una petición que contenga la clave de API. No registres el contenido de las solicitudes. Odoo documenta JSON-RPC como interfaz de servicios. [Servicio JSON-RPC de Odoo 18](https://www.odoo.com/documentation/18.0/developer/howtos/web_services.html), [HTTP Request legacy de UiPath](https://docs.uipath.com/activities/other/latest/developer/http-client).

Construye el cuerpo desde un objeto y serialízalo: si tu paquete incluye **Serialize JSON**, úsalo; en versiones anteriores puedes usar `Newtonsoft.Json.JsonConvert.SerializeObject(objeto)` en **Assign**. Así los nombres, acentos y comillas de las celdas se escapan correctamente. Usa **Deserialize JSON** en `Response content`. Comprueba `error` **aunque HTTP devuelva 200**; si aparece, registra su mensaje sin guardar la clave. Cada llamada debe tener un `id` distinto para correlacionarla.

Primera llamada, autenticación (`LOGIN` y `CLAVE_API` son marcadores, nunca valores en el archivo):

```json
{
  "jsonrpc": "2.0",
  "method": "call",
  "params": {
    "service": "common",
    "method": "authenticate",
    "args": ["quetzalmart_db", "LOGIN", "CLAVE_API", {}]
  },
  "id": 1
}
```

La respuesta `result` debe ser un entero positivo (`uid`). Si es `false` o hay `error`, detén el lote antes de modificar registros. Para consultar y modificar modelos usa `service = "object"`, `method = "execute_kw"` y argumentos `[base, uid, clave, modelo, operación, parámetros_posicionales, opciones]`. Odoo documenta las operaciones `search_read`, `create` y `write` mediante `execute_kw`. [API externa de Odoo 18](https://www.odoo.com/documentation/18.0/developer/reference/external_api.html).

Ejemplo de búsqueda de un cliente por `Reference` (sustituye los marcadores con variables serializadas, no por concatenación de texto):

```json
{
  "jsonrpc": "2.0",
  "method": "call",
  "params": {
    "service": "object",
    "method": "execute_kw",
    "args": [
      "quetzalmart_db", 123, "CLAVE_API", "res.partner", "search_read",
      [[ ["ref", "=", "RPA-C-001"] ]],
      {"fields": ["id", "name", "ref"], "limit": 2}
    ]
  },
  "id": 2
}
```

Si devuelve **cero** registros, crea; si devuelve **uno**, compara y actualiza solo los campos que cambien; si devuelve **dos**, rechaza por ambigüedad. Para `create`, los parámetros posicionales son `[ {campos: valores} ]`; para `write`, `[[id], {campos: valores}]`. Tras crear o actualizar, vuelve a leer por ID y verifica los campos principales. Antes de escribir, consulta `fields_get` para comprobar el nombre, tipo y opciones de los campos instalados. Nunca envíes campos vacíos como `false` para borrar datos existentes sin una regla explícita.

## 6. Mapear campos y completar procesos especiales

| Excel | Modelo/campo inicial de Odoo | Regla |
| --- | --- | --- |
| Cliente `Name`, `Reference`, `Email`, `Phone`, `Tax ID` | `res.partner`: `name`, `ref`, `email`, `phone`, `vat` | Busca por la clave elegida antes de crear. |
| Cliente `Street`, `Street2`, `City`, `Zip`, `Website`, `Notes` | `res.partner`: `street`, `street2`, `city`, `zip`, `website`, `comment` | Escribe solo valores validados. |
| Cliente `Country`, `State`, `Related Company`, `Tags` | `country_id`, `state_id`, `parent_id`, `category_id` | Busca IDs primero; comprueba relaciones y permisos. |
| Producto `Name`, `Internal Reference`, `Sales Price`, `Cost`, `Weight`, `Sales Description` | `product.template`: `name`, `default_code`, `list_price`, `standard_price`, `weight`, `description_sale` | Confirma `fields_get` y tipos en la instancia. |
| Producto `ID Externo`, `Barcode`, `Product Type` | Por acordar: identificador externo, `barcode`, tipo de producto | No fuerces `ID Externo` a `default_code` si ambas columnas tienen valores distintos. Define con el Integrante 1 si se usará `ir.model.data` o un campo propio. |
| Producto `Cantidad a la mano` | Ajuste de inventario en almacén | No escribas una cantidad directamente en `product.template`; implementa el flujo de ajuste y comprueba `stock.quant`. |
| Producto `Está publicado` | Publicación de la tienda | `product.template` tiene `is_published` y `website_published` en esta instancia. Acuerda cuál usar en la API y valida la página del producto después de publicarlo. |
| Producto `Product Values` | Pendiente de muestra real | Conserva el valor original y no inventes variantes. |

El **primer hito de escritura** es un cliente y un producto ficticios, con claves nuevas y valores mínimos. Hazlo en una base de prueba si está disponible; si se usa la base compartida, identifica ambos con prefijo `RPA-PRUEBA-` y acuerda antes con el equipo cómo se conservarán o archivarán. Después incorpora relaciones, inventario y publicación web **una función por vez**. El servicio de Odoo debe aplicar sus reglas; PostgreSQL se usa únicamente para comprobación de lectura.

## 7. Repetir sin duplicar y generar evidencia

1. En `SoloValidar=True`, procesa el libro incluido. El resultado esperado es **3 clientes válidos y 3 rechazados; 3 productos válidos y 4 rechazados**. `clientes` ocupa la quinta hoja y `productos` la sexta: registra ambas posiciones. No se crea nada en Odoo.
2. Con la cuenta de integración lista, procesa un lote **limpio** de un cliente y un producto nuevos. Busca, crea y vuelve a leer ambos. Comprueba el producto en el catálogo y después prueba su ajuste de inventario y publicación.
3. Ejecuta el mismo lote otra vez. Debe producir **cero altas nuevas**; registra actualizados u omitidos según si cambió algún valor. Un fallo de red después de una escritura puede dejar el registro creado: al reintentar, **busca de nuevo** antes de repetir `create`.
4. Agrega libros con `productos` en quinta posición, ambas hojas, una hoja objetivo en otra posición, ninguna hoja objetivo, duplicados y un archivo dañado. Cambia los nombres de carpetas y archivos entre ejecuciones. El libro actual cubre solo parte de estos casos.
5. Guarda un reporte por ejecución con fecha, conteos y detalle por fila. Al menos: `libros_revisados`, `hojas_objetivo`, `posicion_5`, `posicion_distinta`, `creados`, `actualizados`, `omitidos`, `rechazados`, `errores_de_archivo`. En el detalle registra archivo, hoja, fila, clave y motivo. No incluyas credenciales ni datos personales completos en las capturas.
6. Con el rol SQL de solo lectura `sog2_lectura` que ya existe, ejecuta [la consulta de verificación RPA](../sql/validar_rpa.sql) por las referencias `RPA-PRUEBA-...`. Demuestra el mismo producto en el portal junto al Integrante 2. Cloud SQL permanece en red privada: el robot accede solo por HTTPS a Odoo.

## 8. Evidencias para los manuales y criterio de término

Guarda capturas de la carpeta y libros de entrada, las actividades del workflow, la detección de hojas y su posición, filas aceptadas/rechazadas, llamada de prueba a Odoo **sin mostrar el cuerpo con clave**, contacto y producto en Odoo, producto en la tienda, consulta SQL y segunda ejecución sin duplicados. Explica cada captura en tu sección del Manual 1. Usa el mismo recorrido para el diagrama del RPA en el Manual 2.

El robot está listo cuando puede recibir una **carpeta desconocida**, procesar todos sus libros compatibles, importar solo `clientes` y `productos`, continuar después de errores individuales, no duplicar al repetir y mostrar registros nuevos en Odoo, tienda y SQL. Las reglas definitivas de `Product Values`, tipos de producto y ubicación real de encabezados se cerrarán cuando llegue un Excel auténtico del auxiliar.
