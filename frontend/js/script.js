console.log("COMMON SCRIPT LOADED");


  //  CONFIG

const API_BASE_URL = "http://127.0.0.1:5000";

const ENDPOINTS = {
  register: "/auth/register",
  verifyOtp: "/otp/verify-otp",
  resendOtp: "/otp/resend-otp",
  login: "/auth/login",

  forgotPassword: "/forgot-password",
  resetPassword: "/reset-password",

  dashboard: "/dashboard",
  monthlyReport: "/dashboard/monthly-report",
  categoryWiseExpense: "/dashboard/category-wise-expense",

  incomeAdd: "/income/add",
  incomeAll: "/income/all",
  incomeUpdate: "/income/update",
  incomeDelete: "/income/delete",
  aiSuggestion: "/ai/suggestion",
  expenseAdd: "/expense",
  expenseAll: "/expense/all",
  expenseUpdate: "/expense/update",
  expenseDelete: "/expense/delete",
  subscriptionAdd: "/subscription/add",
subscriptionAll: "/subscription/get",
subscriptionUpdate: "/subscription/update",
subscriptionDelete: "/subscription/delete",
subscriptionUpcoming: "/subscription/upcoming",
borrowAdd: "/borrow/add",
borrowAll: "/borrow/get",
borrowUpdate: "/borrow/update",
borrowDelete: "/borrow/delete",
borrowMarkPaid: "/borrow/mark-paid",

loanAdd: "/loan",
loanAll: "/loan/get",
loanUpdate: "/loan/update",
loanDelete: "/loan/delete",
loanRepayment: "/loan/repayment",
refresh: "/auth/refresh"
};

 
  //  COMMON HELPERS
 

function qs(selector) {
  return document.querySelector(selector);
}

function showMessage(id, message, type) {
  const messageBox = document.getElementById(id);

  if (!messageBox) {
    console.log(id + " not found");
    return;
  }

  messageBox.textContent = message;
  messageBox.className = "message show " + type;
}

function setText(id, value) {
  const element = document.getElementById(id);

  if (element) {
    element.textContent = value;
  }
}

function formatAmount(value) {
  const amount = Number(String(value || 0).replace(/,/g, ""));

  if (amount < 0) {
    return "-₹" + Math.abs(amount).toLocaleString("en-IN");
  }

  return "₹" + amount.toLocaleString("en-IN");
}

function setAmountText(id, value) {
  const element = document.getElementById(id);

  if (!element) {
    console.log("Element not found:", id);
    return;
  }

  const amount = Number(String(value || 0).replace(/,/g, ""));

  element.textContent = formatAmount(amount);

  if (amount < 0) {
    element.classList.add("negative-amount");
  } else {
    element.classList.remove("negative-amount");
  }
}

function getAccessToken() {
  return localStorage.getItem("access_token");
}

function getRefreshToken() {
  return localStorage.getItem("refresh_token");
}
function requireAuth() {
  const accessToken = getAccessToken();
  const refreshToken = getRefreshToken();

  if (!accessToken && !refreshToken) {
    window.location.href = "login.html";
  }
}

function saveTokens(accessToken, refreshToken) {
  localStorage.setItem("access_token", accessToken);
  localStorage.setItem("refresh_token", refreshToken);
}

function removeTokens() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
}


async function refreshAccessToken() {
  const refreshToken = getRefreshToken();

  if (!refreshToken) {
    removeTokens();
    window.location.href = "login.html";
    return null;
  }

  const response = await fetch(API_BASE_URL + ENDPOINTS.refresh, {
    method: "POST",
    headers: {
      "Authorization": "Bearer " + refreshToken
    }
  });

  const data = await response.json().catch(function () {
    return {};
  });

  if (!response.ok) {
    removeTokens();
    window.location.href = "login.html";
    return null;
  }

  localStorage.setItem("access_token", data.access_token);
  return data.access_token;
}




  //  API REQUESTS


async function apiRequest(endpoint, method, body) {
  const response = await fetch(API_BASE_URL + endpoint, {
    method: method,
    headers: {
      "Content-Type": "application/json"
    },
    body: body ? JSON.stringify(body) : null
  });

  const data = await response.json().catch(function () {
    return {};
  });

  if (!response.ok) {
    throw new Error(data.message || data.error || data.description || "Something went wrong");
  }

  return data;
}

async function authApiRequest(endpoint, method = "GET", body = null) {
  let token = getAccessToken();

  let response = await fetch(API_BASE_URL + endpoint, {
    method: method,
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + token
    },
    body: body ? JSON.stringify(body) : null
  });

  let data = await response.json().catch(function () {
    return {};
  });

  if (response.status === 401 || response.status === 422) {
    const newToken = await refreshAccessToken();

    if (!newToken) {
      throw new Error("Session expired. Please login again.");
    }

    response = await fetch(API_BASE_URL + endpoint, {
      method: method,
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + newToken
      },
      body: body ? JSON.stringify(body) : null
    });

    data = await response.json().catch(function () {
      return {};
    });
  }

  if (!response.ok) {
    throw new Error(data.message || data.error || data.description || "Something went wrong");
  }

  return data;
}


  //  PAGE DETECTION - IMPORTANT

document.addEventListener("DOMContentLoaded", function () {
  const page = document.body.dataset.page;

  console.log("Current page:", page);

  if (page === "register") {
    setupRegister();
  }

  if (page === "verify-otp") {
    setupOtp();
  }

  if (page === "login") {
    setupLogin();
  }

  if (page === "forgot") {
    setupForgotPassword();
  }

  if (page === "reset") {
    setupResetPassword();
  }

  if (page === "dashboard") {
    requireAuth();
    setupDashboard();
  }

  if (page === "income") {
  requireAuth();
  setupIncomePage();
  }
  if (page === "ai") {
  requireAuth();
  setupAiSuggestionsPage();
  }
  if (page === "expense") {
  requireAuth();
  setupExpensePage();
  }
  if (page === "subscription") {
  requireAuth();
  setupSubscriptionPage();
  }
  if (page === "borrow") {
  requireAuth();
  setupBorrowPage();}

  if (page === "loan") {
  requireAuth();
  setupLoanPage();
}



  

});


  //  REGISTER LOGIC


function setupRegister() {
  const registerForm = qs("#registerForm");

  if (!registerForm) {
    console.log("registerForm not found");
    return;
  }

  console.log("registerForm found");

  registerForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    console.log("REGISTER BUTTON CLICKED");

    const username = qs("#username").value.trim();
    const email = qs("#email").value.trim();
    const mobileNo = qs("#mobile_no").value.trim();
    const password = qs("#password").value;

    if (!username || !email || !mobileNo || !password) {
      showMessage("registerMessage", "All fields are required", "error");
      return;
    }

    try {
      const data = await apiRequest(ENDPOINTS.register, "POST", {
        username: username,
        email: email,
        mobile_no: mobileNo,
        password: password
      });

      localStorage.setItem("otp_mobile", mobileNo);

      showMessage(
        "registerMessage",
        data.message || "Registration successful. Redirecting to OTP page...",
        "success"
      );

      setTimeout(function () {
        window.location.href = "verify-otp.html";
      }, 1000);

    } catch (error) {
      showMessage("registerMessage", error.message, "error");
      console.log("Register error:", error);
    }
  });
}
//    VERIFY OTP LOGIC

function setupOtp() {
  console.log("setupOtp started");

  const mobileInput = qs("#mobile_no");
  const savedMobile = localStorage.getItem("otp_mobile");

  if (mobileInput && savedMobile) {
    mobileInput.value = savedMobile;
  }

  const otpForm = qs("#otpForm");

  if (!otpForm) {
    console.log("otpForm not found");
    return;
  }

  console.log("otpForm found");

  otpForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    console.log("VERIFY OTP BUTTON CLICKED");

    const mobileNo = qs("#mobile_no").value.trim();
    const otp = qs("#otp").value.trim();

    if (!mobileNo || !otp) {
      showMessage("otpMessage", "Mobile number and OTP are required", "error");
      return;
    }

    if (otp.length !== 6) {
      showMessage("otpMessage", "OTP must be 6 digits", "error");
      return;
    }

    try {
      const payload = {
        mobile_no: mobileNo,
        otp: otp,
        type: "register"
      };

      console.log("VERIFY OTP PAYLOAD:", payload);

      const data = await apiRequest(ENDPOINTS.verifyOtp, "POST", payload);

      console.log("VERIFY OTP RESPONSE:", data);

      localStorage.removeItem("otp_mobile");

      showMessage(
        "otpMessage",
        data.message || "OTP verified successfully. Redirecting to login...",
        "success"
      );

      setTimeout(function () {
        window.location.href = "login.html";
      }, 1000);

    } catch (error) {
      showMessage("otpMessage", error.message, "error");
      console.log("OTP error:", error);
    }
  });

  const resendOtpBtn = qs("#resendOtpBtn");

  if (!resendOtpBtn) {
    console.log("resendOtpBtn not found");
    return;
  }

  console.log("resendOtpBtn found");

  resendOtpBtn.addEventListener("click", async function () {
    console.log("RESEND OTP BUTTON CLICKED");

    const mobileNo = qs("#mobile_no").value.trim();

    if (!mobileNo) {
      showMessage("otpMessage", "Please enter mobile number first", "error");
      return;
    }

    try {
      const payload = {
        mobile_no: mobileNo,
        type: "register"
      };

      console.log("RESEND OTP PAYLOAD:", payload);

      const data = await apiRequest(ENDPOINTS.resendOtp, "POST", payload);

      console.log("RESEND OTP RESPONSE:", data);

      showMessage(
        "otpMessage",
        data.message || "OTP resent successfully",
        "success"
      );

    } catch (error) {
      showMessage("otpMessage", error.message, "error");
      console.log("Resend OTP error:", error);
    }
  });
}


        

//    LOGIN LOGIC
function setupLogin() {
  const loginForm = qs("#loginForm");

  if (!loginForm) {
    console.log("loginForm not found");
    return;
  }

  loginForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const username = qs("#username").value.trim();
    const password = qs("#password").value;

    if (!username || !password) {
      showMessage("loginMessage", "Username and password are required", "error");
      return;
    }

    try {
      const data = await apiRequest(ENDPOINTS.login, "POST", {
        username: username,
        password: password
      });

      console.log("LOGIN BACKEND RESPONSE:", data);

      const accessToken = data.access_token || data.token || data.accessToken || data.jwt;
      const refreshToken = data.refresh_token || data.refreshToken;

      if (!accessToken || !refreshToken) {
        showMessage("loginMessage", "Token not found. Check console.", "error");
        return;
      }

      saveTokens(accessToken, refreshToken);

      showMessage("loginMessage", "Login successful", "success");

      setTimeout(function () {
        window.location.href = "dashboard.html";
      }, 800);

    } catch (error) {
      showMessage("loginMessage", error.message, "error");
      console.log("Login error:", error);
    }
  });
}
     
    


  //  FORGOT PASSWORD LOGIC

function setupForgotPassword() {
  const forgotForm = qs("#forgotForm");

  if (!forgotForm) {
    console.log("forgotForm not found");
    return;
  }

  console.log("forgotForm found");

  forgotForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    console.log("SEND RESET OTP BUTTON CLICKED");

    const identifierInput = qs("#identifier");

    if (!identifierInput) {
      console.log("identifier input not found");
      showMessage("forgotMessage", "Identifier input missing in HTML", "error");
      return;
    }

    const identifier = identifierInput.value.trim();

    if (!identifier) {
      showMessage("forgotMessage", "Email or mobile number is required", "error");
      return;
    }

    try {
      const data = await apiRequest(ENDPOINTS.forgotPassword, "POST", {
        identifier: identifier
      });

      console.log("FORGOT PASSWORD RESPONSE:", data);

      localStorage.setItem("reset_identifier", identifier);

      showMessage(
        "forgotMessage",
        data.message || "Reset OTP sent successfully. Redirecting...",
        "success"
      );

      setTimeout(function () {
        window.location.href = "reset-password.html";
      }, 800);

    } catch (error) {
      showMessage("forgotMessage", error.message, "error");
      console.log("Forgot password error:", error);
    }
  });
}

/* 
   RESET PASSWORD LOGIC
 */

function setupResetPassword() {
  const identifierInput = qs("#identifier");
  const savedIdentifier = localStorage.getItem("reset_identifier");

  if (identifierInput && savedIdentifier) {
    identifierInput.value = savedIdentifier;
  }

  const resetForm = qs("#resetForm");

  if (!resetForm) {
    console.log("resetForm not found");
    return;
  }

  console.log("resetForm found");

  resetForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    console.log("RESET PASSWORD BUTTON CLICKED");

    const identifierInput = qs("#identifier");
    const otpInput = qs("#otp");
    const passwordInput = qs("#new_password");

    if (!identifierInput || !otpInput || !passwordInput) {
      console.log("reset input field missing");
      showMessage("resetMessage", "Input field missing in HTML", "error");
      return;
    }

    const identifier = identifierInput.value.trim();
    const otp = otpInput.value.trim();
    const newPassword = passwordInput.value;

    if (!identifier || !otp || !newPassword) {
      showMessage("resetMessage", "All fields are required", "error");
      return;
    }

    if (otp.length !== 6) {
      showMessage("resetMessage", "OTP must be 6 digits", "error");
      return;
    }

    try {
      const data = await apiRequest(ENDPOINTS.resetPassword, "POST", {
        identifier: identifier,
        otp: otp,
        new_password: newPassword
      });

      console.log("RESET PASSWORD RESPONSE:", data);

      localStorage.removeItem("reset_identifier");

      showMessage(
        "resetMessage",
        data.message || "Password reset successfully. Redirecting to login...",
        "success"
      );

      setTimeout(function () {
        window.location.href = "login.html";
      }, 1000);

    } catch (error) {
      showMessage("resetMessage", error.message, "error");
      console.log("Reset password error:", error);
    }
  });
}


  //  DASHBOARD LOGIC


function setupDashboard() {
  setupSidebarToggle();
  setupLogout();
  loadDashboardData();
}

async function loadDashboardData() {
  try {
    const dashboardData = await authApiRequest(ENDPOINTS.dashboard);

    setText("totalIncome", formatAmount(dashboardData.total_income));
    setText("totalExpense", formatAmount(dashboardData.total_expense));
    setAmountText("balance", dashboardData.balance);

    setText("loanRemaining", formatAmount(dashboardData.total_loan_remaining));
    setText("monthlyEmi", formatAmount(dashboardData.total_monthly_emi));

    setText("pendingBorrow", formatAmount(dashboardData.pending_borrow_total));
    setText("pendingLent", formatAmount(dashboardData.pending_lent_total));

    setText("subscriptionTotal", formatAmount(dashboardData.monthly_subscription_total));

    setText("activeLoans", dashboardData.active_loan_count || 0);
    setText("completedLoans", dashboardData.completed_loan_count || 0);
    setText("upcomingSubscriptions", dashboardData.upcoming_subscription_count || 0);

    const monthlyData = await authApiRequest(ENDPOINTS.monthlyReport);

    setText("monthlyIncome", formatAmount(monthlyData.monthly_income));
    setText("monthlyExpense", formatAmount(monthlyData.monthly_expense));
    setAmountText("monthlyBalance", monthlyData.monthly_balance);

    const categoryData = await authApiRequest(ENDPOINTS.categoryWiseExpense);

    renderCategoryList(categoryData.message || categoryData.category_wise_expense || {});

  } catch (error) {
    alert(error.message);
    console.log("Dashboard error:", error);
  }
}

function renderCategoryList(categoryData) {
  const categoryList = document.getElementById("categoryList");

  if (!categoryList) {
    return;
  }

  const entries = Object.entries(categoryData);

  if (entries.length === 0) {
    categoryList.innerHTML = `<p class="empty-text">No category expense found.</p>`;
    return;
  }

  categoryList.innerHTML = entries.map(function ([categoryName, amount]) {
    return `
      <div class="category-row">
        <span>${categoryName}</span>
        <strong>${formatAmount(amount)}</strong>
      </div>
    `;
  }).join("");
}

//    SIDEBAR + LOGOUT

function setupSidebarToggle() {
  const sidebarToggle = document.getElementById("sidebarToggle");
  const sidebar = document.getElementById("sidebar");

  if (!sidebarToggle || !sidebar) {
    return;
  }

  sidebarToggle.addEventListener("click", function () {
    sidebar.classList.toggle("open");
  });
}

function setupLogout() {
  const logoutBtn = document.getElementById("logoutBtn");

  if (!logoutBtn) {
    return;
  }

  logoutBtn.addEventListener("click", function () {
    const confirmLogout = confirm("Are you sure you want to logout?");

    if (!confirmLogout) {
      return;
    }

    removeTokens();

    alert("Logout successful!");

    window.location.href = "login.html";
  });
}

  //  INCOME PAGE LOGIC

function setupIncomePage() {
  setupSidebarToggle();
  setupLogout();
  setupIncomeForm();
  loadIncomeRecords();
}

function setupIncomeForm() {
  const incomeForm = qs("#incomeForm");

  if (!incomeForm) {
    console.log("incomeForm not found");
    return;
  }

  console.log("incomeForm found");

  incomeForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    console.log("ADD INCOME BUTTON CLICKED");

    const source = qs("#source").value.trim();
    const amount = Number(qs("#amount").value);
    const description = qs("#description").value.trim();

    if (!source || !amount) {
      showMessage("incomeMessage", "Source and amount are required", "error");
      return;
    }

    if (amount <= 0) {
      showMessage("incomeMessage", "Amount must be greater than 0", "error");
      return;
    }

    try {
      const data = await authApiRequest(ENDPOINTS.incomeAdd, "POST", {
        source: source,
        amount: amount,
        description: description
      });

      console.log("ADD INCOME RESPONSE:", data);

      showMessage(
        "incomeMessage",
        data.message || "Income added successfully",
        "success"
      );

      incomeForm.reset();

      loadIncomeRecords();

    } catch (error) {
      showMessage("incomeMessage", error.message, "error");
      console.log("Add income error:", error);
    }
  });
}

async function loadIncomeRecords() {
  const incomeTable = qs("#incomeTable");

  if (!incomeTable) {
    console.log("incomeTable not found");
    return;
  }

  try {
    const data = await authApiRequest(ENDPOINTS.incomeAll);

    console.log("INCOME RECORDS RESPONSE:", data);

    const records = data.income || data.incomes || data.message || [];

    if (!Array.isArray(records) || records.length === 0) {
      incomeTable.innerHTML = `
        <tr>
          <td colspan="6">No income records found.</td>
        </tr>
      `;
      return;
    }

    incomeTable.innerHTML = records.map(function (income) {
      return `
        <tr>
          <td>${income.id}</td>
          <td>${income.source || "-"}</td>
          <td>${formatAmount(income.amount)}</td>
          <td>${income.description || "-"}</td>
          <td>${formatDate(income.date)}</td>
          <td>
            <div class="action-buttons">
              <button class="edit-btn" onclick="editIncome(${income.id})">
                Edit
              </button>

              <button class="delete-btn" onclick="deleteIncome(${income.id})">
                Delete
              </button>
            </div>
          </td>
        </tr>
      `;
    }).join("");

  } catch (error) {
    incomeTable.innerHTML = `
      <tr>
        <td colspan="6">${error.message}</td>
      </tr>
    `;

    console.log("Load income error:", error);
  }
}

async function editIncome(id) {
  const source = prompt("Enter updated source:");
  const amount = prompt("Enter updated amount:");
  const description = prompt("Enter updated description:");

  if (!source || !amount) {
    alert("Source and amount are required");
    return;
  }

  if (Number(amount) <= 0) {
    alert("Amount must be greater than 0");
    return;
  }

  try {
    const data = await authApiRequest(`${ENDPOINTS.incomeUpdate}/${id}`, "PUT", {
      source: source,
      amount: Number(amount),
      description: description || ""
    });

    console.log("UPDATE INCOME RESPONSE:", data);

    alert(data.message || "Income updated successfully");

    loadIncomeRecords();

  } catch (error) {
    alert(error.message);
    console.log("Update income error:", error);
  }
}

async function deleteIncome(id) {
  const confirmDelete = confirm("Are you sure you want to delete this income?");

  if (!confirmDelete) {
    return;
  }

  try {
    const data = await authApiRequest(`${ENDPOINTS.incomeDelete}/${id}`, "DELETE");

    console.log("DELETE INCOME RESPONSE:", data);

    alert(data.message || "Income deleted successfully");

    loadIncomeRecords();

  } catch (error) {
    alert(error.message);
    console.log("Delete income error:", error);
  }
}

function formatDate(value) {
  if (!value) {
    return "-";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleDateString("en-IN");
}


/* 
   AI SUGGESTIONS PAGE LOGIC
 */

function setupAiSuggestionsPage() {
  setupSidebarToggle();
  setupLogout();
  loadAiSuggestions();
}

async function loadAiSuggestions() {
  const suggestionList = qs("#suggestionList");

  if (!suggestionList) {
    console.log("suggestionList not found");
    return;
  }

  try {
    const data = await authApiRequest(ENDPOINTS.aiSuggestion);

    console.log("AI SUGGESTIONS RESPONSE:", data);

    const summary = data.summary || {};
    const suggestions = data.suggestions || [];

    setText("healthScore", summary.financial_health_score || "-");
    setText("financialHealth", summary.financial_health || "-");
    setText("expenseRatio", summary.expense_ratio || "-");

    setText("aiIncome", summary.total_income || "-");
    setText("aiExpense", summary.total_expense || "-");
    setAmountText("aiBalance", summary.remaining_balance);

    if (!Array.isArray(suggestions) || suggestions.length === 0) {
      suggestionList.innerHTML = `
        <p class="empty-text">No AI suggestions found.</p>
      `;
      return;
    }

    suggestionList.innerHTML = suggestions.map(function (item) {
      const priority = item.priority || "low";

      return `
        <div class="ai-card ${priority}">
          <div class="ai-card-header">
            <h3>${item.title || "Suggestion"}</h3>
            <span class="priority-badge ${priority}">
              ${priority}
            </span>
          </div>

          <p class="ai-message">
            ${item.message || "-"}
          </p>

          <p class="ai-action">
            <strong>Action:</strong> ${item.action || "-"}
          </p>

          <p class="ai-type">
            Type: ${item.type || "-"}
          </p>
        </div>
      `;
    }).join("");

  } catch (error) {
    suggestionList.innerHTML = `
      <p class="empty-text">${error.message}</p>
    `;

    console.log("AI suggestion error:", error);
  }
}


/* 
   EXPENSE PAGE LOGIC
 */

function setupExpensePage() {
  setupSidebarToggle();
  setupLogout();
  setupExpenseForm();
  loadExpenseRecords();
}

function setupExpenseForm() {
  const expenseForm = qs("#expenseForm");

  if (!expenseForm) {
    console.log("expenseForm not found");
    return;
  }

  console.log("expenseForm found");

  expenseForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    console.log("ADD EXPENSE BUTTON CLICKED");

    const title = qs("#title").value.trim();
    const amount = Number(qs("#amount").value);
    const category = qs("#category").value.trim();
    const description = qs("#description").value.trim();

    if (!title || !amount || !category) {
      showMessage("expenseMessage", "Title, amount and category are required", "error");
      return;
    }

    if (amount <= 0) {
      showMessage("expenseMessage", "Amount must be greater than 0", "error");
      return;
    }

    try {
      const data = await authApiRequest(ENDPOINTS.expenseAdd, "POST", {
        title: title,
        amount: amount,
        category: category,
        description: description
      });

      console.log("ADD EXPENSE RESPONSE:", data);

      showMessage(
        "expenseMessage",
        data.message || "Expense added successfully",
        "success"
      );

      expenseForm.reset();

      loadExpenseRecords();

    } catch (error) {
      showMessage("expenseMessage", error.message, "error");
      console.log("Add expense error:", error);
    }
  });
}

async function loadExpenseRecords() {
  const expenseTable = qs("#expenseTable");

  if (!expenseTable) {
    console.log("expenseTable not found");
    return;
  }

  try {
    const data = await authApiRequest(ENDPOINTS.expenseAll);

    console.log("EXPENSE RECORDS RESPONSE:", data);

    const records = data.expenses || data.expense || data.message || [];

    if (!Array.isArray(records) || records.length === 0) {
      expenseTable.innerHTML = `
        <tr>
          <td colspan="7">No expense records found.</td>
        </tr>
      `;
      return;
    }

    expenseTable.innerHTML = records.map(function (expense) {
      return `
        <tr>
          <td>${expense.id}</td>
          <td>${expense.title || "-"}</td>
          <td>${formatAmount(expense.amount)}</td>
          <td>
            <span class="category-badge">
              ${expense.category || "-"}
            </span>
          </td>
          <td>${expense.description || "-"}</td>
          <td>${formatDate(expense.date)}</td>
          <td>
            <div class="action-buttons">
              <button class="edit-btn" onclick="editExpense(${expense.id})">
                Edit
              </button>

              <button class="delete-btn" onclick="deleteExpense(${expense.id})">
                Delete
              </button>
            </div>
          </td>
        </tr>
      `;
    }).join("");

  } catch (error) {
    expenseTable.innerHTML = `
      <tr>
        <td colspan="7">${error.message}</td>
      </tr>
    `;

    console.log("Load expense error:", error);
  }
}

async function editExpense(id) {
  const title = prompt("Enter updated title:");
  const amount = prompt("Enter updated amount:");
  const category = prompt("Enter updated category:");
  const description = prompt("Enter updated description:");

  if (!title || !amount || !category) {
    alert("Title, amount and category are required");
    return;
  }

  if (Number(amount) <= 0) {
    alert("Amount must be greater than 0");
    return;
  }

  try {
    const data = await authApiRequest(`${ENDPOINTS.expenseUpdate}/${id}`, "PUT", {
      title: title,
      amount: Number(amount),
      category: category,
      description: description || ""
    });

    console.log("UPDATE EXPENSE RESPONSE:", data);

    alert(data.message || "Expense updated successfully");

    loadExpenseRecords();

  } catch (error) {
    alert(error.message);
    console.log("Update expense error:", error);
  }
}

async function deleteExpense(id) {
  const confirmDelete = confirm("Are you sure you want to delete this expense?");

  if (!confirmDelete) {
    return;
  }

  try {
    const data = await authApiRequest(`${ENDPOINTS.expenseDelete}/${id}`, "DELETE");

    console.log("DELETE EXPENSE RESPONSE:", data);

    alert(data.message || "Expense deleted successfully");

    loadExpenseRecords();

  } catch (error) {
    alert(error.message);
    console.log("Delete expense error:", error);
  }
}


/* 
   SUBSCRIPTION PAGE LOGIC
 */

function setupSubscriptionPage() {
  setupSidebarToggle();
  setupLogout();
  setupSubscriptionForm();
  loadSubscriptionRecords();
  loadUpcomingSubscriptions();
}

function setupSubscriptionForm() {
  const subscriptionForm = qs("#subscriptionForm");

  if (!subscriptionForm) {
    console.log("subscriptionForm not found");
    return;
  }

  console.log("subscriptionForm found");

  subscriptionForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    console.log("ADD SUBSCRIPTION BUTTON CLICKED");

    const name = qs("#name").value.trim();
    const amount = Number(qs("#amount").value);
    const billingCycle = qs("#billing_cycle").value;
    const nextBillingDate = qs("#next_billing_date").value;
    const note = qs("#note").value.trim();

    if (!name || !amount || !billingCycle || !nextBillingDate) {
      showMessage(
        "subscriptionMessage",
        "Name, amount, billing cycle and next billing date are required",
        "error"
      );
      return;
    }

    if (amount <= 0) {
      showMessage("subscriptionMessage", "Amount must be greater than 0", "error");
      return;
    }

    try {
      const data = await authApiRequest(ENDPOINTS.subscriptionAdd, "POST", {
        name: name,
        amount: amount,
        billing_cycle: billingCycle,
        next_billing_date: nextBillingDate,
        note: note
      });

      console.log("ADD SUBSCRIPTION RESPONSE:", data);

      showMessage(
        "subscriptionMessage",
        data.message || "Subscription added successfully",
        "success"
      );

      subscriptionForm.reset();

      loadSubscriptionRecords();
      loadUpcomingSubscriptions();

    } catch (error) {
      showMessage("subscriptionMessage", error.message, "error");
      console.log("Add subscription error:", error);
    }
  });
}

async function loadSubscriptionRecords() {
  const subscriptionTable = qs("#subscriptionTable");

  if (!subscriptionTable) {
    console.log("subscriptionTable not found");
    return;
  }

  try {
    const data = await authApiRequest(ENDPOINTS.subscriptionAll);

    console.log("SUBSCRIPTION RECORDS RESPONSE:", data);

    const records =
      data.subscriptions ||
      data.subscription ||
      data.message ||
      [];

    if (!Array.isArray(records) || records.length === 0) {
      subscriptionTable.innerHTML = `
        <tr>
          <td colspan="8">No subscription records found.</td>
        </tr>
      `;
      return;
    }

    subscriptionTable.innerHTML = records.map(function (subscription) {
      const status = subscription.status || "active";

      return `
        <tr>
          <td>${subscription.id}</td>
          <td>${subscription.name || "-"}</td>
          <td>${formatAmount(subscription.amount)}</td>
          <td>
            <span class="cycle-badge">
              ${subscription.billing_cycle || "-"}
            </span>
          </td>
          <td>${formatDate(subscription.next_billing_date)}</td>
          <td>
            <span class="status-badge ${status}">
              ${status}
            </span>
          </td>
          <td>${subscription.note || "-"}</td>
          <td>
            <div class="action-buttons">
              <button class="edit-btn" onclick="editSubscription(${subscription.id})">
                Edit
              </button>

              <button class="delete-btn" onclick="deleteSubscription(${subscription.id})">
                Delete
              </button>
            </div>
          </td>
        </tr>
      `;
    }).join("");

  } catch (error) {
    subscriptionTable.innerHTML = `
      <tr>
        <td colspan="8">${error.message}</td>
      </tr>
    `;

    console.log("Load subscription error:", error);
  }
}

async function loadUpcomingSubscriptions() {
  const upcomingTable = qs("#upcomingSubscriptionTable");

  if (!upcomingTable) {
    console.log("upcomingSubscriptionTable not found");
    return;
  }

  try {
    const data = await authApiRequest(ENDPOINTS.subscriptionUpcoming);

    console.log("UPCOMING SUBSCRIPTION RESPONSE:", data);

    const records =
      data.upcoming_subscriptions ||
      data.subscriptions ||
      data.message ||
      [];

    if (!Array.isArray(records) || records.length === 0) {
      upcomingTable.innerHTML = `
        <tr>
          <td colspan="4">No upcoming subscriptions found.</td>
        </tr>
      `;
      return;
    }

    upcomingTable.innerHTML = records.map(function (subscription) {
      return `
        <tr>
          <td>${subscription.name || "-"}</td>
          <td>${formatAmount(subscription.amount)}</td>
          <td>
            <span class="cycle-badge">
              ${subscription.billing_cycle || "-"}
            </span>
          </td>
          <td>${formatDate(subscription.next_billing_date)}</td>
        </tr>
      `;
    }).join("");

  } catch (error) {
    upcomingTable.innerHTML = `
      <tr>
        <td colspan="4">${error.message}</td>
      </tr>
    `;

    console.log("Load upcoming subscription error:", error);
  }
}

async function editSubscription(id) {
  const name = prompt("Enter updated subscription name:");
  const amount = prompt("Enter updated amount:");
  const billingCycle = prompt("Enter billing cycle: weekly, monthly or yearly");
  const nextBillingDate = prompt("Enter next billing date YYYY-MM-DD:");
  const note = prompt("Enter updated note:");

  if (!name || !amount || !billingCycle || !nextBillingDate) {
    alert("Name, amount, billing cycle and next billing date are required");
    return;
  }

  if (Number(amount) <= 0) {
    alert("Amount must be greater than 0");
    return;
  }

  const allowedCycles = ["weekly", "monthly", "yearly"];

  if (!allowedCycles.includes(billingCycle.toLowerCase())) {
    alert("Billing cycle must be weekly, monthly or yearly");
    return;
  }

  try {
    const data = await authApiRequest(`${ENDPOINTS.subscriptionUpdate}/${id}`, "PUT", {
      name: name,
      amount: Number(amount),
      billing_cycle: billingCycle.toLowerCase(),
      next_billing_date: nextBillingDate,
      note: note || ""
    });

    console.log("UPDATE SUBSCRIPTION RESPONSE:", data);

    alert(data.message || "Subscription updated successfully");

    loadSubscriptionRecords();
    loadUpcomingSubscriptions();

  } catch (error) {
    alert(error.message);
    console.log("Update subscription error:", error);
  }
}

async function deleteSubscription(id) {
  const confirmDelete = confirm("Are you sure you want to delete this subscription?");

  if (!confirmDelete) {
    return;
  }

  try {
    const data = await authApiRequest(`${ENDPOINTS.subscriptionDelete}/${id}`, "DELETE");

    console.log("DELETE SUBSCRIPTION RESPONSE:", data);

    alert(data.message || "Subscription deleted successfully");

    loadSubscriptionRecords();
    loadUpcomingSubscriptions();

  } catch (error) {
    alert(error.message);
    console.log("Delete subscription error:", error);
  }
}


  //  BORROW / LEND PAGE LOGIC
 

function setupBorrowPage() {
  setupSidebarToggle();
  setupLogout();
  setupBorrowForm();
  loadBorrowRecords();
}

function setupBorrowForm() {
  const borrowForm = qs("#borrowForm");

  if (!borrowForm) {
    console.log("borrowForm not found");
    return;
  }

  console.log("borrowForm found");

  borrowForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    console.log("ADD BORROW/LEND BUTTON CLICKED");

    const personName = qs("#person_name").value.trim();
    const amount = Number(qs("#amount").value);
    const type = qs("#type").value;
    const dueDate = qs("#due_date").value;
    const note = qs("#note").value.trim();

    if (!personName || !amount || !type) {
      showMessage("borrowMessage", "Person name, amount and type are required", "error");
      return;
    }

    if (amount <= 0) {
      showMessage("borrowMessage", "Amount must be greater than 0", "error");
      return;
    }

    try {
      const data = await authApiRequest(ENDPOINTS.borrowAdd, "POST", {
        person_name: personName,
        amount: amount,
        type: type,
        due_date: dueDate,
        note: note
      });

      console.log("ADD BORROW/LEND RESPONSE:", data);

      showMessage(
        "borrowMessage",
        data.message || "Borrow/Lend record added successfully",
        "success"
      );

      borrowForm.reset();
      loadBorrowRecords();

    } catch (error) {
      showMessage("borrowMessage", error.message, "error");
      console.log("Add borrow/lend error:", error);
    }
  });
}

async function loadBorrowRecords() {
  const borrowTable = qs("#borrowTable");

  if (!borrowTable) {
    console.log("borrowTable not found");
    return;
  }

  try {
    const data = await authApiRequest(ENDPOINTS.borrowAll);

    console.log("BORROW/LEND RECORDS RESPONSE:", data);

    const records =
      data.borrows ||
      data.borrow_records ||
      data.records ||
      data.message ||
      [];

    if (!Array.isArray(records) || records.length === 0) {
      borrowTable.innerHTML = `
        <tr>
          <td colspan="8">No borrow/lend records found.</td>
        </tr>
      `;
      return;
    }

    borrowTable.innerHTML = records.map(function (item) {
      const type = item.type || "-";
      const status = item.status || "pending";

      return `
        <tr>
          <td>${item.id}</td>
          <td>${item.person_name || "-"}</td>
          <td>${formatAmount(item.amount)}</td>
          <td>
            <span class="type-badge ${type}">
              ${type}
            </span>
          </td>
          <td>${formatDate(item.due_date || item.due_datee)}</td>
          <td>
            <span class="status-badge ${status}">
              ${status}
            </span>
          </td>
          <td>${item.note || "-"}</td>
          <td>
            <div class="action-buttons">
              <button class="edit-btn" onclick="editBorrow(${item.id})">
                Edit
              </button>

              <button class="paid-btn" onclick="markBorrowPaid(${item.id})">
                Paid
              </button>

              <button class="delete-btn" onclick="deleteBorrow(${item.id})">
                Delete
              </button>
            </div>
          </td>
        </tr>
      `;
    }).join("");

  } catch (error) {
    borrowTable.innerHTML = `
      <tr>
        <td colspan="8">${error.message}</td>
      </tr>
    `;

    console.log("Load borrow/lend error:", error);
  }
}

async function editBorrow(id) {
  const personName = prompt("Enter updated person name:");
  const amount = prompt("Enter updated amount:");
  const type = prompt("Enter type: borrowed or lent");
  const dueDate = prompt("Enter due date YYYY-MM-DD:");
  const note = prompt("Enter updated note:");

  if (!personName || !amount || !type) {
    alert("Person name, amount and type are required");
    return;
  }

  if (Number(amount) <= 0) {
    alert("Amount must be greater than 0");
    return;
  }

  const allowedTypes = ["borrowed", "lent"];

  if (!allowedTypes.includes(type.toLowerCase())) {
    alert("Type must be borrowed or lent");
    return;
  }

  try {
    const data = await authApiRequest(`${ENDPOINTS.borrowUpdate}/${id}`, "PUT", {
      person_name: personName,
      amount: Number(amount),
      type: type.toLowerCase(),
      due_date: dueDate || "",
      note: note || ""
    });

    console.log("UPDATE BORROW/LEND RESPONSE:", data);

    alert(data.message || "Borrow/Lend record updated successfully");

    loadBorrowRecords();

  } catch (error) {
    alert(error.message);
    console.log("Update borrow/lend error:", error);
  }
}

async function markBorrowPaid(id) {
  const confirmPaid = confirm("Mark this record as paid?");

  if (!confirmPaid) {
    return;
  }

  try {
    const data = await authApiRequest(`${ENDPOINTS.borrowMarkPaid}/${id}`, "PUT");

    console.log("MARK BORROW/LEND PAID RESPONSE:", data);

    alert(data.message || "Record marked as paid");

    loadBorrowRecords();

  } catch (error) {
    alert(error.message);
    console.log("Mark paid error:", error);
  }
}

async function deleteBorrow(id) {
  const confirmDelete = confirm("Are you sure you want to delete this record?");

  if (!confirmDelete) {
    return;
  }

  try {
    const data = await authApiRequest(`${ENDPOINTS.borrowDelete}/${id}`, "DELETE");

    console.log("DELETE BORROW/LEND RESPONSE:", data);

    alert(data.message || "Record deleted successfully");

    loadBorrowRecords();

  } catch (error) {
    alert(error.message);
    console.log("Delete borrow/lend error:", error);
  }
}



  //  LOAN PAGE LOGIC


function setupLoanPage() {
  setupSidebarToggle();
  setupLogout();
  setupLoanForm();
  loadLoanRecords();
}

function setupLoanForm() {
  const loanForm = qs("#loanForm");

  if (!loanForm) {
    console.log("loanForm not found");
    return;
  }

  console.log("loanForm found");

  loanForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    console.log("ADD LOAN BUTTON CLICKED");

    const loanName = qs("#loan_name").value.trim();
    const totalAmount = Number(qs("#total_amount").value);
    const monthlyEmi = Number(qs("#monthly_emi").value);
    const remainingAmount = Number(qs("#remaining_amount").value);
    const dueDate = qs("#due_date").value;

    if (!loanName || !totalAmount || !monthlyEmi || remainingAmount === "" || !dueDate) {
      showMessage("loanMessage", "All fields are required", "error");
      return;
    }

    if (totalAmount <= 0) {
      showMessage("loanMessage", "Total amount must be greater than 0", "error");
      return;
    }

    if (monthlyEmi <= 0) {
      showMessage("loanMessage", "Monthly EMI must be greater than 0", "error");
      return;
    }

    if (remainingAmount < 0) {
      showMessage("loanMessage", "Remaining amount cannot be negative", "error");
      return;
    }

    if (remainingAmount > totalAmount) {
      showMessage(
        "loanMessage",
        "Remaining amount cannot be greater than total amount",
        "error"
      );
      return;
    }

    try {
      const data = await authApiRequest(ENDPOINTS.loanAdd, "POST", {
        loan_name: loanName,
        total_amount: totalAmount,
        monthly_emi: monthlyEmi,
        remaining_amount: remainingAmount,
        due_date: dueDate
      });

      console.log("ADD LOAN RESPONSE:", data);

      showMessage(
        "loanMessage",
        data.message || "Loan added successfully",
        "success"
      );

      loanForm.reset();
      loadLoanRecords();

    } catch (error) {
      showMessage("loanMessage", error.message, "error");
      console.log("Add loan error:", error);
    }
  });
}

async function loadLoanRecords() {
  const loanTable = qs("#loanTable");

  if (!loanTable) {
    console.log("loanTable not found");
    return;
  }

  try {
    const data = await authApiRequest(ENDPOINTS.loanAll);

    console.log("LOAN RECORDS RESPONSE:", data);

    const records =
      data.loans ||
      data.loan ||
      data.message ||
      [];

    if (!Array.isArray(records) || records.length === 0) {
      loanTable.innerHTML = `
        <tr>
          <td colspan="8">No loan records found.</td>
        </tr>
      `;
      return;
    }

    loanTable.innerHTML = records.map(function (loan) {
      const status = loan.status || "active";
      const totalAmount = loan.total_amount || loan.total_ammount || 0;
      const remainingAmount = loan.remaining_amount || 0;

      return `
        <tr>
          <td>${loan.id}</td>
          <td>${loan.loan_name || "-"}</td>
          <td>${formatAmount(totalAmount)}</td>
          <td>${formatAmount(loan.monthly_emi)}</td>
          <td>${formatAmount(remainingAmount)}</td>
          <td>${formatDate(loan.due_date)}</td>
          <td>
            <span class="status-badge ${status}">
              ${status}
            </span>
          </td>
          <td>
            <div class="action-buttons">
              <button class="edit-btn" onclick="editLoan(${loan.id}, ${totalAmount})">
                Edit
              </button>

              <button class="repay-btn" onclick="repayLoan(${loan.id}, ${remainingAmount})">
                Repay
              </button>

              <button class="delete-btn" onclick="deleteLoan(${loan.id})">
                Delete
              </button>
            </div>
          </td>
        </tr>
      `;
    }).join("");

  } catch (error) {
    loanTable.innerHTML = `
      <tr>
        <td colspan="8">${error.message}</td>
      </tr>
    `;

    console.log("Load loan error:", error);
  }
}

async function editLoan(id, totalAmount) {
  const loanName = prompt("Enter updated loan name:");
  const monthlyEmi = prompt("Enter updated monthly EMI:");
  const remainingAmount = prompt("Enter updated remaining amount:");
  const dueDate = prompt("Enter updated due date YYYY-MM-DD:");

  if (!loanName || !monthlyEmi || remainingAmount === null || !dueDate) {
    alert("All fields are required");
    return;
  }

  if (Number(monthlyEmi) <= 0) {
    alert("Monthly EMI must be greater than 0");
    return;
  }

  if (Number(remainingAmount) < 0) {
    alert("Remaining amount cannot be negative");
    return;
  }

  if (Number(remainingAmount) > Number(totalAmount)) {
    alert("Remaining amount cannot be greater than total amount");
    return;
  }

  try {
    const data = await authApiRequest(`${ENDPOINTS.loanUpdate}/${id}`, "PUT", {
      loan_name: loanName,
      monthly_emi: Number(monthlyEmi),
      remaining_amount: Number(remainingAmount),
      due_date: dueDate
    });

    console.log("UPDATE LOAN RESPONSE:", data);

    alert(data.message || "Loan updated successfully");

    loadLoanRecords();

  } catch (error) {
    alert(error.message);
    console.log("Update loan error:", error);
  }
}

async function repayLoan(id, remainingAmount) {
  const paidAmount = prompt("Enter paid amount:");

  if (!paidAmount) {
    alert("Paid amount is required");
    return;
  }

  if (Number(paidAmount) <= 0) {
    alert("Paid amount must be greater than 0");
    return;
  }

  if (Number(paidAmount) > Number(remainingAmount)) {
    alert("Paid amount cannot be greater than remaining amount");
    return;
  }

  try {
    const data = await authApiRequest(`${ENDPOINTS.loanRepayment}/${id}`, "POST", {
      paid_amount: Number(paidAmount)
    });

    console.log("LOAN REPAYMENT RESPONSE:", data);

    alert(data.message || "Repayment added successfully");

    loadLoanRecords();

  } catch (error) {
    alert(error.message);
    console.log("Loan repayment error:", error);
  }
}

async function deleteLoan(id) {
  const confirmDelete = confirm("Are you sure you want to delete this loan?");

  if (!confirmDelete) {
    return;
  }

  try {
    const data = await authApiRequest(`${ENDPOINTS.loanDelete}/${id}`, "DELETE");

    console.log("DELETE LOAN RESPONSE:", data);

    alert(data.message || "Loan deleted successfully");

    loadLoanRecords();

  } catch (error) {
    alert(error.message);
    console.log("Delete loan error:", error);
  }
}

function setupSidebarToggle() {
  const sidebarToggle = document.getElementById("sidebarToggle");
  const sidebar = document.getElementById("sidebar");

  if (!sidebarToggle || !sidebar) {
    return;
  }

  sidebarToggle.addEventListener("click", function () {
    sidebar.classList.toggle("open");
  })};
