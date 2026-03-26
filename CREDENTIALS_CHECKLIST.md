# Plurino — Credentials Checklist

**Location:** `/home/aipi/plurino-pro/`
**Status:** Built, 68/68 tests passing. Needs credentials to run.

Copy `.env.example` to `.env` and fill in below. Once done, run:
```bash
cd /home/aipi/plurino-pro
cp .env.example .env
# Edit .env with your values below
./start.sh
```

---

## ✅ What You Need to Create (All Free Tier)

### 1. Supabase — PostgreSQL Database
**Why:** Replaces ElephantSQL (better free tier, no expiry).
1. Go to https://supabase.com → Create project
2. Project Settings → Connection String → Copy **URI** (looks like `postgresql://postgres.xxxx:password@aws-0-eu-west-1.pooler.supabase.com:6543/postgres`)
3. Paste into `.env` as `DATABASE_URL`
4. Also add to `.env`:
   ```
   DATABASE_URL=postgresql://postgres.YOUR_ID:YOUR_PASSWORD@aws-0-eu-west-1.pooler.supabase.com:6543/postgres
   ```

### 2. Stripe — Payments (Test Mode)
**Why:** Accept payments, no live data needed yet.
1. Go to https://dashboard.stripe.com → Developers → API Keys
2. Copy **Publishable key** (starts with `pk_test_`) → `STRIPE_PUBLIC_KEY`
3. Copy **Secret key** (starts with `sk_test_`) → `STRIPE_SECRET_KEY`
4. For local testing: Webhooks → add `http://localhost:8000/checkout/webhook/` (or skip for now)
5. Get webhook signing secret (`whsec_...`) → `STRIPE_WEBHOOK_SECRET` (optional for dev)

### 3. Cloudflare R2 — File Storage (Optional, Skip for Now)
**Why:** S3-compatible, 5GB free. Skip until you have real image uploads.
```
USE_R2=False
# Leave the rest blank for now
```

---

## Full `.env` Template (Paste and Fill)

```bash
# Django
SECRET_KEY=your-secret-key-here-generate-with-pwgen-or-use-django.core.management.utils.get_random_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Supabase
DATABASE_URL=postgresql://postgres.YOUR_PROJECT_REF:YOUR_PASSWORD@aws-0-eu-west-1.pooler.supabase.com:6543/postgres

# Stripe TEST keys
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...   # optional for dev

# R2 — optional, set USE_R2=False for now
USE_R2=False

# E-Commerce
FREE_DELIVERY_THRESHOLD=80.00
STANDARD_DELIVERY_PERCENTAGE=15
```

---

## To Generate a Secret Key
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## After You Add Credentials

1. Run the dev server:
   ```bash
   cd /home/aipi/plurino-pro
   source venv/bin/activate
   python manage.py runserver 0.0.0.0:8000
   ```

2. Access at `http://YOUR_PI_IP:8000`

3. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```

4. Admin panel: `http://YOUR_PI_IP:8000/admin/`

---

## Accounts to Create

| Service | URL | Notes |
|---|---|---|
| Supabase | supabase.com | PostgreSQL database |
| Stripe | dashboard.stripe.com | Test mode keys only |
| Cloudflare R2 | cloudflare.com/r2 | Optional — skip for now |
