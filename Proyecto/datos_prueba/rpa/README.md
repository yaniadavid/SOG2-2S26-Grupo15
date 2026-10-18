# Libro de prueba para UiPath

[`Prueba_RPA_Clientes_Productos.xlsx`](Prueba_RPA_Clientes_Productos.xlsx) contiene datos ficticios para probar la **lectura y validación** del robot. No lo importes directamente a Odoo: incluye filas inválidas de forma deliberada.

| Hoja | Posición | Uso esperado |
| --- | ---: | --- |
| `LEEME` | 1 | Explica el caso de prueba; no se importa. |
| `proveedor`, `reclamos`, `registros` | 2 a 4 | Se ignoran aunque tengan datos. |
| `clientes` | 5 | Tres filas válidas y tres que deben rechazarse. |
| `productos` | 6 | Tres filas válidas y cuatro que deben rechazarse. Debe registrarse que no está en quinta posición. |

En `clientes`, las filas 5, 6 y 7 prueban nombre vacío, referencia duplicada y correo mal formado. En `productos`, las filas 5 a 8 prueban precio negativo, valor de publicación inválido, ID externo duplicado y nombre vacío. Los valores de `Product Values` se dejaron vacíos porque el formato real aún no se conoce. Los correos `example.invalid`, nombres, direcciones y referencias son de demostración.

El robot debe reconocer las hojas por nombre y registrar su posición. La hoja `productos` se procesa aunque esté en la sexta posición, según el [diseño del RPA](../../docs/diseno_rpa_excel.md). Para cubrir el caso en que `productos` esté en quinta posición se necesitará otro libro de prueba; este archivo demuestra ambos tipos de datos y la anomalía de posición en un solo recorrido.
