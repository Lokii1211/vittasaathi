---
description: Fix MoneyViya Issues - OTP, NLP, Persistence, Dashboard
---

# MoneyViya Critical Fixes - Implementation Plan

## Issues to Fix:
1. **OTP not receiving** - WhatsApp sending not working
2. **NLP not understanding** - Agent needs smarter understanding
3. **Data not persisting** - Store in JSON files, not memory
4. **Dashboard editing** - Allow profile changes from website
5. **Live sync** - Real-time data between WhatsApp and website

## Step-by-Step Implementation:

### Phase 1: Fix Data Persistence (JSON File Storage)
- [ ] Update moneyview_agent.py to save/load from JSON files
- [ ] Create data folder structure
- [ ] Implement auto-save on every transaction/profile change

### Phase 2: Improve NLP Understanding
- [ ] Add more keyword patterns
- [ ] Handle common variations like "otp", "help", "status", "profile"
- [ ] Use OpenAI for smart understanding when keywords don't match
- [ ] Add fuzzy matching for commands

### Phase 3: Fix OTP Flow
- [ ] Make OTP sending work via Baileys
- [ ] Add debug logging
- [ ] Implement fallback mechanisms

### Phase 4: Dashboard Edit Features
- [ ] Add goal management endpoints
- [ ] Add income/expense editing
- [ ] Add profile update from dashboard
- [ ] Sync changes to WhatsApp conversation

### Phase 5: Testing & Deployment
- [ ] Test all flows
- [ ] Deploy to Railway
- [ ] Verify WhatsApp integration
