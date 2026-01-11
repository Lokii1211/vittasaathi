# WhatsApp Cloud API Setup Guide
## 24/7 Operation - No Phone or Laptop Required!

---

## ✅ Your Credentials (Already Configured)

```
Phone Number ID: 950285898166827
Access Token: EAFp3Mo4Xz2gBQWZCJg58ZAZA8eCk8kxhc9Wswd5YfMC0zuX...
Business Account ID: 876858271395794
```

---

## 📋 Step 1: Update Environment Variables

Add these to your Render.com environment variables:

1. Go to: https://dashboard.render.com
2. Select your **MoneyViya-1** service
3. Go to **Environment** tab
4. Add these variables:

```
WHATSAPP_CLOUD_TOKEN=EAFp3Mo4Xz2gBQWZCJg58ZAZA8eCk8kxhc9Wswd5YfMC0zuXSyconJrbtqvmyegIeRmNxi6iZCHBy9OkbbMvyBWUehBydhZBjKd2mVCZCs3DdUVkzVHZBwGpt9Ap5wqfZA2zQntJi4czoyfXCu0OWHLUG6NmGAAyodB2GBo7Y1nuMuFX7x3ZCun6RLYVhJJ9Q1NkuG5doUqvs1vcSf28MbnqMZBcITKeLZBG2WLyjG65gs3sq4NvtNylvrtUEIAEx4zXbVZBAZCXsPkGgHZAlYUhxH3QZBo5

WHATSAPP_PHONE_NUMBER_ID=950285898166827

WHATSAPP_BUSINESS_ACCOUNT_ID=876858271395794

WHATSAPP_VERIFY_TOKEN=MoneyViya_webhook_verify_2024
```

5. Click **Save Changes** (service will redeploy)

---

## 📋 Step 2: Configure Webhook in Meta Dashboard

1. Go to: https://developers.facebook.com/apps/
2. Select your MoneyViya app
3. Go to **WhatsApp** → **Configuration**
4. Find **Webhook** section
5. Click **Edit** or **Configure Webhooks**

### Webhook URL:
```
https://MoneyViya-1.onrender.com/webhook/whatsapp-cloud
```

### Verify Token:
```
MoneyViya_webhook_verify_2024
```

6. Click **Verify and Save**

---

## 📋 Step 3: Subscribe to Webhook Events

After verifying, subscribe to these events:
- ✅ `messages` (required - to receive messages)
- ✅ `messaging_postbacks` (for button clicks)
- ✅ `messaging_optins` (for opt-in events)

---

## 📋 Step 4: Add Your Phone as Test Recipient

1. In Meta Dashboard, go to **API Testing**
2. Under **"Add a recipient phone number"**
3. Add your phone: `+91 9363324580`
4. Verify with the OTP sent to your phone

---

## 📋 Step 5: Test the Integration

1. Open WhatsApp
2. Message the **test phone number** shown in Meta Dashboard (e.g., +1 555 158 9563)
3. Send "Hi"
4. You should receive a reply from MoneyViya!

---

## 🎯 How It Works Now

```
User sends message to Meta's test number
           ↓
Meta's servers receive it (24/7 cloud)
           ↓
Webhook POST to https://MoneyViya-1.onrender.com/webhook/whatsapp-cloud
           ↓
MoneyViya processes message
           ↓
WhatsApp Cloud API sends reply
           ↓
User receives reply
```

**No laptop needed! No phone online needed! It's fully cloud-based!**

---

## ⚠️ Important Notes

### Access Token Expiry
- The temporary access token expires in **60 minutes**
- For permanent token:
  1. Go to **Business Settings** → **System Users**
  2. Create a system user
  3. Generate permanent token

### Test Number Limitation
- The test number is provided by Meta
- To use YOUR phone number:
  1. Go to **Phone Numbers** management
  2. Add your business phone number
  3. Complete verification (takes 1-2 days)

### Free Tier Limits
- 1000 service conversations/month (FREE)
- 250 business-initiated conversations/day
- This is enough for testing and hackathon!

---

## 🆘 Troubleshooting

### Webhook not verifying?
- Check if Render deployed successfully
- Check logs: `https://dashboard.render.com/web/srv-xxx/logs`
- Ensure verify token matches exactly

### Messages not receiving?
- Check Meta webhook subscriptions
- Ensure `messages` event is subscribed
- Check Render logs for incoming requests

### Replies not sending?
- Check access token is not expired
- Verify phone number ID is correct
- Check Render logs for API errors

---

## 📊 Monitoring

View logs in real-time:
```
https://dashboard.render.com/web/srv-YOUR-SERVICE-ID/logs
```

You'll see:
```
[WhatsApp Cloud] Received: {...}
[WhatsApp Cloud] Message from +919363324580: Hi
[WhatsApp Cloud] Reply sent: {'success': True, ...}
```

---

**Your MoneyViya is now running 24/7 in the cloud! 🚀**

