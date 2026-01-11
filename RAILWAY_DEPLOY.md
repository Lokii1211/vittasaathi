# MoneyViya - Railway Deployment Guide
## 24/7 Cloud Hosting (Free Tier)

---

## Why Railway over Render?

| Feature | Render (Current) | Railway (Recommended) |
|---------|------------------|----------------------|
| Cold Start | 30-50 seconds | ~5 seconds |
| Env Vars | Buggy | Works instantly |
| Free Tier | 750 hours/month | $5 credit/month |
| Python Support | Good | Excellent |

---

## Step 1: Create Railway Account

1. Go to: **https://railway.app**
2. Click **Login** → Sign in with GitHub
3. Authorize Railway

---

## Step 2: Create New Project

1. Click **New Project**
2. Select **Deploy from GitHub repo**
3. Find and select **Lokii1211/MoneyViya**
4. Click **Deploy Now**

---

## Step 3: Add Environment Variables

1. Click on your deployed service
2. Go to **Variables** tab
3. Add these variables:

```
OPENAI_API_KEY=sk-proj-xxxxx
WHATSAPP_CLOUD_TOKEN=EAFp3Mo4Xz2gBQTJiNQJKK4Exzvd...
WHATSAPP_PHONE_NUMBER_ID=950285898166827
WHATSAPP_VERIFY_TOKEN=MoneyViya_webhook_verify_2024
```

4. Railway automatically redeploys when you add variables!

---

## Step 4: Get Your Domain

1. Go to **Settings** tab
2. Under **Domains**, click **Generate Domain**
3. You'll get something like: `MoneyViya-production.up.railway.app`

---

## Step 5: Update WhatsApp Webhook

1. Go to Meta Developer Dashboard
2. Update webhook URL to:
```
https://YOUR-APP.up.railway.app/webhook/whatsapp-cloud
```

---

## Step 6: Test

1. Open: `https://YOUR-APP.up.railway.app`
2. You should see the new dashboard!
3. Send "Hi" to WhatsApp test number
4. You should get a reply!

---

## Railway CLI (Optional)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link project
cd MoneyViya
railway link

# Deploy
railway up

# View logs
railway logs
```

---

## Monitoring

Railway provides:
- Real-time logs
- Metrics (CPU, Memory)
- Automatic HTTPS
- Automatic deploys on git push

---

## Free Tier Limits

- $5 credit per month
- ~500 hours of runtime
- More than enough for a hackathon!

---

## Troubleshooting

### App not starting?
Check logs: Railway Dashboard → Deployments → View Logs

### Env vars not working?
Railway applies env vars immediately but may need a redeploy.
Click **Redeploy** button.

### Need more resources?
Add payment method for $5/month starter plan.

---

**Railway is faster and more reliable than Render for Python apps!** 🚀

