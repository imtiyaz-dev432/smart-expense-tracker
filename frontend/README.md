# Smart Expense Tracker Frontend

This is a plain HTML, CSS, and basic JavaScript frontend for the Flask Smart Expense Tracker Backend.

## How to run

1. Start your Flask backend:
   ```bash
   python app.py
   ```

2. Open `index.html` in browser.

3. Register, verify OTP, login, and test dashboard pages.

## Notes

- API base URL is set in `js/script.js`:
  ```js
  const API_BASE_URL = "http://127.0.0.1:5000";
  ```
- JWT token is stored in `localStorage`.
- No React, Bootstrap, Tailwind, or external framework is used.
