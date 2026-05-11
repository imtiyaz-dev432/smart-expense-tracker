# Smart Expense Tracker Backend

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

This backend solves these problems by combining all these modules into one smart finance API.

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

### Income Management

- Add income
- View all income records
- Update income
- Delete income
- Monthly income calculation

---

### Expense Management

- Add expense
- View all expenses
- Update expense
- Delete expense
- Category-wise expense tracking
- Monthly expense calculation

---

### Category Management

- Add custom categories
- Default categories after OTP verification
- Prevent duplicate categories per user

---

### Loan and EMI Management

- Add loan details
- View all loans
- Update loan
- Delete loan
- Track remaining loan amount
- Track monthly EMI
- Loan repayment system
- Automatically mark loan as completed after full repayment

---

### Borrow/Lend Management

- Track money borrowed from others
- Track money lent to others
- Add due date and notes
- Mark borrow/lend record as paid
- View pending borrow/lend records
- Dashboard summary for pending borrowed and lent amount

---

### Subscription Tracking

- Add subscriptions like Netflix, Spotify, Canva, ChatGPT, etc.
- Support for monthly, weekly, and yearly billing cycles
- Calculate estimated monthly subscription cost
- Track active subscriptions
- Show upcoming subscription renewals in the next 7 days

---

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

---

### Monthly Report

The monthly report shows current month financial activity:

- Monthly income
- Monthly expense
- Monthly balance
- Monthly subscription total
- Monthly borrowed amount
- Monthly lent amount

---

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
