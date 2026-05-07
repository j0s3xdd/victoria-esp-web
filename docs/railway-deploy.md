# Railway — Deploy del webhook

## 1. Subir el código a GitHub

El webhook vive en la carpeta `webhook/`. Tienes dos opciones:

### Opción A: Repo separado (recomendado)
```bash
cd webhook/
git init
git add .
git commit -m "Victoria webhook inicial"
gh repo create victoria-webhook --public --push --source=.
```

### Opción B: Mismo repo que la web (subdirectorio)
- Sube la carpeta `webhook/` al repo `j0s3xdd/victoria-esp-web`
- En Railway, configura "Root directory" como `/webhook`

---

## 2. Crear proyecto en Railway

1. railway.app → New Project
2. Deploy from GitHub repo → selecciona el repo
3. (Si usas Opción B): Settings → Source → Root Directory → `/webhook`
4. Railway detecta `package.json` y despliega automáticamente

---

## 3. Añadir variable de entorno

En Railway → Variables:
- `OPENAI_API_KEY` = tu API key de OpenAI (sk-proj-...)

> No añadas PORT — Railway lo gestiona solo.

---

## 4. Obtener la URL

Railway → tu servicio → Settings → Domains:
- Click "Generate Domain"
- URL resultante: `https://victoria-webhook-xxxx.up.railway.app`

Esta es la URL que pegas en ManyChat → External Request.

---

## 5. Verificar que funciona

```bash
curl https://TU-DOMINIO.up.railway.app/
# Respuesta esperada: Victoria webhook OK 🌿
```

```bash
curl -X POST https://TU-DOMINIO.up.railway.app/webhook \
  -H "Content-Type: application/json" \
  -d '{"message":"tengo mucha hinchazón después de comer, qué hago?","subscriber_id":"test123","first_name":"Ana"}'
```

Deberías recibir una respuesta JSON con el mensaje de Victoria.

---

## Costes estimados

- Railway: gratis hasta 500h/mes (plan Hobby $5/mes para producción)
- OpenAI GPT-4o-mini: ~$0.15 por 1M tokens de entrada. Una conversación = ~500 tokens. **1000 conversaciones ≈ $0.08**. Prácticamente gratis.
