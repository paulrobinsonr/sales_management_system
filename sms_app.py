import streamlit as st
from database_local import get_connection


# ============================================================
# SESSION STATE
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "role" not in st.session_state:
    st.session_state.role = ""

if "username" not in st.session_state:
    st.session_state.username = ""

if "branch_id" not in st.session_state:
    st.session_state.branch_id = None


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Sales Management System",
    page_icon="📒",
    layout="centered"
)


# ============================================================
# MAIN CSS
# ============================================================

st.markdown(
    """
    <style>
    .stApp {
        background-color: #0D47A1;
    }

    .stButton > button {
        border-radius: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# LOGIN PAGE
# ============================================================

if not st.session_state.logged_in:

    st.title("📒 Sales Management System")
    st.subheader("Please Login To Continue 🔐")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    login = st.button("Login")

    if login:

        if username.strip() == "" or password.strip() == "":
            st.warning("Please enter Username and Password")

        else:
            conn = get_connection()
            cursor = conn.cursor()

            query = """
                SELECT *
                FROM users
                WHERE username = %s
                AND password = %s
            """

            cursor.execute(query, (username, password))
            user = cursor.fetchone()

            if user:
                st.session_state.logged_in = True
                st.session_state.username = user[1]
                st.session_state.branch_id = user[3]
                st.session_state.role = user[4]

                cursor.close()
                conn.close()

                st.rerun()

            else:
                st.error("Invalid Username or Password")
                cursor.close()
                conn.close()

    st.stop()


# ============================================================
# SIDEBAR / NAVIGATION
# ============================================================

with st.sidebar:

    st.title("📒 Sales Management")
    st.divider()

    page = st.radio(
        "Navigation",
        [
            "📊 Dashboard and Reports",
            "📋 Data Entry Workspace",
            "🗃️ Advanced SQL Query"
        ]
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()

    st.write(f"🧑‍💻 **{st.session_state.username}**")
    st.write(f"🔑 **{st.session_state.role}**")

    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()

    if st.button("⬅️ Logout", use_container_width=True):

        st.session_state.logged_in = False
        st.session_state.role = ""
        st.session_state.username = ""
        st.session_state.branch_id = None

        st.rerun()


# ============================================================
# MODULE ROUTING
# ============================================================

if page == "📊 Dashboard and Reports":
    from dashboard import show_dashboard
    show_dashboard()

elif page == "📋 Data Entry Workspace":
    from data_entry import show_data_entry
    show_data_entry()

elif page == "🗃️ Advanced SQL Query":
    from advanced_sql import show_advanced_sql
    show_advanced_sql()
