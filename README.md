# Smart Expense Tracker 

Smart Expense Tracker Backend is a Flask-based personal finance management API designed to help users track income, expenses, loans, borrow/lend records, subscriptions, and financial health insights from one place.

This project is not just a basic expense tracker. It includes authentication, OTP verification, loan repayment tracking, borrow/lend management, subscription monitoring, dashboard analytics, and rule-based AI financial suggestions.

---

## Project Purpose

Many users track only expenses, but real personal finance also includes:

- Monthly income
- Category-wise spending
- Loan EMI pressure
- Borrowed and lent money
- Active subscriptions
- Upcoming payments
- Financial health score

This web app solves these problems by combining all these modules into one smart finance API.

---

## Key Features

### Authentication and Security

- User registration
- User login
- JWT-based authentication
- Logout using token blocklist
- OTP verification
- Resend OTP
- Forgot password
- Reset password
- Environment variable support using `.env`

---

### Frontend UI

- Responsive frontend using HTML, CSS, and JavaScript
- Register page
- OTP verification page
- Login page
- Forgot password page
- Reset password page
- Dashboard page
- Income page
- Expense page
- Loan page
- Borrow/Lend page
- Subscription page
- AI suggestions page
- Sidebar navigation
- Success and error messages
- Indian currency formatting
- Frontend API integration with backend
- Auto redirect if user is not logged in
- Auto refresh expired access token using refresh token

---

### Income Management

- Add income
- View all income records
- Update income
- Delete income
- Monthly income calculation

### Expense Management

- Add expense
- View all expenses
- Update expense
- Delete expense
- Category-wise expense tracking
- Monthly expense calculation

### Category Management

- Add custom categories
- Default categories after OTP verification
- Prevent duplicate categories per user

### Loan and EMI Management

- Add loan details
- View all loans
- Update loan
- Delete loan
- Track remaining loan amount
- Track monthly EMI
- Loan repayment system
- Automatically mark loan as completed after full repayment

### Borrow/Lend Management

- Track money borrowed from others
- Track money lent to others
- Add due date and notes
- Mark borrow/lend record as paid
- View pending borrow/lend records
- Dashboard summary for pending borrowed and lent amount

### Subscription Tracking

- Add subscriptions like Netflix, Spotify, Canva, ChatGPT, etc.
- Support for monthly, weekly, and yearly billing cycles
- Calculate estimated monthly subscription cost
- Track active subscriptions
- Show upcoming subscription renewals in the next 7 days

### Dashboard Analytics

The dashboard gives a complete financial overview, including:

- Total income
- Total expense
- Remaining balance
- Active loan count
- Completed loan count
- Total remaining loan amount
- Total monthly EMI
- Pending borrowed amount
- Pending lent amount
- Active subscription count
- Monthly subscription total
- Upcoming subscription count

### Monthly Report

The monthly report shows current month financial activity:

- Monthly income
- Monthly expense
- Monthly balance
- Monthly subscription total
- Monthly borrowed amount
- Monthly lent amount

### Rule-Based AI Financial Suggestions

The AI suggestion system analyzes user financial data and generates personalized insights such as:

- Overspending alert
- Low balance warning
- Good saving progress
- Highest spending category
- Loan repayment warning
- EMI due soon reminder
- Pending money to collect
- Pending money to return
- Subscription spending warning
- Emergency fund suggestion
- Financial health score

Example AI insight:

```json
{
  "type": "saving_suggestion",
  "priority": "low",
  "title": "Good Saving Progress",
  "message": "You saved 11,345 this month.",
  "action": "Move some money into an emergency fund or savings account."
}
```

---

## Tech Stack
**Backend**
- Python
- Flask
- PostgreSQL
- SQLAlchemy
- Flask-Migrate
- Flask-JWT-Extended
- Werkzeug Security
- Python Dotenv
- Postman
- Git and GitHub


**Frontend**
- HTML5
- CSS3
- JavaScript
- Fetch API
- LocalStorage

**Tools**
-GIT
-GIT HUB
-Postman
-VS Code
---


---
## Screenshots
<img width="1919" height="971" alt="Register Page" src="https://github.com/user-attachments/assets/e2080a76-704a-45e0-a092-d341f645ea22" />
<img width="1905" height="982" alt="Verify-otp-Page" src="https://github.com/user-attachments/assets/b86303d7-636b-41a0-b21e-bb5a6529dbdd" />
<img width="1920" height="970" alt="Login Page " src="https://github.com/user-attachments/assets/11208293-b3e9-4329-a3da-fbc18ccfbd34" />
<img width="1917" height="976" alt="Dashboard Page" src="https://github.com/user-attachments/assets/3a6131fd-366b-4a1d-b907-5aad3d3a6fdd" />
<img width="1914" height="976" alt="Loan Page" src="https://github.com/user-attachments/assets/1a657a71-677f-4834-8d83-1959d45353b0" />
<img width="1910" height="973" alt="Income Page" src="https://github.com/user-attachments/assets/6afc13b2-2dea-484a-b52a-724df0e02510" />
<img width="1920" height="972" alt="Expense Page" src="https://github.com/user-attachments/assets/d776198a-dc58-44e2-b35e-3e17ff6ce9be" />
<img width="1917" height="974" alt="Borrow or Lend Page" src="https://github.com/user-attachments/assets/6f39e7cc-6887-4e2d-8461-b5814182ab64" />
<img width="1918" height="973" alt="Subscription Page" src="https://github.com/user-attachments/assets/69a4a6f2-c013-4b46-8dac-f49f921a37a1" />
<img width="1920" height="977" alt="AI Suggestion Page" src="https://github.com/user-attachments/assets/7cb2615f-18d2-42b3-a376-ed78f705ad4d" />

---

---

## Frontend API Base URL

The frontend connects with the Flask backend using the API base URL defined in:


Simple meaning:

```text
frontend/js/script.js = location of code
http://127.0.0.1:5000 = local backend URL
```

## Authentication Flow

User registers
        ↓
OTP is generated
        ↓
User verifies OTP
        ↓
User logs in
        ↓
Backend returns access_token and refresh_token
        ↓
Frontend saves both tokens in localStorage
        ↓
Protected API calls use access_token
        ↓
If access_token expires, frontend uses refresh_token
        ↓
New access_token is generated
        ↓
User stays logged in
        ↓
Logout removes both tokens

---

---



## Project Structure

```text
smart-expense-tracker/
├── app.py
├── block.py
├── requirements.txt
├── README.md
├── .gitignore
├── dbms/
├── models/
├── routes/
├── utils/
├── migrations/
├── frontend/
└── screenshots/





## Environment Variables

Create a `.env` file in the root directory:

```env
DATABASE_URL=postgresql://username:password@localhost/dbname
JWT_SECRET_KEY=your-strong-jwt-secret-key
APP_ENV=development
```

---

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/imtiyaz-dev432/smart-expense-tracker.git
```

### 2. Move into the project folder

```bash
cd smart-expense-tracker
```

### 3. Create a virtual environment

```bash
python -m venv .venv
```

### 4. Activate the virtual environment

For Windows:

```bash
.venv\Scripts\activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Set up environment variables

Create a `.env` file and add your database URL and JWT secret key.

### 7. Run database migrations

```bash
flask db upgrade
```

### 8. Start the Flask server

```bash
python app.py
```

Server will run at:

```text
http://127.0.0.1:5000
```

---

## API Modules

### Auth APIs

```text
POST /auth/register
POST /auth/login
POST /auth/logout
POST /auth/refresh
```

### OTP APIs

```text
POST /otp/verify-otp
POST /otp/resend-otp
```

### Forgot Password APIs

```text
POST /forgot-password
POST /reset-password
```

### Income APIs

```text
POST /income/add
GET /income/all
PUT /income/update/<income_id>
DELETE /income/delete/<income_id>
```

### Expense APIs

```text
POST /expense
GET /expense/all
PUT /expense/update/<expense_id>
DELETE /expense/delete/<expense_id>
```

### Category APIs

```text
POST /category
```

### Dashboard APIs

```text
GET /dashboard
GET /dashboard/category-wise-expense
GET /dashboard/monthly-report
```

### Loan APIs

```text
POST /loan
GET /loan/get
PUT /loan/update/<loan_id>
DELETE /loan/delete/<loan_id>
POST /loan/repayment/<loan_id>
```

### Borrow/Lend APIs

```text
POST /borrow/add
GET /borrow/get
PUT /borrow/update/<borrow_id>
DELETE /borrow/delete/<borrow_id>
PUT /borrow/mark-paid/<borrow_id>
```

### Subscription APIs

```text
POST /subscription/add
GET /subscription/get
PUT /subscription/update/<subscription_id>
DELETE /subscription/delete/<subscription_id>
GET /subscription/upcoming
```

### AI Suggestion API

```text
GET /ai/suggestion
```

---

## Sample Dashboard Response

```json
{
  "total_income": 12000,
  "total_expense": 655,
  "balance": 11345,
  "pending_borrow_lend_count": 1,
  "pending_borrow_total": 0,
  "pending_lent_total": 1000,
  "total_loan_remaining": 215000,
  "total_monthly_emi": 5000,
  "active_loan_count": 1,
  "completed_loan_count": 0,
  "active_subscription_count": 2,
  "monthly_subscription_total": 899,
  "upcoming_subscription_count": 1
}
```

---

## Sample AI Suggestion Response

```json
{
  "summary": {
    "expense_ratio": "5.46%",
    "financial_health": "Good",
    "financial_health_score": 94,
    "total_income": "12,000",
    "total_expense": "655",
    "remaining_balance": "11,345"
  },
  "suggestions": [
    {
      "type": "saving_suggestion",
      "priority": "low",
      "title": "Good Saving Progress",
      "message": "You saved 11,345 this month.",
      "action": "Move some money into an emergency fund or savings account."
    },
    {
      "type": "active_loan_warning",
      "priority": "high",
      "title": "Active Loan Repayment",
      "message": "You have 1 active loan with total monthly EMI of 5,000.",
      "action": "Keep EMI money aside before spending on non-essential items."
    }
  ]
}
```

---

## Development Notes


- `.env` file is ignored using `.gitignore`.
- JWT token blocklist is used for logout.
- Flask-Migrate is used for database migrations.
- APIs are tested using Postman and Frontend.

---

## Future Scope

- Deployment on Render/Vercel
- Charts for dashboard analytics
- PDF monthly reports
- AI/ML-based expense prediction
---

## Project Status

```text
Backend: Completed
Frontend:Completed
Database: PostgreSQL
Authentication: JWT based
Testing: Completed using Postman and Browser
Deployment: Planned
```

---

## Author

**Mohommad Imtiyaz**

Python Backend Developer  
Flask | PostgreSQL | REST APIs | JavaScript | JWT | SQLAlchemy | GitHub
