# 🥗 BulkMate — AI-Powered Nutrition Tracker

<div align="center">

![BulkMate Banner](https://img.shields.io/badge/BulkMate-AI%20Nutrition%20Partner-4ade80?style=for-the-badge&logo=leaf&logoColor=black)

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1.1-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+-4169E1?style=flat-square&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Gemini AI](https://img.shields.io/badge/Gemini-AI-8E75B2?style=flat-square&logo=google&logoColor=white)](https://ai.google.dev)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-CSS-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
[![PWA](https://img.shields.io/badge/PWA-Ready-5A0FC8?style=flat-square&logo=pwa&logoColor=white)](https://web.dev/progressive-web-apps)
[![Deploy](https://img.shields.io/badge/Deployed-Render-46E3B7?style=flat-square&logo=render&logoColor=white)](https://render.com)

**BulkMate** is a full-stack AI-powered nutrition tracking web application that helps users achieve their weight goals — whether gaining, maintaining, or losing weight — through smart meal logging, real-time calorie tracking, and an intelligent AI chat assistant.

[🌐 Live Demo](https://bulk-mate.onrender.com) · [🐛 Report Bug](https://github.com/charan-d11/BulkMate/issues) · [✨ Request Feature](https://github.com/charan-d11/BulkMate/issues)

</div>

---

## 📱 Screenshots

| Dashboard | AI Chat | Meal Logging |
|-----------|---------|--------------|
| Real-time calorie tracking | Goal-aware AI assistant | Smart nutrition calculator |

---

## ✨ Features

- 🤖 **AI-Powered Chat** — Context-aware Gemini AI that knows your goal, calorie target, and today's meals
- 🍽️ **Smart Meal Logging** — Type any food naturally (e.g. "250g chicken and rice") and get accurate nutrition data
- 📊 **Live Dashboard** — Real-time macros (calories, protein, carbs, fat) with progress bars and circular progress ring
- 🎯 **Personalized Goals** — Choose to gain, maintain, or lose weight — calorie targets auto-calculated using Harris-Benedict formula
- 🔑 **OTP Password Reset** — Secure forgot-password flow via SendGrid email with 6-digit OTP and 10-minute expiry
- 📱 **PWA Support** — Install as a mobile app on Android & iOS directly from the browser
- 🍔 **Hamburger Navigation** — Mobile-first responsive design with smooth sidebar animation
- 📅 **Meal History** — Every meal saved to PostgreSQL with full daily history
- 💬 **Persistent Chat** — AI remembers your entire conversation history across sessions
- ✏️ **Edit Profile** — Update name, weight, height, goal, and activity level anytime
- 🔒 **Secure Auth** — Bcrypt password hashing, Flask session management

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| **Python 3.11+** | Core language |
| **Flask 3.1** | Web framework |
| **Flask-SQLAlchemy** | ORM for database |
| **Flask-Bcrypt** | Password hashing |
| **PostgreSQL** | Production database |
| **Gunicorn** | Production WSGI server |

### AI & APIs
| Technology | Purpose |
|------------|---------|
| **Google Gemini 3.6 Flash** | AI chat + nutrition estimation |
| **SendGrid** | OTP email delivery |

### Frontend
| Technology | Purpose |
|------------|---------|
| **Tailwind CSS** | Utility-first styling |
| **Vanilla JavaScript** | Interactive UI |
| **Chart.js** | Data visualization |
| **PWA (manifest + service worker)** | Mobile app experience |

### Infrastructure
| Technology | Purpose |
|------------|---------|
| **Render** | Cloud hosting |
| **Render PostgreSQL** | Managed database |
| **GitHub** | Version control & CI/CD |

---

## 🗂️ Project Structure

```
BulkMate/
│
├── app/
│   ├── __init__.py              # App factory, DB & blueprint registration
│   ├── models.py                # SQLAlchemy models (User, Meal, ChatHistory)
│   ├── common/
│   │   ├── logger.py            # Daily rotating file logger
│   │   └── custom_exception.py  # Custom exception with file & line tracking
│   └── routes/
│       ├── auth.py              # Register, login, logout, onboarding, OTP
│       ├── chat.py              # AI chat with persistent history
│       ├── meals.py             # Meal CRUD + nutrition fetch
│       └── dashboard.py        # Dashboard + edit profile
│
├── static/
│   ├── manifest.json            # PWA manifest
│   ├── service-worker.js        # PWA service worker
│   └── icons/
│       ├── icon-192x192.png     # PWA icon (small)
│       └── icon-512x512.png     # PWA icon (large)
│
├── templates/
│   ├── index.html               # Landing page
│   ├── login.html               # Login page
│   ├── register.html            # Registration page
│   ├── onboarding.html          # Goal setup page
│   ├── dashboard.html           # Main dashboard
│   ├── chat.html                # AI chat interface
│   ├── forgot_password.html     # Forgot password
│   ├── verify_otp.html          # OTP verification
│   └── reset_password.html      # Password reset
│
├── logs/                        # Auto-generated daily log files
├── .env                         # Environment variables (never commit!)
├── .gitignore
├── config.py                    # App configuration class
├── run.py                       # App entry point
├── Procfile                     # Render/Heroku process file
├── requirements.txt             # Production dependencies
├── req.txt                      # Development dependencies
└── README.md
```

---

## 🗄️ Database Schema

```sql
-- User table
User {
  id             INTEGER PRIMARY KEY
  name           VARCHAR(100)
  email          VARCHAR(120) UNIQUE
  password       VARCHAR(200)        -- bcrypt hashed
  age            INTEGER
  weight         FLOAT               -- kg
  height         FLOAT               -- cm
  goal           VARCHAR(20)         -- 'gain' | 'maintain' | 'lose'
  activity_level FLOAT               -- 1.2 to 1.9 (activity multiplier)
  goal_calories  INTEGER             -- auto-calculated
  otp_code       VARCHAR(6)          -- 6-digit OTP
  otp_expiry     DATETIME            -- 10 min from sent
  otp_verified   BOOLEAN
}

-- Meal table
Meal {
  id        INTEGER PRIMARY KEY
  user_id   INTEGER FK → User.id
  date      DATE
  food_name VARCHAR(200)
  calories  FLOAT
  protein   FLOAT
  carbs     FLOAT
  fat       FLOAT
}

-- ChatHistory table
ChatHistory {
  id        INTEGER PRIMARY KEY
  user_id   INTEGER FK → User.id
  timestamp DATETIME
  role      VARCHAR(20)   -- 'user' | 'assistant'
  message   TEXT
}
```

---

## ⚙️ Local Setup

### Prerequisites
- Python 3.11+
- PostgreSQL 16+
- Git

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/BulkMate.git
cd BulkMate
```

### 2. Create virtual environment
```bash
python -m venv bulk
# Windows
bulk\Scripts\activate
# Mac/Linux
source bulk/bin/activate
```

### 3. Install dependencies
```bash
pip install -r req.txt
```

### 4. Create PostgreSQL database
```sql
CREATE DATABASE bulkmate;
```

### 5. Configure environment variables
Create a `.env` file in the root directory:
```env
# Flask
SECRET_KEY=your_super_secret_key_here
DEBUG=True

# Database
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/bulkmate

# Google Gemini AI
GEMINI_API_KEY=your_gemini_api_key

# SendGrid (for OTP emails)
SENDGRID_API_KEY=your_sendgrid_api_key
SENDER_EMAIL=your_verified_sender@gmail.com
```

### 6. Run the application
```bash
python run.py
```

Visit `http://127.0.0.1:5000` 🎉

---

## 🔑 API Keys Setup

### Google Gemini API (Free)
1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Click **Create API Key**
3. Copy key → paste as `GEMINI_API_KEY` in `.env`

### SendGrid API (Free — 100 emails/day)
1. Go to [SendGrid](https://sendgrid.com) → Sign up
2. Settings → **API Keys** → Create API Key (Full Access)
3. Settings → **Sender Authentication** → Verify your email
4. Copy key → paste as `SENDGRID_API_KEY` in `.env`

### Generate Flask Secret Key
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 🚀 Deployment (Render)

### 1. Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/charan-d11/BulkMate.git
git push -u origin main
```

### 2. Create PostgreSQL on Render
- Render Dashboard → **New +** → **PostgreSQL**
- Name: `bulkmate-db` → Plan: Free → Create
- Copy the **External Database URL**

### 3. Deploy Web Service
- Render Dashboard → **New +** → **Web Service**
- Connect GitHub → Select `BulkMate` repo
- Settings:
  ```
  Runtime    : Python 3
  Build cmd  : pip install -r requirements.txt
  Start cmd  : gunicorn run:app
  ```
- **Environment Variables** → Add all keys from `.env` + `DATABASE_URL`
- Click **Create Web Service**

### 4. Auto-deploy on push
```bash
git add .
git commit -m "your update"
git push
# Render auto-redeploys! ✅
```

---

## 📱 PWA Installation

### Android
1. Open Chrome → visit your BulkMate URL
2. Tap menu (⋮) → **Add to Home Screen**
3. Tap **Add** → BulkMate icon appears! 🎉

### iPhone
1. Open Safari → visit your BulkMate URL
2. Tap **Share** (□↑) → **Add to Home Screen**
3. Tap **Add** → BulkMate icon appears! 🎉

---

## 🧠 AI Features

### Goal-Aware Chat
The AI receives a system prompt with:
- User's name, age, weight, height
- Current goal (gain/maintain/lose)
- Daily calorie target
- Today's consumed calories & protein
- Full conversation history

### Smart Nutrition Calculation
- Gemini AI parses natural language food descriptions
- Understands quantities: "250g chicken", "3 eggs", "1 cup rice"
- Returns total values (not per 100g)
- Falls back gracefully on API errors with retry logic

### Harris-Benedict Formula
```
BMR = 10 × weight(kg) + 6.25 × height(cm) − 5 × age + 5
TDEE = BMR × activity_multiplier

Gain weight  → TDEE + 450 kcal
Maintain     → TDEE
Lose weight  → TDEE − 450 kcal
```

---

## 🔐 Security Features

- ✅ Bcrypt password hashing (cost factor 12)
- ✅ Flask session-based authentication
- ✅ OTP expiry (10 minutes)
- ✅ Environment variables for all secrets
- ✅ `.env` excluded from version control
- ✅ SQL injection prevention via SQLAlchemy ORM
- ✅ HTTPS enforced on Render

---

## 📝 Logging

BulkMate uses a custom logging system with daily rotating log files:

```
logs/
├── bulkmate_2026-09-01.log
├── bulkmate_2026-09-02.log
└── bulkmate_2026-09-03.log
```

Log entries include:
- User registrations and logins
- Meal additions and deletions
- AI chat interactions
- OTP generations
- Errors with file name and line number

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/AmazingFeature`
3. Commit your changes: `git commit -m 'Add AmazingFeature'`
4. Push to the branch: `git push origin feature/AmazingFeature`
5. Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## 👨‍💻 Author

**Durga Charan Mallick**

[![GitHub](https://img.shields.io/badge/GitHub-charan-d11-181717?style=flat-square&logo=github)](https://github.com/charan-d11)

---

## 🙏 Acknowledgements

- [Google Gemini AI](https://ai.google.dev) — AI chat and nutrition estimation
- [SendGrid](https://sendgrid.com) — Email OTP delivery
- [Render](https://render.com) — Cloud hosting platform
- [Tailwind CSS](https://tailwindcss.com) — UI styling
- [Flask](https://flask.palletsprojects.com) — Web framework

---

<div align="center">
  <strong>Built with 💪 for gainers, maintainers & losers alike</strong>
  <br/>
  <sub>BulkMate © 2026</sub>
</div>
