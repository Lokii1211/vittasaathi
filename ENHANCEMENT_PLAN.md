# MoneyViya Enhancement Plan
# =============================

## Current Issues:
1. Twilio sandbox limit (50 msg/day) - CRITICAL: Switch to production or wait 24hrs
2. Onboarding shows numbered options - Need to update ALL language templates
3. OpenAI not being used for onboarding NLP
4. Missing PDF report generation
5. Missing OCR for receipt scanning
6. Missing voice reply

## Features to Implement:

### Phase 1: Fix Critical Issues
- [ ] Update ALL onboarding messages (Tamil, Telugu, Kannada, etc.) to NLP-based
- [ ] Use OpenAI for understanding onboarding responses
- [ ] Add voice transcription during onboarding

### Phase 2: Advanced Features
- [ ] PDF Report Generation with Charts
- [ ] Receipt/Bill OCR scanning
- [ ] Voice reply generation
- [ ] AI-powered financial advice
- [ ] Smart expense categorization
- [ ] Budget recommendations
- [ ] Savings goal tracking with charts

### Phase 3: Monetization Features
- [ ] Premium subscription model
- [ ] Family finance sharing
- [ ] Investment tracking
- [ ] Bill reminders
- [ ] Spending insights

## API Keys Required:
1. OPENAI_API_KEY - For NLP, Whisper, GPT
2. TWILIO_ACCOUNT_SID - For WhatsApp
3. TWILIO_AUTH_TOKEN - For WhatsApp

## Implementation Priority:
1. Make onboarding work with plain text (no numbers)
2. Add PDF report generation
3. Add receipt OCR
4. Polish mobile UI

