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
  expenseAdd: "/expense/add",
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

loanAdd: "/loan/add",
loanAll: "/loan/get",
loanUpdate: "/loan/update",
loanDelete: "/loan/delete",
loanRepayment: "/loan/repayment",
refresh: "/auth/refresh",
logout: "/auth/logout"
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
function createSafeCell(text) {
  const td = document.createElement("td");
  td.textContent = text ?? "-";   // textContent is safe
  return td;
}

function createBadgeCell(badgeClass, text) {
  const td = document.createElement("td");
  const badge = document.createElement("span");
  badge.className = badgeClass;
  badge.textContent = text || "-";
  td.appendChild(badge);
  return td;
}

function createStatusBadgeCell(status) {
  // status also lands in a class name -> sanitize it
  const safe = String(status || "active").replace(/[^a-z0-9-]/gi, "");
  return createBadgeCell("status-badge " + safe, status || "active");
}

function createActionButton(label, cssClass, handler) {
  const btn = document.createElement("button");
  btn.className = cssClass;
  btn.textContent = label;
  btn.addEventListener("click", handler);
  return btn;
}

function createActionsCell(buttons) {
  const td = document.createElement("td");
  const div = document.createElement("div");
  div.className = "action-buttons";
  buttons.forEach(function (b) { div.appendChild(b); });
  td.appendChild(div);
  return td;
}

function renderEmptyRow(table, colspan, text) {
  const tr = document.createElement("tr");
  const td = document.createElement("td");
  td.colSpan = colspan;
  td.textContent = text;
  tr.appendChild(td);
  table.appendChild(tr);
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
        type: "verification"
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
     
// FORGOT PASSWORD LOGIC

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

    // Identify whether input is email or mobile number
    const payload = identifier.includes("@")
      ? { email: identifier }
      : { mobile_no: identifier };

    try {
      const data = await apiRequest(
        ENDPOINTS.forgotPassword,
        "POST",
        payload
      );

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

    // Read input values
    const identifier = identifierInput.value.trim();
    const otp = otpInput.value.trim();
    const newPassword = passwordInput.value;

    // Validate required fields
    if (!identifier || !otp || !newPassword) {
      showMessage("resetMessage", "All fields are required", "error");
      return;
    }

    // Validate OTP
    if (!/^\d{6}$/.test(otp)) {
      showMessage("resetMessage", "OTP must be 6 digits", "error");
      return;
    }

    // Identify email or mobile number
    const identifierPayload = identifier.includes("@")
      ? { email: identifier }
      : { mobile_no: identifier };

    try {
      const data = await apiRequest(
        ENDPOINTS.resetPassword,
        "POST",
        {
          ...identifierPayload,
          otp: otp,
          new_password: newPassword
        }
      );

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
    categoryList.replaceChildren();
    const p = document.createElement("p");
    p.className = "empty-text";
    p.textContent = "No category expense found.";
    categoryList.appendChild(p);
    return;
  }

  categoryList.replaceChildren();
  entries.forEach(function ([categoryName, amount]) {
    const row = document.createElement("div");
    row.className = "category-row";

    const span = document.createElement("span");
    span.textContent = categoryName;
    row.appendChild(span);

    const strong = document.createElement("strong");
    strong.textContent = formatAmount(amount);
    row.appendChild(strong);

    categoryList.appendChild(row);
  });
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

async function setupLogout() {
    const logoutBtn = document.getElementById("logoutBtn");

    if (!logoutBtn) {
        return;
    }

    logoutBtn.addEventListener("click", async function () {
        const confirmLogout = confirm("Are you sure you want to logout?");

        if (!confirmLogout) {
            return;
        }

        const refreshToken = getRefreshToken();
        const accessToken = getAccessToken();

        let serverLogoutSuccess = false;

        try {
            if (refreshToken) {
                const response = await fetch(
                    API_BASE_URL + ENDPOINTS.logout,
                    {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                            "Authorization": `Bearer ${refreshToken}`
                        },
                        body: JSON.stringify({
                            access_token: accessToken
                        })
                    }
                );

                if (!response.ok) {
                    throw new Error("Server-side logout failed");
                }

                serverLogoutSuccess = true;
            }

        } catch (error) {
            console.error("Logout error:", error);

        } finally {
            removeTokens();
            window.location.href = "login.html";
        }

        if (!serverLogoutSuccess) {
            alert(
                "You have been logged out locally, but server-side token revocation could not be confirmed."
            );
        }
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
      incomeTable.replaceChildren();
      renderEmptyRow(incomeTable, 6, "No income records found.");
      return;
    }

    incomeTable.replaceChildren();

    records.forEach(function (income) {
      const tr = document.createElement("tr");

      tr.appendChild(createSafeCell(income.id));
      tr.appendChild(createSafeCell(income.source));
      tr.appendChild(createSafeCell(formatAmount(income.amount)));
      tr.appendChild(createSafeCell(income.description));
      tr.appendChild(createSafeCell(formatDate(income.date)));

      tr.appendChild(createActionsCell([
        createActionButton("Edit", "edit-btn", function () { editIncome(income.id); }),
        createActionButton("Delete", "delete-btn", function () { deleteIncome(income.id); })
      ]));

      incomeTable.appendChild(tr);
    });

  } catch (error) {
    incomeTable.replaceChildren();
    renderEmptyRow(incomeTable, 6, error.message);
  
    console.log("Load income error:", error);
  }
}


async function editIncome(id) {
  const source = prompt("Enter updated source (leave blank to keep unchanged):");

  if (source === null) {
    return;
  }

  const amount = prompt("Enter updated amount (leave blank to keep unchanged):");

  if (amount === null) {
    return;
  }

  const description = prompt("Enter updated description (leave blank to keep unchanged):");

  if (description === null) {
    return;
  }

  // Build payload only with fields that need updating
  const payload = {};

  if (source.trim()) {
    payload.source = source.trim();
  }

  if (amount.trim()) {
    const numericAmount = Number(amount);

    if (!Number.isFinite(numericAmount) || numericAmount <= 0) {
      alert("Amount must be a valid number greater than 0");
      return;
    }

    payload.amount = numericAmount;
  }

  if (description.trim()) {
    payload.description = description.trim();
  }

  if (Object.keys(payload).length === 0) {
    alert("Please provide at least one field to update");
    return;
  }

  if (payload.description && payload.description.length > 200) {
    alert("Description cannot exceed 200 characters");
    return;
  }

  try {
    const data = await authApiRequest(
      `${ENDPOINTS.incomeUpdate}/${id}`,
      "PATCH",
      payload
    );

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
      suggestionList.replaceChildren();
      const p = document.createElement("p");
      p.className = "empty-text";
      p.textContent = "No AI suggestions found.";
      suggestionList.appendChild(p);
      return;
    }

    suggestionList.replaceChildren();

    suggestions.forEach(function (item) {
      const priority = item.priority || "low";
      const safePriority = String(priority).replace(/[^a-z0-9-]/gi, "");

      const card = document.createElement("div");
      card.className = "ai-card " + safePriority;

      const header = document.createElement("div");
      header.className = "ai-card-header";

      const h3 = document.createElement("h3");
      h3.textContent = item.title || "Suggestion";
      header.appendChild(h3);

      const priorityBadge = document.createElement("span");
      priorityBadge.className = "priority-badge " + safePriority;
      priorityBadge.textContent = priority;
      header.appendChild(priorityBadge);

      card.appendChild(header);

      const message = document.createElement("p");
      message.className = "ai-message";
      message.textContent = item.message || "-";
      card.appendChild(message);

      const action = document.createElement("p");
      action.className = "ai-action";
      const actionLabel = document.createElement("strong");
      actionLabel.textContent = "Action:";
      action.appendChild(actionLabel);
      action.appendChild(document.createTextNode(" " + (item.action || "-")));
      card.appendChild(action);

      const type = document.createElement("p");
      type.className = "ai-type";
      type.textContent = "Type: " + (item.type || "-");
      card.appendChild(type);

      suggestionList.appendChild(card);
    });

  } catch (error) {
    suggestionList.replaceChildren();
    const p = document.createElement("p");
    p.className = "empty-text";
    p.textContent = error.message;
    suggestionList.appendChild(p);
  
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
      expenseTable.replaceChildren();
      renderEmptyRow(expenseTable, 7, "No expense records found.");
      return;
    }

    expenseTable.replaceChildren(); // clear old rows

    records.forEach(function (expense) {
             const tr = document.createElement("tr");

             tr.appendChild(createSafeCell(expense.id));
             tr.appendChild(createSafeCell(expense.title));
             tr.appendChild(createSafeCell(formatAmount(expense.amount)));
  
             const categoryTd = document.createElement("td");
             const badge = document.createElement("span");
             badge.className = "category-badge";
             badge.textContent = expense.category || "-";
             categoryTd.appendChild(badge);
             tr.appendChild(categoryTd);

             tr.appendChild(createSafeCell(expense.description));
             tr.appendChild(createSafeCell(formatDate(expense.date)));

  // Action buttons (safe: static markup, id is a DB integer)
             const actionTd = document.createElement("td");
             actionTd.appendChild(createActionsCell([
               createActionButton("Edit", "edit-btn", function () { editExpense(expense.id); }),
               createActionButton("Delete", "delete-btn", function () { deleteExpense(expense.id); })
             ]));
             tr.appendChild(actionTd);

             expenseTable.appendChild(tr);
           });

  } catch (error) {
    expenseTable.replaceChildren();
    renderEmptyRow(expenseTable, 7, error.message);
  
    console.log("Load expense error:", error);
  }
}

async function editExpense(id) {
  const title = prompt("Enter updated title (leave blank to keep unchanged):");

  if (title === null) return;

  const amount = prompt("Enter updated amount (leave blank to keep unchanged):");

  if (amount === null) return;

  const category = prompt("Enter updated category (leave blank to keep unchanged):");

  if (category === null) return;

  const description = prompt("Enter updated description (leave blank to keep unchanged):");

  if (description === null) return;

  // Build PATCH payload with only changed fields
  const payload = {};

  if (title.trim()) {
    payload.title = title.trim();
  }

  if (amount.trim()) {
    const numericAmount = Number(amount);

    if (!Number.isFinite(numericAmount) || numericAmount < 0) {
      alert("Amount must be a valid number and cannot be negative");
      return;
    }

    payload.amount = numericAmount;
  }

  if (category.trim()) {
    payload.category = category.trim();
  }

  if (description.trim()) {
    payload.description = description.trim();
  }

  if (Object.keys(payload).length === 0) {
    alert("Please provide at least one field to update");
    return;
  }

  try {
    const data = await authApiRequest(
      `${ENDPOINTS.expenseUpdate}/${id}`,
      "PATCH",
      payload
    );

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
      subscriptionTable.replaceChildren();
      renderEmptyRow(subscriptionTable, 8, "No subscription records found.");
      return;
    }

    subscriptionTable.replaceChildren();

    records.forEach(function (subscription) {
      const status = subscription.status || "active";

      const tr = document.createElement("tr");

      tr.appendChild(createSafeCell(subscription.id));
      tr.appendChild(createSafeCell(subscription.name));
      tr.appendChild(createSafeCell(formatAmount(subscription.amount)));
      tr.appendChild(createBadgeCell("cycle-badge", subscription.billing_cycle));
      tr.appendChild(createSafeCell(formatDate(subscription.next_billing_date)));
      tr.appendChild(createStatusBadgeCell(status));
      tr.appendChild(createSafeCell(subscription.note));

      tr.appendChild(createActionsCell([
        createActionButton("Edit", "edit-btn", function () { editSubscription(subscription.id); }),
        createActionButton("Delete", "delete-btn", function () { deleteSubscription(subscription.id); })
      ]));

      subscriptionTable.appendChild(tr);
    });

  } catch (error) {
    subscriptionTable.replaceChildren();
    renderEmptyRow(subscriptionTable, 8, error.message);
  
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
      upcomingTable.replaceChildren();
      renderEmptyRow(upcomingTable, 4, "No upcoming subscriptions found.");
      return;
    }

    upcomingTable.replaceChildren();

    records.forEach(function (subscription) {
      const tr = document.createElement("tr");

      tr.appendChild(createSafeCell(subscription.name));
      tr.appendChild(createSafeCell(formatAmount(subscription.amount)));
      tr.appendChild(createBadgeCell("cycle-badge", subscription.billing_cycle));
      tr.appendChild(createSafeCell(formatDate(subscription.next_billing_date)));

      upcomingTable.appendChild(tr);
    });

  } catch (error) {
    upcomingTable.replaceChildren();
    renderEmptyRow(upcomingTable, 4, error.message);
  
    console.log("Load upcoming subscription error:", error);
  }
}


async function editSubscription(id) {
  const name = prompt("Enter updated name (blank = unchanged):");

  if (name === null) return;

  const amount = prompt("Enter updated amount (blank = unchanged):");

  if (amount === null) return;

  const billingCycle = prompt(
    "Enter billing cycle: monthly, yearly or weekly (blank = unchanged)"
  );

  if (billingCycle === null) return;

  const nextBillingDate = prompt(
    "Enter next billing date YYYY-MM-DD (blank = unchanged):"
  );

  if (nextBillingDate === null) return;

  const note = prompt(
    "Enter updated note (blank = clear note, Cancel = unchanged):"
  );

  const payload = {};

  if (name.trim()) {
    payload.name = name.trim();
  }

  if (amount.trim()) {
    const numericAmount = Number(amount);

    if (!Number.isFinite(numericAmount) || numericAmount <= 0) {
      alert("Amount must be a valid number greater than zero");
      return;
    }

    payload.amount = numericAmount;
  }

  if (billingCycle.trim()) {
    const cycle = billingCycle.trim().toLowerCase();
    const allowedCycles = ["monthly", "yearly", "weekly"];

    if (!allowedCycles.includes(cycle)) {
      alert("Billing cycle must be monthly, yearly or weekly");
      return;
    }

    payload.billing_cycle = cycle;
  }

  if (nextBillingDate.trim()) {
    payload.next_billing_date = nextBillingDate.trim();
  }

  // Cancel means unchanged; blank means clear the note
  if (note !== null) {
    payload.note = note.trim();
  }

  if (Object.keys(payload).length === 0) {
    alert("Please provide at least one field to update");
    return;
  }

  try {
    const data = await authApiRequest(
      `${ENDPOINTS.subscriptionUpdate}/${id}`,
      "PATCH",
      payload
    );

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
    const borrow_type = qs("#type").value;
    const dueDate = qs("#due_date").value;
    const note = qs("#note").value.trim();

    if (!personName || !amount || !borrow_type) {
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
        borrow_type: borrow_type,
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
      data.borrow ||
      data.borrows ||
      data.borrow_records ||
      data.records ||
      [];

    if (!Array.isArray(records) || records.length === 0) {
      borrowTable.replaceChildren();
      renderEmptyRow(borrowTable, 8, "No borrow/lend records found.");
      return;
    }

    borrowTable.replaceChildren();

    records.forEach(function (item) {
      const type = item.type || "-";
      const status = item.status || "pending";
      const safeType = String(type).replace(/[^a-z0-9-]/gi, "");

      const tr = document.createElement("tr");

      tr.appendChild(createSafeCell(item.id));
      tr.appendChild(createSafeCell(item.person_name));
      tr.appendChild(createSafeCell(formatAmount(item.amount)));
      tr.appendChild(createBadgeCell("type-badge " + safeType, type));
      tr.appendChild(createSafeCell(formatDate(item.due_date || item.due_datee)));
      tr.appendChild(createStatusBadgeCell(status));
      tr.appendChild(createSafeCell(item.note));

      tr.appendChild(createActionsCell([
        createActionButton("Edit", "edit-btn", function () { editBorrow(item.id); }),
        createActionButton("Paid", "paid-btn", function () { markBorrowPaid(item.id); }),
        createActionButton("Delete", "delete-btn", function () { deleteBorrow(item.id); })
      ]));

      borrowTable.appendChild(tr);
    });

  } catch (error) {
    borrowTable.replaceChildren();
    renderEmptyRow(borrowTable, 8, error.message);
  
    console.log("Load borrow/lend error:", error);
  }
}


async function editBorrow(id) {
  const personName = prompt("Enter updated person name:");
  const amount = prompt("Enter updated amount:");
  const type = prompt("Enter type: borrowed or lent");

  if (!personName || !amount || !type) {
    alert("Person name, amount and type are required");
    return;
  }

  if (Number(amount) <= 0) {
    alert("Amount must be greater than 0");
    return;
  }

  const allowedTypes = ["borrowed", "lent"];

  if (!allowedTypes.includes(type.trim().toLowerCase())) {
    alert("Type must be borrowed or lent");
    return;
  }

  const dueDate = prompt("Enter due date YYYY-MM-DD (leave empty to keep unchanged):");
  const note = prompt("Enter updated note:");

  const payload = {
    person_name: personName.trim(),
    amount: Number(amount),
    borrow_type: type.trim().toLowerCase()
  };

  // Only send due_date when user provides one
  if (dueDate && dueDate.trim()) {
    payload.due_date = dueDate.trim();
  }

  // Keep existing note if user clicks Cancel
  if (note !== null) {
    payload.note = note.trim();
  }

  try {
    const data = await authApiRequest(
      `${ENDPOINTS.borrowUpdate}/${id}`,
      "PATCH",
      payload
    );

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
    const data = await authApiRequest(`${ENDPOINTS.borrowMarkPaid}/${id}`, "PATCH");

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
    const totalAmountValue = qs("#total_amount").value;
    const monthlyEmiValue = qs("#monthly_emi").value;
    const dueDate = qs("#due_date").value;

    if (!loanName || !totalAmountValue || !monthlyEmiValue || !dueDate) {
      showMessage("loanMessage", "All fields are required", "error");
      return;
    }

    const totalAmount = Number(totalAmountValue);
    const monthlyEmi = Number(monthlyEmiValue);

    if (!Number.isFinite(totalAmount) || totalAmount <= 0) {
      showMessage("loanMessage", "Total amount must be greater than 0", "error");
      return;
    }

    if (!Number.isFinite(monthlyEmi) || monthlyEmi <= 0) {
      showMessage("loanMessage", "Monthly EMI must be greater than 0", "error");
      return;
    }

    if (monthlyEmi >= totalAmount) {
      showMessage(
        "loanMessage",
        "Monthly EMI must be less than total amount",
        "error"
      );
      return;
    }

    try {
      const data = await authApiRequest(ENDPOINTS.loanAdd, "POST", {
        loan_name: loanName,
        total_amount: totalAmount,
        monthly_emi: monthlyEmi,
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
      loanTable.replaceChildren();
      renderEmptyRow(loanTable, 8, "No loan records found.");
      return;
    }

    loanTable.replaceChildren();

    records.forEach(function (loan) {
      const status = loan.status || "active";
      const totalAmount = loan.total_amount || loan.total_ammount || 0;
      const remainingAmount = loan.remaining_amount || 0;

      const tr = document.createElement("tr");

      tr.appendChild(createSafeCell(loan.id));
      tr.appendChild(createSafeCell(loan.loan_name));
      tr.appendChild(createSafeCell(formatAmount(totalAmount)));
      tr.appendChild(createSafeCell(formatAmount(loan.monthly_emi)));
      tr.appendChild(createSafeCell(formatAmount(remainingAmount)));
      tr.appendChild(createSafeCell(formatDate(loan.due_date)));
      tr.appendChild(createStatusBadgeCell(status));

      tr.appendChild(createActionsCell([
        createActionButton("Edit", "edit-btn", function () { editLoan(loan.id, totalAmount); }),
        createActionButton("Repay", "repay-btn", function () { repayLoan(loan.id, remainingAmount); }),
        createActionButton("Delete", "delete-btn", function () { deleteLoan(loan.id); })
      ]));

      loanTable.appendChild(tr);
    });

  } catch (error) {
    loanTable.replaceChildren();
    renderEmptyRow(loanTable, 8, error.message);
  
    console.log("Load loan error:", error);
  }
}


async function editLoan(id) {
  const loanName = prompt("Enter updated loan name (blank = unchanged):");

  if (loanName === null) return;

  const totalAmount = prompt("Enter updated total amount (blank = unchanged):");

  if (totalAmount === null) return;

  const monthlyEmi = prompt("Enter updated monthly EMI (blank = unchanged):");

  if (monthlyEmi === null) return;

  const dueDate = prompt("Enter updated due date YYYY-MM-DD (blank = unchanged):");

  if (dueDate === null) return;

  const payload = {};

  if (loanName.trim()) {
    payload.loan_name = loanName.trim();
  }

  if (totalAmount.trim()) {
    const numericTotal = Number(totalAmount);

    if (!Number.isFinite(numericTotal) || numericTotal <= 0) {
      alert("Total amount must be a valid positive number");
      return;
    }

    payload.total_amount = numericTotal;
  }

  if (monthlyEmi.trim()) {
    const numericEmi = Number(monthlyEmi);

    if (!Number.isFinite(numericEmi) || numericEmi <= 0) {
      alert("Monthly EMI must be a valid positive number");
      return;
    }

    payload.monthly_emi = numericEmi;
  }

  if (dueDate.trim()) {
    payload.due_date = dueDate.trim();
  }

  if (Object.keys(payload).length === 0) {
    alert("Please provide at least one field to update");
    return;
  }

  try {
    const data = await authApiRequest(
      `${ENDPOINTS.loanUpdate}/${id}`,
      "PATCH",
      payload
    );

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


