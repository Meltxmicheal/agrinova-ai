# 🌿 AgriNova AI — Smart Agriculture Platform

> AI-powered SaaS platform for precision agriculture — combining machine learning, real-time weather intelligence, and agronomic science to help farmers make data-driven decisions.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.1-green?logo=flask)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?logo=postgresql)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple?logo=bootstrap)
![scikit-learn](https://img.shields.io/badge/scikit--learn-ML-orange?logo=scikitlearn)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🎯 Features

### 🧠 Five AI Prediction Modules
| Module | Input | Output |
|--------|-------|--------|
| **Crop Recommendation** | NPK, pH, Temperature, Humidity, Rainfall | Best crop to cultivate |
| **Yield Prediction** | State, Crop, Season, Area, Rainfall, Temp | Predicted yield (tonnes) |
| **Disease Detection** | Leaf image upload | Disease class + treatment plan |
| **Fertilizer Recommendation** | Soil type, Crop, NPK, Moisture | Optimal fertilizer |
| **Market Price Prediction** | State, District, Commodity, Month | Predicted ₹/quintal price |

### 🌾 Farm Management
- Full CRUD operations for farm registration
- GPS geolocation capture
- Soil type classification
- Per-farm weather binding

### 🌤️ Weather Intelligence
- Real-time weather via OpenWeather API
- 7-day forecast per farm
- Automatic alert generation (heat waves, frost, heavy rain)
- Fallback mock data engine (never shows empty states)

### 📊 Reports & Analytics
- Export predictions, farms, and weather data as **CSV**, **Excel**, or **PDF**
- Dashboard with Chart.js doughnut visualization
- Recent AI prediction activity log

### 🔐 Authentication & Security
- JWT-based auth with access + refresh tokens
- Bcrypt password hashing
- Forgot/Reset password flow
- Route-level auth guards

---

## 🏗️ Architecture

```
┌────────────────────────────────────────────────────┐
│                  Frontend (Jinja2)                  │
│  HTML5 + CSS3 + Bootstrap 5 + JavaScript ES6       │
│  Glassmorphism Design System                       │
├────────────────────────────────────────────────────┤
│                  Flask Backend                      │
│  Blueprint Architecture + Service Layer Pattern    │
├──────┬──────┬──────┬──────┬──────┬──────┬──────────┤
│ Auth │ Farm │ Weather │ AI │ Crop │ Disease │ Reports│
├──────┴──────┴──────┴──────┴──────┴──────┴──────────┤
│            Repository Layer (SQLAlchemy)            │
├────────────────────────────────────────────────────┤
│               PostgreSQL Database                   │
├────────────────────────────────────────────────────┤
│        ML Inference Engine (scikit-learn)           │
│  5 Random Forest .pkl models                       │
└────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 14+
- Git

### 1. Clone & Setup

```bash
git clone https://github.com/your-username/agrinova-ai.git
cd agrinova-ai
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

pip install -r backend/requirements.txt
```

### 3. Configure Environment

Create a `.env` file in `backend/`:

```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/agrinova_db
SECRET_KEY=your-super-secret-key
OPENWEATHER_API_KEY=your_openweather_api_key  # Optional
```

### 4. Initialize Database

```bash
cd backend
createdb agrinova_db  # or create via pgAdmin
flask db upgrade
```

### 5. Train ML Models

```bash
python -c "from ml.train_model import train_all_models; train_all_models()"
```

### 6. Run Development Server

```bash
python run.py
```

Visit: **http://localhost:5000**

---

## 🐳 Docker Deployment

```bash
# Build & run with Docker Compose
docker-compose up --build -d

# View logs
docker-compose logs -f app
```

---

## 🌐 Render Deployment

1. Push to GitHub
2. Connect repo to [Render](https://render.com)
3. Use the included `render.yaml` Blueprint
4. Set `OPENWEATHER_API_KEY` in Render Environment

---

## 📁 Project Structure

```
AgriNova_AI/
├── backend/
│   ├── app/
│   │   ├── __init__.py          # App factory + blueprint registry
│   │   ├── extensions.py        # SQLAlchemy, Bcrypt, JWT, Migrate
│   │   ├── models/              # SQLAlchemy models
│   │   │   ├── user.py
│   │   │   ├── farm.py
│   │   │   ├── weather.py
│   │   │   └── prediction.py
│   │   ├── auth/                # Auth blueprint (routes/service/repository)
│   │   ├── farm/                # Farm CRUD blueprint
│   │   ├── weather/             # Weather intelligence blueprint
│   │   ├── crop/                # Crop recommendation blueprint
│   │   ├── disease/             # Disease detection blueprint
│   │   ├── ai/                  # Fertilizer AI blueprint
│   │   ├── prediction/          # Yield + Price prediction blueprint
│   │   ├── dashboard/           # Dashboard stats blueprint
│   │   └── reports/             # Report export blueprint
│   ├── config/
│   │   └── config.py            # Flask configuration
│   ├── ml/
│   │   ├── train_model.py       # ML model training
│   │   ├── predict.py           # ML inference service
│   │   └── models/              # Trained .pkl files
│   ├── migrations/              # Alembic migrations
│   ├── run.py                   # App entry point
│   └── requirements.txt
├── frontend/
│   ├── templates/               # Jinja2 HTML templates
│   │   ├── base.html
│   │   ├── _sidebar.html
│   │   ├── index.html           # Landing page
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── dashboard.html
│   │   ├── farms.html
│   │   ├── weather.html
│   │   ├── prediction.html      # All 5 AI modules
│   │   ├── reports.html
│   │   ├── profile.html
│   │   └── settings.html
│   └── static/
│       ├── css/style.css         # Glassmorphism design system
│       └── js/app.js             # Frontend controller (1178 lines)
├── tests/
│   └── test_api.py              # Integration test suite
├── postman/
│   └── AgriNova_AI_API.postman_collection.json
├── Dockerfile
├── docker-compose.yml
├── render.yaml
└── README.md
```

---

## 🧪 Testing

```bash
# Create test database
createdb agrinova_test_db

# Run integration tests
cd AgriNova_AI
python -m pytest tests/test_api.py -v
```

---

## 📬 API Endpoints (25+)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login and get tokens |
| GET | `/api/auth/profile` | Get user profile |
| POST | `/api/auth/forgot-password` | Generate reset token |
| POST | `/api/auth/reset-password` | Reset password |
| POST | `/api/auth/refresh` | Refresh access token |
| POST | `/api/auth/logout` | Logout |
| GET | `/api/farms/` | List all farms |
| POST | `/api/farms/` | Create farm |
| GET | `/api/farms/<id>` | Get single farm |
| PUT | `/api/farms/<id>` | Update farm |
| DELETE | `/api/farms/<id>` | Delete farm |
| GET | `/api/weather/` | Get farm weather |
| GET | `/api/weather/history` | Get weather history |
| POST | `/api/crop/recommend` | Crop recommendation |
| POST | `/api/prediction/yield` | Yield prediction |
| POST | `/api/prediction/price` | Market price prediction |
| POST | `/api/disease/detect` | Disease detection |
| POST | `/api/ai/fertilizer` | Fertilizer recommendation |
| GET | `/api/dashboard/stats` | Dashboard statistics |
| GET | `/api/reports/export` | Export reports (CSV/Excel/PDF) |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML5, CSS3, Bootstrap 5, JavaScript ES6, Jinja2 |
| Backend | Python 3.11, Flask, SQLAlchemy, Marshmallow |
| Database | PostgreSQL |
| ML | scikit-learn (Random Forest), Pillow, NumPy, Pandas |
| Auth | Flask-JWT-Extended, Flask-Bcrypt |
| Reports | ReportLab (PDF), OpenPyXL (Excel) |
| Weather | OpenWeather API + Fallback Engine |
| Deployment | Docker, Docker Compose, Render, Gunicorn |

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<p align="center">
  Built with ❤️ for Farmers — <strong>AgriNova AI</strong>
</p>
