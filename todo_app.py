import streamlit as st
import json
import os
from datetime import date
import matplotlib.pyplot as plt

# --- Email Setup (Optional, placeholder) ---
EMAIL_SENDER = "your_email@gmail.com"
EMAIL_PASSWORD = "your_gmail_app_password"

# --- Page Setup ---
st.set_page_config(page_title="To-Do List", page_icon="🗃")
st.title("🗃 To-Do List App with Priority, Filters, Chart")

# --- Background Styling ---
st.markdown("""
<style>
.stApp {
    background-color: #e3f2fd !important;
}
.main > div {
    background: #ffffffcc;
    border-radius: 16px;
    padding: 2rem;
    box-shadow: 0 4px 24px rgba(0,0,0,0.07);
    margin-top: 2rem;
}
</style>
""", unsafe_allow_html=True)

# --- File Paths ---
USERS_FILE = "users.json"
def get_task_file(username): return f"tasks_{username}.json"

# --- Load/Save Helpers ---
def load_users():
    return json.load(open(USERS_FILE)) if os.path.exists(USERS_FILE) else {}

def save_users(users):
    json.dump(users, open(USERS_FILE, "w"), indent=4)

def load_tasks(username):
    path = get_task_file(username)
    return json.load(open(path)) if os.path.exists(path) else []

def save_tasks(username, tasks):
    json.dump(tasks, open(get_task_file(username), "w"), indent=4)

# --- Session Initialization ---
for key, default in {
    "users": load_users(),
    "logged_in": False,
    "username": "",
    "tasks": [],
    "show_register": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# --- Register UI ---
def register_user():
    st.subheader("🔑 Register")
    uname = st.text_input("Username", key="reg_user")
    pwd = st.text_input("Password", type="password", key="reg_pass")
    if st.button("Register"):
        if uname in st.session_state.users:
            st.error("Username already exists.")
        elif not uname or not pwd:
            st.error("Username and password required.")
        else:
            st.session_state.users[uname] = pwd
            save_users(st.session_state.users)
            st.success("Registered successfully. Please log in.")
            st.session_state.show_register = False

# --- Login UI ---
def login_user():
    st.subheader("🔑 Login")
    uname = st.text_input("Username", key="login_user")
    pwd = st.text_input("Password", type="password", key="login_pass")
    if st.button("Login"):
        if uname in st.session_state.users and st.session_state.users[uname] == pwd:
            st.session_state.logged_in = True
            st.session_state.username = uname
            st.session_state.tasks = load_tasks(uname)
            st.success(f"Welcome, {uname}!")
            st.rerun()
        else:
            st.error("Invalid username or password.")
    if st.button("New user? Register"):
        st.session_state.show_register = True
        st.rerun()

# --- Logout ---
def logout_user():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.tasks = []
    st.rerun()

# --- UI Routing ---
if not st.session_state.logged_in:
    register_user() if st.session_state.show_register else login_user()
    st.stop()

# --- Sidebar Info ---
st.sidebar.write(f"👤 Logged in as: {st.session_state.username}")
st.sidebar.button("Logout", on_click=logout_user)

# --- Add Task ---
st.subheader("➕ Add Task")
task = st.text_input("New Task")
priority = st.selectbox("Priority", ["Low", "Medium", "High"])
due_date = st.date_input("Due Date (optional)", value=date.today())

if st.button("Add"):
    if task:
        st.session_state.tasks.append({
            "task": task,
            "done": False,
            "priority": priority,
            "due_date": str(due_date)
        })
        save_tasks(st.session_state.username, st.session_state.tasks)
        st.rerun()
    else:
        st.warning("Task cannot be empty.")

# --- Task Filters ---
st.subheader("🔍 Filter Tasks")
filter_status = st.selectbox("Filter by Status", ["All", "Pending", "Completed"])
filter_priority = st.selectbox("Filter by Priority", ["All", "High", "Medium", "Low"])

def apply_filters(tasks):
    filtered = tasks
    if filter_status != "All":
        is_done = filter_status == "Completed"
        filtered = [t for t in filtered if t["done"] == is_done]
    if filter_priority != "All":
        filtered = [t for t in filtered if t["priority"] == filter_priority]
    return filtered

filtered_tasks = apply_filters(st.session_state.tasks)

# --- Show Tasks ---
st.subheader("📝 Your Tasks")

priority_map = {"High": 0, "Medium": 1, "Low": 2}
for t in st.session_state.tasks:
    if "priority" not in t:
        t["priority"] = "Low"
    if "due_date" not in t:
        t["due_date"] = ""

filtered_tasks.sort(key=lambda x: priority_map.get(x["priority"], 3))

updated_tasks = []
for i, t in enumerate(filtered_tasks):
    col1, col2, col3, col4, col5, col6 = st.columns([0.1, 0.35, 0.15, 0.2, 0.1, 0.1])
    with col1:
        symbol = "✔️" if t["done"] else "⭐"
        st.write(symbol)
    with col2:
        text = st.text_input(f"Task {i+1}", value=t["task"], key=f"task_{i}")
    with col3:
        due = st.date_input("Due", value=date.fromisoformat(t["due_date"]) if t["due_date"] else date.today(), key=f"due_{i}")
    with col4:
        pval = st.selectbox("Priority", ["Low", "Medium", "High"], index=["Low", "Medium", "High"].index(t["priority"]), key=f"priority_{i}")
    with col5:
        done = st.checkbox("Done", value=t["done"], key=f"done_{i}")
    with col6:
        if st.button("Delete", key=f"del_{i}"):
            st.session_state.tasks.remove(t)
            save_tasks(st.session_state.username, st.session_state.tasks)
            st.rerun()
    updated_tasks.append({
        "task": text,
        "done": done,
        "priority": pval,
        "due_date": str(due)
    })

st.session_state.tasks = updated_tasks
save_tasks(st.session_state.username, updated_tasks)

# --- Clear Completed ---
if st.button("🧹 Clear Completed Tasks"):
    st.session_state.tasks = [t for t in st.session_state.tasks if not t["done"]]
    save_tasks(st.session_state.username, st.session_state.tasks)
    st.success("Completed tasks cleared!")
    st.rerun()

# --- Pie Chart ---
st.subheader("📊 Task Completion Overview")
done_count = sum(1 for t in st.session_state.tasks if t["done"])
pending_count = len(st.session_state.tasks) - done_count

fig, ax = plt.subplots()
ax.pie([done_count, pending_count], labels=["Completed", "Pending"], autopct="%1.1f%%", startangle=90, colors=["#4caf50", "#ffc107"])
ax.axis("equal")
st.pyplot(fig)