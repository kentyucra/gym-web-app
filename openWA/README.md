# OpenWA Service

OpenWA is planned as the WhatsApp messaging service for gym notifications, such as member invites, payment reminders, membership expiration notices, and weekly class schedules.

Start with the Docker development setup first to confirm it works locally.

## 1. Clone OpenWA

From a folder outside this app, clone the OpenWA repository:

```bash
git clone https://github.com/rmyndharis/OpenWA.git
cd OpenWA
```

## 2. Start The Development Docker Setup

```bash
docker compose -f docker-compose.dev.yml up -d
```

Then open:

```txt
Dashboard: http://localhost:2886
API:       http://localhost:2785/api
Swagger:   http://localhost:2785/api/docs
```

The Docker setup exposes:

- API on port `2785`
- Dashboard on port `2886`
- Swagger docs at `/api/docs`

## 3. API Key

The API examples below require an API key.

Replace this placeholder:

```txt
YOUR_API_KEY
```

with the API key configured by the OpenWA service.

## 4. Create A WhatsApp Session

Create a session for the gym bot:

```bash
curl -X POST http://localhost:2785/api/sessions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{"name": "gym-bot"}'
```

Save the returned `sessionId`.

## 5. Start The Session

Replace `{sessionId}` with the session ID returned from the previous step:

```bash
curl -X POST http://localhost:2785/api/sessions/{sessionId}/start \
  -H "X-API-Key: YOUR_API_KEY"
```

## 6. Get The QR Code

```bash
curl http://localhost:2785/api/sessions/{sessionId}/qr \
  -H "X-API-Key: YOUR_API_KEY"
```

Scan the QR code with WhatsApp.

## 7. Send A Test Message

```bash
curl -X POST http://localhost:2785/api/sessions/{sessionId}/messages/send-text \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "chatId": "51987654321@c.us",
    "text": "Hello from OpenWA"
  }'
```

## Peru Phone Number Format

For Peru numbers, use:

```txt
51 + phone_number + @c.us
```

Example:

```txt
51987654321@c.us
```

## Production Setup Later

For production later, use the profile-based Docker setup:

```bash
docker compose --profile postgres --profile redis --profile with-dashboard up -d
```

Do this only after the local Docker development setup works.

## How This Fits Site Fitness

OpenWA can eventually be called by the Flask backend when the app needs to send:

- Member portal invite links
- Membership expiring in 7 days
- Membership expired notices
- Payment reminders
- Weekly class schedules

For the MVP, keep the first integration simple:

```txt
Flask API creates notification
Flask API calls OpenWA send-text endpoint
OpenWA sends WhatsApp message
```

Suggested backend environment variables for later:

```txt
OPENWA_API_URL=http://localhost:2785/api
OPENWA_API_KEY=dev-admin-key
OPENWA_SESSION_ID=b6dc3e8b-6f3f-45bd-9b3f-25a29c2eb89d
OPENWA_DEFAULT_COUNTRY_CODE=51
```

`OPENWA_SESSION_ID` must be the session ID returned by OpenWA when you create
the WhatsApp session. In local development, OpenWA creates `dev-admin-key` as
the default API key.
