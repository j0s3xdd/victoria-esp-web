# Make.com — Escenario: Stripe → ManyChat

## Objetivo
Cuando Stripe confirme un pago del RESET 45 (49€), Make.com añade el tag `reset45-activo` al suscriptor de ManyChat correspondiente. Eso dispara automáticamente la secuencia de 5 días.

---

## Requisitos
- Cuenta Make.com (plan gratuito funciona para esto)
- Stripe: API Key (modo live) y Webhook configurado
- ManyChat: API Key (Settings → API → copy token)
- El número de teléfono del comprador debe coincidir con el de WhatsApp en ManyChat

---

## Paso 1: Crear el escenario

1. Make.com → Create new scenario
2. Nombre: `Stripe → ManyChat RESET 45`

---

## Paso 2: Módulo 1 — Trigger Stripe

1. Add module → busca **Stripe** → elige **Watch Events (Webhook)**
2. Click "Add" para crear un nuevo webhook
3. Copia la URL del webhook que te da Make.com
4. Ve a Stripe Dashboard → Developers → Webhooks → Add endpoint
   - URL: pega la URL de Make.com
   - Events to send: selecciona `checkout.session.completed` (o `payment_intent.succeeded`)
5. Vuelve a Make.com → click "OK"
6. Haz un pago de prueba en Stripe para que Make.com reciba la estructura del evento

**Datos que llegan de Stripe:**
```json
{
  "type": "checkout.session.completed",
  "data": {
    "object": {
      "customer_details": {
        "phone": "+34612345678",
        "email": "cliente@email.com",
        "name": "Ana García"
      },
      "amount_total": 4900,
      "currency": "eur",
      "metadata": {}
    }
  }
}
```

---

## Paso 3: Módulo 2 — Filter (solo pagos de 49€)

Añade un **Filter** entre Stripe y ManyChat para evitar falsos triggers:

- Condition: `amount_total` **Equal to** `4900`

---

## Paso 4: Módulo 3 — Buscar suscriptor en ManyChat por teléfono

1. Add module → busca **ManyChat** → elige **Make an API Call**
   - Method: `GET`
   - URL: `https://api.manychat.com/fb/subscriber/findByPhone`
   - Query params: `phone` = número del módulo Stripe (`customer_details.phone`)
   - Headers: `Authorization: Bearer TU_MANYCHAT_API_KEY`

**Respuesta esperada:**
```json
{
  "status": "success",
  "data": {
    "id": "1234567890"
  }
}
```

> **Nota:** El teléfono en Stripe debe estar en formato E.164 (`+34612345678`). El formulario de Stripe Payment Link tiene campo de teléfono — asegúrate de activarlo como obligatorio.

---

## Paso 5: Módulo 4 — Añadir tag en ManyChat

1. Add module → **ManyChat** → **Make an API Call**
   - Method: `POST`
   - URL: `https://api.manychat.com/fb/subscriber/addTag`
   - Body (JSON):
   ```json
   {
     "subscriber_id": "{{ID del módulo anterior}}",
     "tag_id": "ID_DEL_TAG_reset45-activo"
   }
   ```
   - Headers: `Authorization: Bearer TU_MANYCHAT_API_KEY`

**Para obtener el tag_id:**
- ManyChat → Settings → Tags → click en el tag `reset45-activo`
- El ID aparece en la URL: `/tags/XXXXXXX`

---

## Paso 6: Módulo 5 (opcional) — Enviar email de confirmación

Si quieres enviar un email adicional además del WhatsApp:
- Add module → **Gmail** o **SendGrid** → Send Email
- Para: `customer_details.email`
- Asunto: `Tu RESET 45 está activado ✓`
- Cuerpo: confirmación simple con instrucciones

---

## Configuración final en Stripe

En Stripe Dashboard → Payment Links → tu link de RESET 45:
1. **After payment:** Redirect to URL → `https://victoria-esp-web.vercel.app/gracias.html`
2. **Collect phone numbers:** Activado y obligatorio
3. **Webhook:** Ya configurado en el Paso 2

---

## Checklist de prueba

- [ ] Stripe en modo test → hacer pago de prueba
- [ ] Make.com recibe el evento
- [ ] Filter pasa (amount_total = 4900)
- [ ] ManyChat encuentra el suscriptor por teléfono
- [ ] Tag `reset45-activo` aparece en el perfil del suscriptor
- [ ] Secuencia de 5 días arranca en ManyChat
- [ ] Suscriptor redirigido a gracias.html

---

## Solución de problemas

| Problema | Causa probable | Solución |
|----------|----------------|----------|
| ManyChat no encuentra al suscriptor | Teléfono en formato incorrecto | El comprador debe haber escrito previamente al bot de WhatsApp |
| Tag no se añade | tag_id incorrecto | Verificar ID del tag en ManyChat Settings |
| Secuencia no arranca | Tag no conectado a secuencia | En ManyChat, la secuencia debe tener como trigger "Tag added: reset45-activo" |

---

## Flujo completo

```
Stripe pago ✓
    │
    ▼
Make.com recibe webhook
    │
    ▼
Filter: ¿amount = 49€? ──No──▶ Stop
    │ Sí
    ▼
Buscar suscriptor por teléfono en ManyChat
    │
    ▼
Añadir tag "reset45-activo"
    │
    ▼
ManyChat detecta tag → arranca secuencia Día 1
    │
    ▼
Cliente recibe mensaje de bienvenida en WhatsApp
```
