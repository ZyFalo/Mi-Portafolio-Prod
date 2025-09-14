# GTM + GA4 — Instrumentación y Verificación

Este documento resume cómo se instrumentó el sitio con Google Tag Manager (GTM) y Google Analytics 4 (GA4), qué eventos se envían, cómo configurarlos en GTM y cómo verificarlos con capturas de pantalla.

## Variables de entorno

- `GTM_CONTAINER_ID`: contenedor GTM (opcional; si no está, se usa GA4 `gtag` fallback).
- `GA_MEASUREMENT_ID`: ID de medición GA4 (usado como fallback si no hay GTM).

## Eventos y mapeo (GA4 estándar + personalizados)

- Page view
  - Evento: `page_view`
  - Parámetros: `page_location`, `page_title`, `page_referrer`, `utm_source`, `utm_medium`, `utm_campaign`, `utm_term`, `utm_content`.

- Contacto
  - Submit: `contact_form_submit` (custom) — antes de enviar POST.
  - Éxito: `contact_submit_success` (custom).
  - Lead: `generate_lead` (GA4 estándar) — al éxito; no se duplica en servidor.

- Home (Desarrolladores)
  - Click banner: `developer_portfolio_click` (custom) + `select_promotion` (GA4 estándar).
  - Click card: `developer_card_click` (custom).
  - Vista sección: `developer_section_view` (custom).

- OpenApp (Gadgets)
  - Vista de lista: `view_item_list` (GA4 estándar) con `items` [{item_id, item_name}].
  - Click en ítem: `gadget_click` (custom) + `select_content` (GA4 estándar).
  - Vista de detalle: `view_item` (GA4 estándar). Adicional: `gadget_view` (custom si viene desde lista).

- FAQ
  - Click en pregunta: `faq_click` (custom) + `select_content` (GA4 estándar, content_type=faq_question).

## Configuración en GTM

1) Tag GA4 Configuration
   - Measurement ID: tu `GA_MEASUREMENT_ID`.
   - Trigger: All Pages.

2) Opcional (page_view controlado por GTM)
   - Alternativa: desactivar el page_view automático y crear un Tag GA4 Event `page_view` con trigger Custom Event `page_view` para usar UTMs del `dataLayer`. No mezclar ambas opciones.

3) Tags GA4 Event (Custom Event triggers)
   - `generate_lead`: Trigger Custom Event `generate_lead`. Params: `form_name`, `method`, `page_location`.
   - `contact_form_submit`: Trigger `contact_form_submit`. Params: `form_name`, `page_location`.
   - `contact_submit_success`: Trigger `contact_submit_success`. Params: `form`, `status`.
   - `select_promotion`: Trigger `select_promotion`. Params: `promotion_name`, `creative_name`, `location_id`, `link_url`, `utm_content`, `page_location`.
   - `view_item_list`: Trigger `view_item_list`. Params: `item_list_id`, `item_list_name`, `items[]`, `page_location`.
   - `select_content`: Trigger `select_content`. Params: `content_type`, `item_id`, `item_name`, `item_list_name` (cuando aplica), `page_location`.
   - `view_item`: Trigger `view_item`. Params: `item_id`, `item_name`, `page_location`.

4) Variables recomendadas en GTM
   - URL Query: `utm_source`, `utm_medium`, `utm_campaign`, `utm_term`, `utm_content`.
   - Data Layer: variables homónimas si prefieres leerlas directo del `dataLayer`.

## Definiciones personalizadas en GA4 (opcional)

- Admin → Custom definitions → Create custom dimension (Scope: Event):
  - `utm_source`, `utm_medium`, `utm_campaign`, `utm_term`, `utm_content`.
  - Otras que te interese analizar (`promotion_name`, `content_type`, etc.).

## Verificación (con capturas)

1) GTM Preview
   - Abre el contenedor → Preview → ingresa la URL local/producción.
   - Navega: Home (`/`), Gadgets (`/open/`), Detalle (`/open/<slug>/`), Contacto (`/contactame/`), FAQ (`/fyq/`).
   - Haz clic en un banner de desarrollador y un gadget.
   - Captura: `docs/analytics/preview.png` (lista de eventos y tags disparados con 1–2 ejemplos).

2) GA4 DebugView
   - GA4 → Configure → DebugView.
   - Observa caer eventos `page_view`, `select_promotion`, `view_item_list`, `select_content`, `view_item`, `generate_lead`.
   - Captura: `docs/analytics/debugview.png` (timeline con eventos y parámetros visibles).

3) GA4 Realtime (UTMs)
   - Entra con URL con UTM: `/?utm_source=demo&utm_medium=test&utm_campaign=gtm&utm_content=banner_home`.
   - Revisa Realtime → Traffic source / Session source/medium.
   - Captura: `docs/analytics/realtime.png` (orígenes con UTMs y 1 usuario activo).

Coloca las capturas en `docs/analytics/` con los nombres sugeridos para que se muestren en el repo.

## Notas

- `generate_lead` se envía solo en cliente tras éxito del formulario (no duplicado en servidor).
- Si usas solo GA4 sin GTM, el fallback de `gtag` convierte `dataLayer.push({event: ...})` en `gtag('event', ...)` automáticamente.
- Evita disparar doble `page_view`: o lo envía GTM automáticamente, o lo generas con el Custom Event.

