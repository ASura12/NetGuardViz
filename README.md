# 🚀 NetGuardViz

**NetGuardViz** is a security-focused log analysis platform that ingests, processes, and monitors system logs to detect suspicious activity in real time. It converts raw logs into actionable alerts using automated pipelines, JWT authentication, and role-based access control.

---

## 🔥 Features

### 🛡️ Authentication & Security
- JWT-based authentication
- Role-Based Access Control (RBAC)
- Secure password hashing (bcrypt)

### 📂 Log Management
- Upload `.log`, `.txt`, `.json` files
- File validation (size, type, encoding)
- Background processing (non-blocking)

### 🚨 Threat Detection
- Keyword-based suspicious activity detection
- Automatic alert generation
- Alerts stored in MongoDB

### 📊 Data Handling
- Pagination for large datasets
- Filtering for logs and alerts
- Clean API responses

### 📢 Notifications
- Email alerts using SMTP

### 💻 Frontend
- React dashboard (Vite)
- Login with JWT storage
- Logs & Alerts table
- RBAC-based UI rendering

---

## 🏗️ Project Structure


---

## ⚙️ Tech Stack

- Backend: FastAPI  
- Database: MongoDB  
- Auth: JWT (python-jose)  
- Hashing: Passlib + bcrypt  
- Frontend: React (Vite)  

---

## 🔐 Authentication Flow

1. User Signup → Store hashed password  
2. Login → Verify credentials  
3. Generate JWT Token  
4. Access protected APIs using token  
5. RBAC restricts access by role  

---

## 🚀 Getting Started


### 1. Clone Repo
git clone https://github.com/ASura12/NetGuardViz.git

cd NetGuardViz

### 2. Create Virtual Environment
python -m venv venv
source venv/bin/activate

### 3. Install Dependencies
pip install -r requirements.txt

### 4. Setup Environment Variables
Create `.env` file:
MONGO_URI=your_mongodb_uri
SECRET_KEY=your_secret_key
ALGORITHM=HS256
EMAIL_USER=your_email
EMAIL_PASS=your_password

### 5. Run Server
uvicorn app.main:app --reload

---

## 📡 API Endpoints

### Auth
- POST `/auth/signup`
- POST `/auth/login`

### Logs
- POST `/api/logs/upload`
- GET `/api/logs?page=1&limit=20`

### Alerts
- GET `/api/alerts?page=1&limit=20`

---

## 🧠 Core Concepts

- Async background processing  
- JWT authentication  
- RBAC authorization  
- File validation pipeline  
- Alert generation system  

---

## 📌 Future Improvements

- Docker support  
- CI/CD pipeline  
- WebSocket real-time alerts  
- AI-based anomaly detection  

---

## 👨‍💻 Author

**Ashish Pathak**  
Cybersecurity | FastAPI | Backend Development
