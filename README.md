
# Zafipay — Multi-Provider Payment Gateway

> A production-grade payment infrastructure built for Kenya and the world. One unified API for M-Pesa, Airtel Money, Stripe, Flutterwave, and PayPal — with a full merchant dashboard and embeddable SDK.

![Zafipay Dashboard](https://img.shields.io/badge/status-production--ready-10B95A?style=flat-square)
![Django](https://img.shields.io/badge/Django-6.0-092E20?style=flat-square&logo=django)
![React](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=flat-square&logo=postgresql)
![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)

---

## What is Zafipay?

Zafipay is a self-hosted payment gateway that abstracts multiple African and global payment providers behind a single, consistent REST API. Instead of integrating M-Pesa, Stripe, and PayPal separately — merchants integrate Zafipay once and get access to all providers instantly.

Built as a portfolio-grade project demonstrating real-world fintech architecture: webhook delivery with exponential backoff, idempotent transactions, HMAC-signed payloads, JWT + API key dual authentication, and a complete React merchant dashboard.

---

## Supported Payment Providers

| Provider | Method | Region | Status |
|---|---|---|---|
| Safaricom M-Pesa | STK Push | Kenya | Sandbox + Production |
| Airtel Money | Mobile Money | Kenya | Code ready — awaiting approval |
| Stripe | Card payments | Global | Sandbox + Production |
| Flutterwave | Card + Mobile | Africa | Sandbox + Production |
| PayPal | PayPal wallet | Global | Sandbox + Production |

---

## Architecture
```
Zafipay/
├── backend/                  # Django REST Framework API
│   ├── apps/
│   │   ├── merchants/        # Auth, API keys, merchant profiles
│   │   ├── transactions/     # Payment initiation, state machine
│   │   ├── providers/        # M-Pesa, Airtel, Stripe, Flutterwave, PayPal adapters
│   │   ├── webhooks/         # Webhook delivery, Celery tasks, retries
│   │   ├── refunds/          # Refund processing per provider
│   │   └── audit/            # Immutable audit log
│   └── config/               # Settings (base/dev/prod), Celery, URLs
├── frontend/                 # React + TypeScript dashboard
│   └── src/
│       ├── pages/            # Dashboard, Transactions, Webhooks, API Keys, Refunds, Settings
│       ├── components/       # Layout, UI components
│       └── lib/              # API client (Axios), Auth context
└── sdk/                      # Embeddable JS SDK (coming soon)
```

---

## Tech Stack

### Backend
- **Django 6** + **Django REST Framework** — API layer
- **PostgreSQL** — Primary database with JSONB for provider metadata
- **Celery** + **Redis** — Async webhook delivery with exponential backoff
- **JWT** (SimpleJWT) + **API Key** authentication — dual auth system
- **django-environ** — Environment-based configuration

### Frontend
- **React 19** + **TypeScript** — Type-safe UI
- **Vite** — Fast build tooling
- **TanStack Query** — Server state management
- **Recharts** — Analytics charts
- **React Router** — Client-side routing
- **Tailwind CSS** — Utility-first styling

---

## Key Features

### For Merchants
- **Unified payment API** — one endpoint for all providers
- **Real-time webhooks** — HMAC-signed event delivery with automatic retries
- **Test / Live mode** — switch instantly with no code changes
- **API key management** — scoped keys with `sk_test_` and `sk_live_` prefixes
- **Transaction history** — full audit trail with status events
- **Refund management** — per-provider refund processing
- **Merchant dashboard** — dark-themed React UI with analytics

### For Developers (SDK integration)
```javascript
// Drop-in script tag
<script src="https://cdn.zafipay.com/sdk.js"></script>

// Or npm
npm install zafipay

// Initiate a payment
const zafipay = new Zafipay('pk_test_your_key')
zafipay.pay({
  amount: 100,
  currency: 'KES',
  provider: 'mpesa',
  phone: '254700000000',
  reference: 'ORDER-001',
  onSuccess: (data) => console.log('Paid!', data),
  onError: (err) => console.error(err),
})
```

### For Platform Builders
Any existing system can integrate Zafipay instead of building their own payment infrastructure:
```bash
# Initiate payment
curl -X POST https://api.zafipay.com/api/v1/transactions/initiate/ \
  -H "Authorization: Bearer sk_test_your_key" \
  -H "Content-Type: application/json" \
  -d '{"provider":"mpesa","amount":100,"currency":"KES","phone":"254700000000","reference":"ORDER-001"}'

# Response
{
  "success": true,
  "transaction_id": "uuid",
  "checkout_request_id": "ws_CO_...",
  "message": "Payment initiated. Please complete on your phone."
}
```

---

## Transaction State Machine
```
PENDING → PROCESSING → COMPLETED
                    → FAILED
COMPLETED → REFUNDED
```

Every transition is recorded in `transaction_events` with before/after state, and triggers webhook delivery to subscribed endpoints.

---

## Webhook System

Webhooks are delivered asynchronously via Celery with exponential backoff:

| Attempt | Delay |
|---|---|
| 1 | Immediate |
| 2 | 30 seconds |
| 3 | 5 minutes |
| 4 | 30 minutes |
| 5 | 2 hours |
| 6 | 24 hours |

All payloads are signed with HMAC-SHA256:
```
X-Zafipay-Signature: sha256=...
X-Zafipay-Event: transaction.completed
X-Zafipay-Delivery: uuid
```

---

## API Endpoints

### Authentication
```
POST /api/v1/merchants/register/
POST /api/v1/merchants/login/
POST /api/v1/merchants/token/refresh/
GET  /api/v1/merchants/profile/
POST /api/v1/merchants/mode/toggle/
```

### API Keys
```
GET  /api/v1/merchants/api-keys/
POST /api/v1/merchants/api-keys/
POST /api/v1/merchants/api-keys/{id}/revoke/
```

### Transactions
```
POST /api/v1/transactions/initiate/
GET  /api/v1/transactions/
GET  /api/v1/transactions/{id}/
```

### Webhooks
```
GET  /api/v1/webhooks/endpoints/
POST /api/v1/webhooks/endpoints/
DEL  /api/v1/webhooks/endpoints/{id}/
GET  /api/v1/webhooks/deliveries/
POST /api/v1/webhooks/deliveries/{id}/retry/
```

### Refunds
```
POST /api/v1/refunds/initiate/
GET  /api/v1/refunds/
GET  /api/v1/refunds/{id}/
```

### Provider Callbacks (public)
```
POST /api/v1/providers/mpesa/callback/
POST /api/v1/providers/airtel/callback/
POST /api/v1/providers/stripe/webhook/
POST /api/v1/providers/flutterwave/webhook/
POST /api/v1/providers/paypal/webhook/
```

---

## Local Development Setup

### Prerequisites
- Python 3.11+
- Node.js 20+
- PostgreSQL 15+
- Redis (or Memurai on Windows)
- Ngrok (for M-Pesa callbacks)

### Backend Setup
```bash
# Clone the repo
git clone https://github.com/DevKenya1/Zafipay.git
cd Zafipay/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements/base.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Set up database
createdb zafipay_db
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start server
python manage.py runserver
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Celery Worker (for webhooks)
```bash
cd backend
celery -A config worker --loglevel=info --pool=solo  # Windows
celery -A config worker --loglevel=info               # Linux/Mac
```

### Ngrok (for M-Pesa callbacks)
```bash
ngrok http 8000
# Update MPESA_CALLBACK_URL in .env with your ngrok URL
```

---

## Environment Variables

Copy `backend/.env.example` and fill in your values:
```env
# Django
DJANGO_SETTINGS_MODULE=config.settings.development
SECRET_KEY=your-secret-key
DEBUG=True

# Database
DB_NAME=zafipay_db
DB_USER=zafipay_user
DB_PASSWORD=zafipay_pass
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# M-Pesa (Safaricom Daraja)
MPESA_CONSUMER_KEY=
MPESA_CONSUMER_SECRET=
MPESA_SHORTCODE=174379
MPESA_PASSKEY=
MPESA_CALLBACK_URL=https://your-ngrok-url/api/v1/providers/mpesa/callback/
MPESA_ENV=sandbox

# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Flutterwave
FLUTTERWAVE_SECRET_KEY=FLWSECK_TEST-...
FLUTTERWAVE_PUBLIC_KEY=FLWPUBK_TEST-...
FLUTTERWAVE_WEBHOOK_SECRET=

# PayPal
PAYPAL_CLIENT_ID=
PAYPAL_CLIENT_SECRET=
PAYPAL_ENV=sandbox

# Airtel
AIRTEL_CLIENT_ID=
AIRTEL_CLIENT_SECRET=
AIRTEL_ENV=sandbox
```

---

## Sandbox Credentials for Testing

The sandbox passkey for Safaricom Daraja is publicly available:
```
Shortcode: 174379
Passkey: bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919
```

Register at:
- M-Pesa: https://developer.safaricom.co.ke
- Stripe: https://dashboard.stripe.com
- Flutterwave: https://dashboard.flutterwave.com
- PayPal: https://developer.paypal.com
- Airtel: https://developers.airtel.africa

---

## Production Deployment

When moving to production:

1. Set `DEBUG=False` and update `ALLOWED_HOSTS`
2. Replace all sandbox credentials with live credentials
3. Set a strong `SECRET_KEY`
4. Configure a production WSGI server (Gunicorn)
5. Set up SSL (required by Daraja and Stripe)
6. Use a managed Redis and PostgreSQL service

Recommended hosting: **Railway**, **Render**, or **DigitalOcean App Platform** — all have free tiers for testing.

---

## Roadmap

- [ ] Airtel Money — activate once credentials approved
- [ ] SDK npm package + script tag
- [ ] Merchant registration UI
- [ ] Transaction analytics with date filters
- [ ] Multi-currency support
- [ ] Team members / sub-accounts
- [ ] Rate limiting per API key
- [ ] Docker + docker-compose setup
- [ ] GitHub Actions CI/CD pipeline

---

## Project Structure (detailed)
```
backend/apps/providers/
├── base.py           # Abstract PaymentProvider class
├── mpesa.py          # Safaricom Daraja STK Push
├── airtel.py         # Airtel Africa Money
├── stripe_provider.py # Stripe PaymentIntents
├── flutterwave.py    # Flutterwave Hosted Payments
├── paypal.py         # PayPal Orders v2
├── router.py         # Provider factory — get_provider('mpesa')
└── views.py          # Callback/webhook receiver endpoints
```

Adding a new provider takes less than 100 lines — implement the `PaymentProvider` abstract class and register it in `router.py`.

---

## Author

Built by **Emmanuel Jesse** (Code Tech)
- GitHub: [@DevKenya1](https://github.com/DevKenya1)

---

## License

MIT License — free to use, modify, and distribute.
