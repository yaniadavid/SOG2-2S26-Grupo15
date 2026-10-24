# Robot de Excel a Odoo para UiPath Studio 2021.10

El proyecto **Windows - Legacy** contiene dos actividades **Invoke Code** en `Main.xaml`:

1. `ProcesarExcel.vb` recorre una carpeta y sus subcarpetas, abre `.xlsx`, `.xls` y `.xlsm` en modo de lectura, busca hojas `clientes` y `productos`, valida filas y deja `validacion_*.csv`, `resumen_*.json` y `lote_*.json` en `Reportes/`.
2. `CargarOdoo.vb` consulta y escribe mediante JSON-RPC de Odoo **solo cuando** `RPA_MODO=CARGAR`. Busca por todas las claves disponibles antes de crear, actualiza registros existentes, resuelve relaciones de contactos, crea etiquetas faltantes, carga productos, ajusta inventario en `WH/Stock` y aplica el valor de publicación web. Deja `carga_*.csv` con IDs y resultado por fila. Una segunda ejecución debe producir cero altas nuevas.

El código fuente de cada actividad queda también como `.vb` legible. Si lo cambias, ejecuta `python generar_xaml.py` para regenerar `Main.xaml`. No edites una copia sin actualizar la otra.

## Modo de validación

Es el modo predeterminado. Abre [project.json](project.json) en UiPath Studio y ejecuta `Main.xaml`. Si `RPA_ENTRADA` no está definida, toma `Proyecto/datos_prueba/rpa`. El libro incluido produce **3 clientes válidos, 3 rechazados; 3 productos válidos, 4 rechazados**. `clientes` aparece en posición 5 y `productos` en 6; la anomalía se registra.

Para otra carpeta, define `RPA_ENTRADA` con una ruta absoluta **antes de abrir Studio**. En PowerShell, por ejemplo:

```powershell
$env:RPA_ENTRADA = 'C:\RPA\Entrada'
& 'C:\Program Files\UiPath\Studio\UiPath.Studio.exe'
```

Los reportes permanecen en `Reportes/` para que puedas revisarlos y documentar la ejecución. Se excluyen de Git porque los Excel reales pueden contener datos personales.

## Modo de carga

1. Crea en Odoo una cuenta interna de integración con permisos para Contactos, Productos, Inventario y publicación web. Los campos propios `x_rpa_external_id` y `x_rpa_product_values` ya se añadieron a `product.template` en la base compartida; el primero conserva el `ID Externo` separado de `Internal Reference`, y el segundo conserva literalmente `Product Values`.
2. En **Preferencias → Seguridad de la cuenta**, genera una clave de API para la cuenta. No la pegues en el repositorio ni en el chat.
3. Ejecuta `GuardarCredencial.ps1` en PowerShell. Solicita usuario y clave sin mostrarlos y guarda la clave cifrada con DPAPI en `%LOCALAPPDATA%\QuetzalMartRPA\credencial.dat`. Solo el mismo usuario de Windows puede descifrarla.
4. Copia el [Excel de carga controlada](../../datos_prueba/rpa_carga_controlada/Prueba_Controlada_RPA.xlsx) a una carpeta de entrada independiente. Contiene un cliente y un producto ficticios con claves `RPA-PRUEBA-...`. Activa el modo de carga y abre Studio desde la misma consola:

   ```powershell
   $env:RPA_ENTRADA = 'C:\RPA\Entrada'
   $env:RPA_MODO = 'CARGAR'
   & 'C:\Program Files\UiPath\Studio\UiPath.Studio.exe'
   ```

5. Ejecuta el flujo, revisa `carga_*.csv` y verifica los IDs en Odoo. Repite la ejecución: no debe aparecer `CREADO`. Si una fila da `ERROR`, corrige la causa y vuelve a ejecutar; el robot vuelve a buscar antes de intentar crear.

Se puede cambiar la URL y base mediante `RPA_ODOO_URL` y `RPA_ODOO_DB`. El valor predeterminado es `https://136.116.120.10` y `quetzalmart_db`. La verificación TLS permanece activa. `RPA_PRUEBA_LOCAL=1` solo permite HTTP hacia `127.0.0.1` para el simulador incluido en `tests/`.

## Mapeo y límites conocidos

- **Clientes:** `Reference → ref`, `Tax ID → vat`, correo, dirección, web, notas, tipo de compañía, país, estado, empresa relacionada y etiquetas. Un país o estado desconocido detiene esa fila; una etiqueta nueva se crea.
- **Productos:** `ID Externo → x_rpa_external_id`, `Internal Reference → default_code`, código de barras, precios, costo, peso, descripción, tipo, cantidad y publicación. `Product Values` se conserva como texto original en `x_rpa_product_values`; el enunciado no define su formato, así que no se crean variantes a partir de él.
- **Inventario:** la cantidad se trata como conteo en `WH/Stock`, mediante `stock.quant.inventory_quantity` y `action_apply_inventory`. Si hay varios quants para un producto en esa ubicación, la fila se detiene para revisar lotes o propietarios.
- **Publicación:** se escribe `is_published` y se comprueba por API. La visibilidad final en el portal y la consulta PostgreSQL deben mostrarse durante la demostración.

## Verificación realizada

Se compiló y ejecutó el código VB.NET fuera de Studio con el libro de prueba. Un simulador JSON-RPC local recibió las seis filas válidas: primera ejecución **6 creados**, segunda ejecución **6 omitidos**. El libro de carga controlada produjo **2 creados**, luego **2 omitidos**; al cambiar el precio en un lote simulado, produjo **1 actualizado**. El analizador de Studio pudo leer el XAML. La ejecución dentro de UiPath y la carga contra Odoo real siguen pendientes: Studio no carga proyectos en esta instalación y la cuenta de integración todavía no está disponible. El proyecto vacío original `Proyecto/uipath/Gerenciales` se conservó.
