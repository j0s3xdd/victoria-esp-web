# ManyChat — Configuración completa

## Requisitos previos
- Cuenta ManyChat Pro (necesitas Pro para WhatsApp y External Request)
- WhatsApp Business conectado a ManyChat
- URL del webhook Railway desplegado (ej: `https://victoria-webhook.up.railway.app/webhook`)
- Stripe Payment Link del RESET 45 (49€)

---

## FLUJO 1: Keyword "RESET 45" → Enviar link de pago

**Dónde:** Automation → Keywords

1. Click "New Keyword"
2. Keyword: `RESET 45`
3. Match type: **Contains** (para que funcione aunque escriban "reset 45" en minúsculas)
4. Añadir segunda keyword: `reset 45` (por si acaso)
5. Action: **Send Message**
6. Mensaje:

```
Hola {{first name}} 👋

Me alegra que quieras empezar el RESET 45.

En los próximos 5 días vamos a trabajar juntas para reducir la hinchazón, recuperar energía y empezar a sentirte bien con tu alimentación. Sin dietas estrictas. Sin pasar hambre.

Aquí tienes el enlace para reservar tu plaza (solo quedan unas pocas):

👉 [ENLACE STRIPE AQUÍ]

Precio: 49€ · Pago único y seguro.

En cuanto confirmes el pago, te mando el primer mensaje. ¿Cualquier duda, escríbeme aquí mismo!
```

> Sustituye `[ENLACE STRIPE AQUÍ]` con tu Stripe Payment Link.

---

## FLUJO 2: Secuencia 5 días (se activa tras pago confirmado)

**Dónde:** Automation → Sequences → New Sequence

Nombre: `RESET 45 — 5 días`

### Cómo se activa
- La secuencia se activa desde Make.com cuando Stripe confirma el pago
- Make.com añade el tag `reset45-activo` al suscriptor → eso dispara el día 1

**Crear tag:** Settings → Tags → New Tag → `reset45-activo`

### Configurar la secuencia

| Mensaje | Timing | Contenido |
|---------|--------|-----------|
| Día 1 | Inmediato al activar | Ver copy Día 1 |
| Día 2 | 24h después | Ver copy Día 2 |
| Día 3 | 24h después | Ver copy Día 3 |
| Día 4 | 24h después | Ver copy Día 4 |
| Día 5 | 24h después | Ver copy Día 5 (incluye oferta) |

**Para cada mensaje:**
1. New Step → Send Message
2. Pegar el copy del día correspondiente (ver archivo `whatsapp-copy-5-dias.md`)
3. En timing: "After 24 hours" (excepto el primero: "Immediately")

---

## FLUJO 3: Default Reply → Webhook IA Victoria

**Dónde:** Automation → Default Reply

Este flujo se activa cuando alguien escribe cualquier cosa que ManyChat no reconoce como keyword.

1. Automation → Default Reply → Edit
2. Borrar el mensaje por defecto
3. Add Action → **External Request**

**Configuración del External Request:**
- Method: `POST`
- URL: `https://TU-DOMINIO.up.railway.app/webhook`
- Headers: `Content-Type: application/json`
- Body (JSON):
```json
{
  "message": "{{last input text}}",
  "subscriber_id": "{{subscriber id}}",
  "first_name": "{{first name}}"
}
```
- Response timeout: 10 segundos
- On success: usa la respuesta para enviar un mensaje
- On error: envía mensaje de fallback: "Un momento, ahora mismo te contesto 🌿"

**Mapear la respuesta:**
- ManyChat recibe el JSON `{ "version": "v2", "content": { "messages": [...] } }`
- El texto de la respuesta se envía automáticamente al suscriptor

---

## FLUJO 4: Keyword "SÍ" → Notificar a Victoria (Live Chat)

**Dónde:** Automation → Keywords

1. New Keyword
2. Keyword: `SÍ` + `si` + `Si` + `SI`
3. Match type: **Is** (exacto, para evitar falsos positivos)
4. Actions:
   a. **Send Message:**
   ```
   Perfecto, {{first name}}. En unas horas Victoria te escribe personalmente para contarte todos los detalles del programa. ¡Nos vemos pronto! 🌿
   ```
   b. **Notify Admins** (o Live Chat Takeover):
   - Add Action → Notify Admins → selecciona a Victoria
   - Mensaje interno: `{{first name}} quiere info del programa completo 12 semanas. Último mensaje: {{last input text}}`

---

## FLUJO 5: Bienvenida inicial (opt-in)

**Dónde:** Automation → Welcome Message

Cuando alguien empieza a hablar con el bot por primera vez:

```
Hola {{first name}} 👋 Soy Victoria Esp, nutricionista especializada en mujeres de 45 a 65 años.

Si quieres empezar el RESET 45 (5 días para deshincharte y recuperar energía), escríbeme:

👉 RESET 45

¿Tienes alguna pregunta? Escríbeme aquí mismo.
```

---

## Tags necesarios

| Tag | Para qué |
|-----|----------|
| `reset45-activo` | Activar secuencia de 5 días (lo añade Make.com tras pago) |
| `reset45-completado` | Añadir al final del día 5 para segmentar |
| `interesada-programa-12s` | Añadir cuando alguien escribe SÍ |

---

## Checklist de prueba

- [ ] Escribir "RESET 45" → recibir link de Stripe
- [ ] Completar pago de prueba (Stripe test mode) → Make.com añade tag → secuencia arranca
- [ ] Escribir pregunta aleatoria → IA responde como Victoria
- [ ] Escribir "SÍ" → mensaje de confirmación + notificación a Victoria
- [ ] Verificar que los 5 mensajes llegan en el horario correcto
