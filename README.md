# Smart Complaint Prioritization Using AI

> **BCA Final Year College Project**
> An AI-powered civic complaint management system that automatically analyzes and prioritizes complaints using Natural Language Processing.

---

## 🚀 Project Overview

This full-stack web application allows citizens to submit civic complaints which are automatically analyzed by a custom NLP engine and assigned a **priority level** (Low / Medium / High / Critical) with a **score from 0 to 100**.

Administrators get a dedicated dashboard with analytics charts, complaint management, and real-time status updates.

---

## 🛠️ Tech Stack

| Layer       | Technology                          |
|-------------|--------------------------------------|
| Backend     | Python 3.x · Flask 3.0              |
| Database    | SQLite (via Python's `sqlite3`)     |
| Frontend    | HTML5 · CSS3 · Vanilla JavaScript   |
| Charts      | Chart.js 4.x                        |
| Icons       | Font Awesome 6.5                    |
| Fonts       | Google Fonts (Inter)                |
| AI / NLP    | Custom Python NLP Module (`model.py`)|
| Auth        | Flask Sessions · Werkzeug hashing   |
| Deployment  | Vercel                              |

---

## 📁 Project Structure

```
smart-complaint-prioritization/
├── app.py                     # Flask application & routes
├── model.py                   # AI prioritization engine
├── database.py                # SQLite DB helpers
├── requirements.txt
├── vercel.json                # Vercel deployment config
├── README.md
├── templates/
│   ├── index.html             # Landing page
│   ├── login.html
│   ├── register.html
│   ├── user_dashboard.html
│   ├── complaint_new.html     # Submit + live AI preview
│   ├── my_complaints.html
│   ├── complaint_details.html
│   ├── admin_dashboard.html   # Analytics + charts
│   ├── admin_complaints.html
│   ├── admin_users.html
│   ├── error.html
│   └── partials/
│       ├── _sidebar_user.html
│       └── _sidebar_admin.html
└── static/
    ├── css/style.css          # Full premium UI
    └── js/script.js           # All JS interactions
```

---

## ⚙️ Installation & Setup

### 1. Install Python Dependencies

```bash
# Create and activate a virtual environment (recommended)
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python app.py
```

This will:
- ✅ Initialize the SQLite database (`complaints.db`)
- ✅ Create the default admin account
- ✅ Start the development server on `http://localhost:5000`

### 3. Access the Application

| URL                        | Description         |
|----------------------------|---------------------|
| `http://localhost:5000/`   | Landing page        |
| `http://localhost:5000/register` | User registration |
| `http://localhost:5000/login`    | User/Admin login  |
| `http://localhost:5000/admin`    | Admin dashboard   |

---

## 👤 Default Admin Account

When you first run the app, a default admin account is created automatically:

| Field    | Value                        |
|----------|------------------------------|
| Email    | `admin@smartcomplaint.com`   |
| Password | `Admin@1234`                 |

> ⚠️ Change the admin password after your first login for security.

---

## 🤖 How the AI Priority Algorithm Works

The AI engine is in [`model.py`](model.py). It uses a **multi-factor weighted keyword scoring system**:

### Step-by-Step Process

1. **Text Normalization**
   - Combines complaint title + description
   - Converts to lowercase
   - Removes punctuation

2. **Keyword Scoring** (4 tiers)

   | Tier     | Score Contribution | Example Keywords |
   |----------|--------------------|-----------------|
   | Critical | +28 to +40 per keyword | fire, gas leak, building collapse, electrocution |
   | High     | +14 to +24 per keyword | water pipe burst, power failure, sewage overflow |
   | Medium   | +6 to +14 per keyword | garbage, streetlight, noise, road maintenance |
   | Low      | +2 to +5 per keyword | suggestion, inquiry, minor issue |

3. **Urgency Amplifier Detection**
   - Phrases like "please help", "very urgent", "immediately", "people are dying"
   - Adds up to 20 bonus points

4. **Detail Bonus**
   - Longer, more detailed complaints → slight score boost (realistic signal)

5. **Category Detection**
   - Scans text against 9 category keyword lists
   - Assigns the most matching category

6. **Category Multiplier**
   - Safety: ×1.20, Health: ×1.10, Security: ×1.05

7. **Score Clamping & Classification**

   | Score Range | Priority |
   |-------------|----------|
   | 81 – 100    | 🔴 Critical |
   | 61 – 80     | 🟠 High |
   | 31 – 60     | 🟡 Medium |
   | 0  – 30     | 🟢 Low |

### Test the AI Engine

```bash
python model.py
```

---

## 🌐 Deployment on Vercel

### Prerequisites
- [Vercel account](https://vercel.com)
- [Vercel CLI](https://vercel.com/cli): `npm i -g vercel`

### Steps

```bash
# Login to Vercel
vercel login

# Set the secret key environment variable
vercel env add SECRET_KEY
# Enter a strong random string when prompted

# Deploy
vercel --prod
```

> **Note:** Vercel's serverless functions are stateless. For production with persistent data, switch to a hosted database like PostgreSQL (Supabase or Railway) or use Vercel's KV storage.

---

## 🧪 Testing the System

### Test AI Prioritization

| Complaint Description | Expected Priority | Score Range |
|----------------------|-------------------|-------------|
| Gas leakage near houses, people can't breathe | Critical | 85–100 |
| Building collapse risk, families inside | Critical | 85–100 |
| Major water pipe burst flooding the road | High | 61–80 |
| Power failure in entire colony | High | 61–80 |
| Street light not working | Low–Medium | 10–30 |
| Garbage not collected for a week | Medium | 30–50 |
| Request for a park bench | Low | 5–20 |

### Test User Flow
1. Register as a new user
2. Submit a complaint with detailed description
3. Check AI priority assigned
4. View complaint details and score bar
5. Filter complaints by status/priority

### Test Admin Flow
1. Login as admin (`admin@smartcomplaint.com` / `Admin@1234`)
2. View dashboard analytics charts
3. See critical complaints sorted first
4. Change complaint status (Pending → In Progress → Resolved)
5. Search complaints by keyword
6. Delete a test complaint

---

## 🔒 Security Features

- ✅ Passwords hashed using **Werkzeug PBKDF2-SHA256**
- ✅ **Parameterized SQL queries** (no SQL injection)
- ✅ **Session-based authentication** with role checks
- ✅ Admin routes protected by `@admin_required` decorator
- ✅ Input validation on both client and server side
- ✅ Empty complaint prevention
- ✅ CSRF-safe form submissions

---

## 📊 Admin Analytics

The admin dashboard shows **4 interactive Chart.js charts**:

| Chart | Type | Description |
|-------|------|-------------|
| By Priority | Doughnut | Distribution across Critical/High/Medium/Low |
| By Status | Doughnut | Pending/In Progress/Resolved/Rejected |
| By Category | Bar | Complaints per civic category |
| Monthly Trend | Line | Last 6 months submission trend |

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Landing page |
| GET/POST | `/register` | User registration |
| GET/POST | `/login` | Login (user + admin) |
| GET | `/logout` | Logout |
| GET | `/dashboard` | User dashboard |
| GET/POST | `/complaint/new` | Submit complaint |
| GET | `/complaints` | My complaints list |
| GET | `/complaint/<id>` | Complaint details |
| GET | `/admin` | Admin dashboard |
| GET | `/admin/complaints` | All complaints |
| GET | `/admin/complaint/<id>` | Admin complaint view |
| POST | `/admin/update-status/<id>` | Update status |
| POST | `/admin/delete/<id>` | Delete complaint |
| GET | `/admin/users` | User list |
| **POST** | **`/api/analyze`** | **Live AI analysis (JSON)** |
| GET | `/api/stats` | Analytics data (JSON) |

---

## 🎓 Project Information

- **Project Name:** Smart Complaint Prioritization Using AI
- **Course:** BCA (Bachelor of Computer Applications)
- **Purpose:** Final Year Project Demonstration
- **Built With:** Python Flask · SQLite · Custom NLP · Chart.js

---

*Built with ❤️ for BCA Final Year Project*
