# Plan de trabajo - Proyecto QuetzalMart

Este plan ordena el trabajo solicitado en el enunciado del proyecto de SOG2, segundo semestre de 2026. Cada fase termina con una evidencia comprobable. La infraestructura ya está desplegada; su estado verificado el 17 de octubre de 2026 está en [despliegue_odoo_gcp.md](despliegue_odoo_gcp.md).

## Criterio de entrega

La evaluación exige tres manuales PDF, entrega en UEDI, Odoo Community y la base de datos operativos en la nube, consultas SQL preparadas y una demostración funcional. Estos son requisitos para optar a calificación; la rúbrica detallada se publicará después. Este plan no organiza el trabajo por fechas.

## Decisiones del equipo

- **Base de datos:** PostgreSQL. Aunque el enunciado enumera otros motores, [Odoo 18 usa PostgreSQL](https://www.odoo.com/documentation/18.0/administration/on_premise/source.html). Se documentará esta diferencia en los manuales.
- **Alojamiento:** GCP para Odoo Community y PostgreSQL; los tres integrantes accederán a la misma instancia con cuentas individuales y permisos según su función.
- **Distribución:** Integrante 1, infraestructura y núcleo ERP; Integrante 2, portal, CRM, marketing y GA4; Integrante 3, UiPath, gestión documental, Empleados y Manual 2. Las integraciones entre bloques se prueban en conjunto. El [paso a paso del Integrante 3](guia_integrante_3.md) organiza su trabajo.
- **Excel del RPA:** [criterio de interpretación y diseño](diseno_rpa_excel.md). La hoja se selecciona por nombre; la quinta posición se comprueba y registra.

| Responsable | Trabajo principal | Aporte documental |
| --- | --- | --- |
| Integrante 1 | GCP, Odoo Community, PostgreSQL, Ventas, Compras, Facturas y SQL de esos procesos | Manual 1: instalación y capturas de ventas, compras y facturas |
| Integrante 2 | Tienda, CRM, marketing por correo, GA4 y análisis de negocio | Manual 1: capturas de portal, CRM y marketing; Manual 3 completo |
| Integrante 3 | RPA en UiPath, carga de Excel, gestor documental, Empleados y 15 documentos | Manual 1: RPA y Empleados; Manual 2 completo |

Cada integrante documenta el funcionamiento de los módulos a su cargo para integrar la sección 2 del Manual 1. Falta designar quién unificará y revisará ese manual.

## 1. Cerrar decisiones y responsabilidades

- [x] Fijar PostgreSQL, GCP y los tres bloques de responsabilidad.
- [ ] Confirmar versión de Odoo, alcance por sucursal y criterio de conteo de 20 cotizaciones y 60 materiales.
- [x] Adoptar una interpretación operativa de las hojas Excel; documentar en la ejecución cualquier archivo que no cumpla la quinta posición.
- [ ] Designar quién integrará la sección de funcionamiento de módulos del Manual 1 y quién coordinará la prueba integral.
- [ ] Elegir el dominio, remitente institucional y forma de pago de prueba. La [solución documental compatible con Odoo Community](gestion_documental.md) ya se instaló y verificó.

**Salida:** decisiones registradas y responsables asignados. Los puntos pendientes no deben presentarse como decisiones tomadas.

## 2. Verificar y preparar la nube

**Estado actual:** Odoo Community 18 y PostgreSQL 16 funcionan en GCP por HTTPS. Las cuentas individuales de los tres integrantes están activas. Cloud SQL tiene respaldos automáticos y el disco de Odoo tiene instantáneas diarias. Siguen pendientes el usuario SQL de solo lectura, la cuenta de integración de UiPath y una restauración de prueba. Véase [despliegue_odoo_gcp.md](despliegue_odoo_gcp.md).

- [ ] **Integrante 1:** comprobar el estado actual de GCP, facturación, cuotas, permisos y presupuesto. El documento de arquitectura solo registra el estado observado el 14 de octubre.
- [ ] Revisar el dimensionamiento, la red privada, la VM, la base de datos, los respaldos, los secretos y el acceso administrativo previstos en [la arquitectura](arquitectura_odoo_gcp.md).
- [ ] Desplegar Odoo Community, PostgreSQL, HTTPS y acceso seguro de consulta SQL. Guardar configuración reproducible sin contraseñas en Git.
- [x] Crear cuentas individuales de Odoo para los tres integrantes y verificar sus contraseñas iniciales.
- [ ] Crear una cuenta de integración con permisos mínimos para el robot. Definir el acceso de solo lectura a PostgreSQL sin publicar su puerto.
- [ ] Probar inicio de sesión web, conexión de Odoo a la base, respaldo y restauración de prueba, y acceso SQL de solo lectura para la evaluación.

**Salida:** ERP accesible en la nube y base consultable. Registrar URL, versión y fecha de la prueba, sin publicar credenciales.

## 3. Configurar los procesos centrales del ERP

- [ ] Configurar empresa, sucursales, usuarios, permisos, impuestos, unidades de medida, almacenes y reglas de inventario necesarias para el flujo de compra y venta.
- [ ] Activar y probar ventas, compras, inventario, empleados, facturación y CRM. Integrante 1 configura el núcleo; Integrante 2 integra CRM y portal; Integrante 3 configura Empleados. Definir cómo una cotización pasa a venta, una compra recibe productos y una orden genera factura.
- [ ] Configurar productos vendibles y materiales operativos, proveedores y clientes. Probar primero un caso pequeño de extremo a extremo en la interfaz y en SQL.
- [ ] Definir dónde se almacenarán y cómo se exportarán las facturas PDF para que sean visibles en una carpeta durante la evaluación.

**Salida:** una compra a proveedor y una venta completas, con inventario y facturas coherentes, antes de cargar cientos de registros.

## 4. Preparar y cargar los datos mínimos

El bloque de **Empleados** del Integrante 3 ya cumple sus mínimos: [35 empleados válidos, 5 departamentos del proyecto y 7 cargos](empleados.md), comprobados por Odoo y [SQL](../sql/validar_empleados.sql). Falta incorporar capturas de la interfaz al Manual 1. Los demás mínimos de esta fase siguen pendientes de comprobación por sus responsables.

| Dato | Mínimo del enunciado | Evidencia |
| --- | ---: | --- |
| Ventas a distintos clientes y con distintos productos | 150 | Interfaz de Odoo y consulta SQL |
| Cotizaciones a clientes y proveedores | 20 | Interfaz y consulta SQL; confirmar interpretación del total |
| Empleados | 35 | Interfaz y consulta SQL |
| Cargos | 6 | Interfaz y consulta SQL |
| Departamentos | 5 | Interfaz y consulta SQL |
| Compras con facturas correspondientes | 100 | Órdenes, facturas y consulta SQL |
| Materiales | 60 | Catálogo y consulta SQL; confirmar alcance por sucursal |
| Facturas PDF | 50, más las creadas durante la calificación | Carpeta, facturas en Odoo y consulta SQL |

- [ ] Diseñar datos coherentes y distintos: clientes, proveedores, productos, sucursales, precios, existencias y fechas. Integrante 1 coordina ventas, compras y facturas; Integrante 3 coordina empleados y los datos nuevos del RPA. Definir identificadores externos para repetir la carga sin duplicar registros.
- [ ] Automatizar la carga mediante interfaces soportadas por Odoo o importación controlada; registrar errores y totales por lote.
- [ ] Revisar y ejecutar en la versión realmente desplegada [las consultas analíticas](../sql/004_consultas_analisis.sql) y [la validación de carga](../sql/validar_carga_odoo.sql). Son borradores existentes, no evidencia de que ya funcionen contra una instancia real.
- [ ] Contar las entidades correctas y comprobar relaciones, estados y PDFs; un total global de filas no basta para demostrar cada requisito.

**Salida:** mínimos cumplidos en la interfaz y en la base, con consultas repetibles y los archivos PDF accesibles.

## 5. Completar el portal de compras y el CRM

- [ ] Implementar catálogo con imagen, descripción, precio y disponibilidad; carrito con agregar y quitar productos, impuestos y envío; y pago de prueba seguro.
- [ ] Verificar el flujo de cliente: registro, compra, descuento de inventario, orden en ERP, factura PDF y envío del comprobante.
- [ ] Integrar el registro del cliente y su historial de compra con el CRM. Evitar que el portal mantenga un catálogo o inventario divergente del ERP.
- [ ] Configurar un remitente institucional y una campaña de marketing. Después del correo de compra debe enviarse otro correo promocional, con asunto diferente, al cliente registrado durante la evaluación.

**Salida:** una compra web reproducible que produzca orden, factura, actualización de inventario, contacto CRM y dos correos en el orden solicitado.

## 6. Instrumentar Google Analytics 4

- [ ] Crear propiedad y flujo web GA4; conectarlos al portal. [La integración básica de Odoo](https://www.odoo.com/documentation/18.0/applications/websites/website/reporting/analytics.html) permite vincular Analytics, pero hay que comprobar por separado los eventos de comercio electrónico exigidos.
- [ ] Emitir `view_item`, `add_to_cart`, `begin_checkout` y `purchase` con productos, valor, moneda y un identificador de transacción coherente. Validar cada evento con [DebugView](https://developers.google.com/analytics/devguides/collection/ga4/validate-ecommerce).
- [ ] Generar tráfico y compras de prueba; comprobar conversión, adquisición, ingresos, productos más vendidos y abandono de carrito. Los informes históricos pueden tardar en reflejar eventos nuevos; preparar una comprobación en tiempo real para la prueba del auxiliar.
- [ ] Crear 3 segmentos de usuarios, 5 segmentos de eventos, 2 exploraciones que usen segmentos y 3 audiencias, al menos una personalizada. Guardar capturas y definiciones.

**Salida:** eventos observables y paneles con datos reales, incluida una interacción nueva durante la evaluación.

## 7. Integrar la gestión documental

- [x] Instalar [OCA/dms](gestion_documental.md) para Odoo Community 18, con acceso desde el ERP, categorías, etiquetas y búsqueda.
- [x] Cargar 5 facturas de proveedores, 5 contratos de outsourcing y 5 contratos de empleados; probar filtrado, descarga y permisos con cuentas individuales. Los PDF permanecen en [`../../output/pdf/gestion_documental`](../../output/pdf/gestion_documental).
- [ ] Reunir capturas de pantalla de los directorios, etiquetas, filtro y descarga para el Manual 1.

**Salida:** 15 documentos clasificados y accesibles desde el ERP.

## 8. Construir la automatización en UiPath

- [ ] **Integrante 3:** seguir el [diseño del RPA](diseno_rpa_excel.md) y preparar Excel de prueba con nombres y carpetas variables.
- [ ] Recorrer carpetas y libros, detectar las hojas `clientes` y `productos` por nombre, comprobar si son la quinta hoja, validar columnas y registrar filas aceptadas o rechazadas.
- [ ] Cargar mediante la interfaz autenticada de Odoo, acordada con Integrante 1; coordinar con Integrante 2 la visibilidad de productos y clientes en el portal. Evitar duplicados y generar un resumen de ejecución.
- [ ] Ejecutar el robot con archivos nuevos y comprobar los resultados en Odoo, el sitio web y PostgreSQL mediante consultas de solo lectura.

**Salida:** ejecución visible de UiPath, trazabilidad de los archivos procesados y datos nuevos consultables.

## 9. Redactar manuales y reunir evidencias

- [ ] **Manual 1:** instalación, funcionamiento de cada módulo, cargas masivas, compras, ventas, CRM, empleados, facturas y construcción paso a paso del RPA con sus ventajas.
- [ ] **Manual 2:** diagramas detallados de UiPath, compra a proveedores, venta, recorrido del producto (recepción, almacén, defectos, inventario, empaque y calidad) y recorrido del cliente por web y tienda física.
- [ ] **Manual 3:** análisis de negocio basado en GA4, con gráficos, interpretación de métricas y propuestas justificadas.
- [ ] Tomar capturas durante cada implementación; identificar fecha, sistema y resultado. Revisar que los tres PDF coincidan con la versión desplegada.

**Salida:** tres PDF completos y evidencia localizable para cada afirmación.

## 10. Ensayar la calificación y entregar

- [ ] Ejecutar el recorrido completo con una cuenta de prueba nueva: alta en CRM, navegación, carrito, pago, factura, correos y eventos GA4.
- [ ] Mostrar SQL de conteos y de los datos recién creados; comprobar los 50 PDF previos y el PDF generado en vivo.
- [ ] Ejecutar UiPath con un Excel no usado antes; verificar en web y SQL. Mostrar el gestor documental, segmentos, exploraciones y audiencias.
- [ ] Probar acceso, credenciales, conectividad, respaldos y plan de recuperación. Tener preparadas consultas y enlaces sin exponer secretos.
- [ ] Entregar los tres manuales por UEDI y conservar comprobante.

**Salida:** demostración ensayada y entrega acreditada.

## Orden recomendado para empezar

La ruta crítica es **GCP accesible para el equipo -> Odoo y PostgreSQL operativos -> flujo mínimo de compra/venta -> carga masiva -> integraciones -> ensayo completo**. El diseño de Excel, UiPath y los manuales puede avanzar en paralelo después de fijar el modelo y los procesos del ERP. El primer hito técnico debe ser una venta de prueba que aparezca en Odoo, en SQL y en un PDF; para el Integrante 3, el primer hito propio es cargar un cliente y un producto desde un Excel desconocido, verificar ambos en Odoo y SQL y comprobar que el producto aparece en el portal cuando esté publicado.
