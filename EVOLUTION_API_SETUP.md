# Evolution API Setup Guide for VittaSaathi

## ⚡ Why Evolution API?

| Feature | Twilio | Evolution API |
|---------|--------|---------------|
| Cost | $0.005/message | **FREE** |
| Daily Limit | 50 (sandbox) | **UNLIMITED** |
| Setup | Easy | Medium |
| Reliability | Very High | Good |
| Official API | Yes | No (uses WhatsApp Web) |

## 📋 Prerequisites

1. **Docker Desktop** installed on your computer
2. A **WhatsApp account** (personal or business)
3. **Phone connected to internet** (your phone stays connected like WhatsApp Web)

---

## 🚀 Quick Setup (5 minutes)

### Step 1: Install Docker (if not installed)

**Windows:**
1. Download: https://www.docker.com/products/docker-desktop/
2. Install and restart computer
3. Verify: Open PowerShell and run `docker --version`

### Step 2: Run Evolution API

Open PowerShell and run:

```powershell
docker run -d --name evolution_api -p 8080:8080 -e AUTHENTICATION_API_KEY=MySecretKey123 atendai/evolution-api:latest
```

Wait about 30 seconds for it to start.

### Step 3: Verify Installation

Open browser: http://localhost:8080

You should see:
```json
{
  "status": 200,
  "message": "Welcome to the Evolution API, it is working!",
  "version": "2.x.x"
}
```

### Step 4: Create WhatsApp Instance

**Using curl (PowerShell):**
```powershell
curl -X POST "http://localhost:8080/instance/create" `
  -H "apikey: MySecretKey123" `
  -H "Content-Type: application/json" `
  -d '{"instanceName":"vittasaathi","qrcode":true,"integration":"WHATSAPP-BAILEYS"}'
```

**Or use Postman:**
- POST http://localhost:8080/instance/create
- Header: `apikey: MySecretKey123`
- Body: `{"instanceName":"vittasaathi","qrcode":true,"integration":"WHATSAPP-BAILEYS"}`

### Step 5: Connect WhatsApp (Scan QR Code)

1. Get QR Code:
   - Open browser: http://localhost:8080/manager
   - Or call: GET http://localhost:8080/instance/connect/vittasaathi

2. Open WhatsApp on your phone:
   - Go to Settings > Linked Devices
   - Tap "Link a Device"
   - Scan the QR code

3. ✅ Once connected, your instance is ready!

### Step 6: Set Up Webhook (for n8n)

Configure Evolution to send incoming messages to your n8n workflow:

```powershell
curl -X POST "http://localhost:8080/webhook/set/vittasaathi" `
  -H "apikey: MySecretKey123" `
  -H "Content-Type: application/json" `
  -d '{
    "enabled": true,
    "url": "https://your-ngrok-url/webhook/evolution-incoming",
    "webhookByEvents": true,
    "events": ["MESSAGES_UPSERT"]
  }'
```

---

## 🔧 VittaSaathi Configuration

Add these to your `.env` file:

```env
# Evolution API Configuration
EVOLUTION_API_URL=http://localhost:8080
EVOLUTION_API_KEY=MySecretKey123
EVOLUTION_INSTANCE_NAME=vittasaathi
```

For Render deployment, you'll need to:
1. Host Evolution API on a VPS (DigitalOcean, AWS, etc.)
2. Use the public URL instead of localhost

---

## 📱 Testing

### Send a test message:

```powershell
curl -X POST "http://localhost:8080/message/sendText/vittasaathi" `
  -H "apikey: MySecretKey123" `
  -H "Content-Type: application/json" `
  -d '{
    "number": "919003360494",
    "text": "Hello from VittaSaathi! 🙏"
  }'
```

---

## ⚠️ Important Notes

1. **Phone must stay connected**: Evolution uses WhatsApp Web protocol, so your phone must be online
2. **Don't spam**: WhatsApp may ban accounts that send too many messages too quickly
3. **For production**: Consider using a dedicated phone/number for the bot
4. **Docker must be running**: Evolution runs in Docker container

---

## 🔄 Switching from Twilio to Evolution

VittaSaathi has built-in support for both. The `evolution_service.py` automatically:
1. Checks if Evolution API is available
2. Falls back to Twilio if Evolution is not configured
3. Uses a universal `send_whatsapp_message()` function

---

## 📊 n8n Workflow Update

For n8n to receive messages from Evolution API:

1. Create a webhook node in n8n: `POST /webhook/evolution-incoming`
2. Configure Evolution to send to your n8n URL
3. Update the workflow to parse Evolution's message format

Evolution sends messages in this format:
```json
{
  "event": "messages.upsert",
  "instance": "vittasaathi",
  "data": {
    "key": {
      "remoteJid": "919003360494@s.whatsapp.net"
    },
    "message": {
      "conversation": "Hello"
    }
  }
}
```

---

## 🆘 Troubleshooting

**Problem: Can't connect to Evolution API**
- Make sure Docker is running
- Check: `docker ps` to see if container is running
- Check logs: `docker logs evolution_api`

**Problem: QR Code not showing**
- Instance might already be connected
- Try: `docker restart evolution_api`

**Problem: Messages not sending**
- Check if WhatsApp is still connected
- GET http://localhost:8080/instance/connectionState/vittasaathi

---

## 📞 Need Help?

- Evolution API Docs: https://doc.evolution-api.com
- Evolution GitHub: https://github.com/EvolutionAPI/evolution-api
