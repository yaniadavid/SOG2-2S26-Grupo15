# Reparto técnico del bloque de portal, CRM, marketing y GA4

Este documento propone cómo dividir entre el Integrante 1 y el Integrante 2 el trabajo del bloque de portal web. El Integrante 1 prepara la base técnica dentro de Odoo, y el Integrante 2 conserva lo que depende de sus cuentas, de su criterio y del análisis de datos. El reparto es aproximado: si conviene mover una pieza, se mueve.

## 1. Estado de partida

Verificado el 22 de octubre de 2026 sobre el Odoo compartido:

| Elemento | Estado |
|---|---|
| Módulos `crm`, `sale_crm`, `website`, `website_crm`, `website_sale`, `website_sale_stock`, `delivery`, `payment_demo`, `mass_mailing`, `base_automation`, `website_mass_mailing` | Disponibles y sin instalar |
| Sitio web | No instalado |
| Servidor de correo saliente | Ninguno configurado |
| Productos vendibles | 40, con precio en GTQ y IVA de 12 % incluido en el precio, sin imágenes |
| Moneda y plan contable | GTQ y plan `gt` |
| PDF de facturas | Un servicio de la VM genera el PDF de toda factura publicada, también las de compras web |
| Cuentas | Cada integrante tiene un usuario interno. El del Integrante 2 aún no tiene permisos de CRM ni de tienda |

El módulo de automatización de marketing de Odoo es de la edición Enterprise y no está disponible. El segundo correo posterior a la compra se logra con una automatización de `base_automation`, que sí es de la edición Community.

## 2. Reparto

| Parte del bloque | Peso aproximado | Responsable | Alcance |
|---|---:|---|---|
| Tienda en línea | 30 % | Integrante 1 | Instalar sitio web y tienda, publicar los productos, carrito con impuestos y envío, pago de prueba y factura con su PDF |
| CRM | 10 % | Integrante 1 | Instalar el módulo, definir etapas y lograr que el registro de un cliente web cree su contacto y su oportunidad |
| Marketing técnico | 10 % | Integrante 1 | Plantilla del correo de compra y regla que envía un segundo correo promocional con asunto distinto; configurar el servidor de correo cuando exista el remitente |
| Integración con GA4 | 5 % | Integrante 1 | Colocar el ID de medición en el sitio y comprobar que se emiten `view_item`, `add_to_cart`, `begin_checkout` y `purchase` |
| Google Analytics 4 | 20 % | Integrante 2 | Propiedad y flujo de datos, validación en DebugView, 3 segmentos de usuarios, 5 de eventos, 2 exploraciones y 3 audiencias, una de ellas personalizada |
| Campaña de correo | 5 % | Integrante 2 | Diseño y texto del correo, que se califica por vistosidad y originalidad, y remitente que no sea una cuenta personal |
| Manual 3 | 15 % | Integrante 2 | Análisis de negocio con los datos reales de GA, con gráficos e interpretación |
| Capturas del Manual 1 | 5 % | Integrante 2 | Portal, CRM y marketing |

## 3. Orden de trabajo

1. **Integrante 1, fase 1.** Respaldo de la base, instalación de los módulos, tienda funcionando y una compra de prueba completa. Al terminar entrega la URL de la tienda y la lista de lo realizado.
2. **Integrante 2, en paralelo y desde el inicio.** Crear la propiedad de GA4, elegir el remitente de correo, preparar el diseño de la campaña y reunir las imágenes de los productos. Nada de esto depende de la fase 1.
3. **Fase 2, los dos.** El Integrante 1 coloca el ID de medición y revisa los eventos. El Integrante 2 los valida en DebugView y genera tráfico y compras de prueba.
4. **Fase 3.** Con el remitente disponible, el Integrante 1 configura el envío y se prueban los dos correos, el de la compra y después el promocional, con asuntos distintos.
5. **Integrante 2, al final.** Segmentos, exploraciones, audiencias y Manual 3, con los datos que ya existan.

## 4. Lo que necesita el Integrante 1 del Integrante 2

- El ID de medición de GA4 cuando exista la propiedad.
- Una cuenta remitente que no sea personal, con la forma de conectarla (servidor SMTP y credenciales entregadas por un canal privado, nunca por el chat del grupo ni por el repositorio).
- Las imágenes y descripciones de los productos. Si no hay fotos propias, el Integrante 1 puede generar imágenes sencillas y originales, que se verán básicas. No se deben usar imágenes de otros sitios por la regla de no copias.
- Confirmación de que el Integrante 2 no instaló ni configuró módulos de este bloque por su cuenta.

## 5. Reglas de coordinación

- Una persona a la vez cambia la configuración de un módulo, y se avisa en el grupo antes de hacerlo.
- El Integrante 1 trabaja con la cuenta administradora y deja constancia de cada cambio. El Integrante 2 trabaja con su usuario.
- Las contraseñas y claves se comparten solo por Secret Manager o por un canal privado.
- Los cambios al repositorio van por ramas `feature` y por revisión.

## 6. Criterios de aceptación de la fase técnica

La fase 1 se da por completa solo si una compra hecha desde la tienda con un cliente nuevo produce todo lo siguiente, y se comprueba en la interfaz y con una consulta SQL:

- Una orden de venta confirmada con el IVA incluido y el costo de envío.
- Una factura publicada y su PDF en la carpeta de facturas.
- Un contacto en la base y una oportunidad en el CRM.
- El inventario descontado.

## 7. Riesgos y límites

- Al instalar el sitio web, la página principal de la dirección del servidor pasa a mostrar la tienda. El inicio de sesión de Odoo sigue en su ruta actual.
- Los módulos de sitio web y tienda aumentan la carga sobre una base pequeña. Por eso se toma un respaldo antes de empezar.
- Sin un dominio propio, los correos pueden llegar a la carpeta de no deseados.
- Que Odoo emita los cuatro eventos de comercio electrónico debe comprobarse con DebugView y no darse por supuesto.
- Los segmentos, las exploraciones y las audiencias se crean en la interfaz de Google Analytics y necesitan datos reales para tener contenido.

## 8. Cómo se revierte

Antes de instalar se toma un respaldo en demanda de Cloud SQL. Si la instalación deja el sistema en mal estado, se restaura ese respaldo. La restauración ya se ensayó sobre un clon temporal y sus datos coincidieron con producción.
