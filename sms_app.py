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

if 'branch_admin_name' not in st.session_state:
    st.session_state.branch_admin_name=''

if 'branch_name' not in st.session_state:
    st.session_state.branch_name =''    


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Sales Management System",
    page_icon="📒",
    layout="wide"
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
# left_space,login_area,right_space =st.columns([1.5,2,1.5])
# with login_area:
#     st.markdown (
#         "<div style='height: 80px;'></div>",
#         unsafe_allow_html=True
#     )
#     st.markdown(
#         """
#         <h1 style="
#              text-align:center;
#              color:white;
#              font-size:42px;
#              margin-bottom:10px;
#         ">
#              📒 Sales Management System
#         </h1>
#         """,
#         unsafe_allow_html=True
#     )
#     st.markdown(
#         """
#         <h3 style="
#             text-align:center;
#             color:white;
#             margin-bottom:35px;
#         ">
#             Please Login To Continue 🔐
#         </h3>
#         """,
#         unsafe_allow_html=True
#     )
#     username =st.text_input(
#         'Username',
#         key='login_username'
#     )
#     password =st.text_input(
#         'password',
#         type='password',
#         key='login_password'
#     )

#     button_left, button_center, button_right =st.columns([1,1,1])

#     with button_center:
#         login=st.button(
#             'Login',
#             use_container_width=True
#         )
    #---------------------------------------------------    
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

                #get branch admin name
                if user[4]=="Super Admin":
                    st.session_state.branch_name = "All Branches"
                    st.session_state.branch_admin_name="Super Admin"

                else:
                    cursor.execute(
                        """
                        SELECT branch_name, branch_admin_name
                        FROM branches
                        WHERE branch_id=%s
                        """,
                        (user[3],)
                    )
                    branch_data=cursor.fetchone()
                    if branch_data:
                        st.session_state.branch_name = branch_data[0]
                        st.session_state.branch_admin_name = branch_data[1]
                    else:
                        st.session_state.branch_name = ''
                        st.session_state.branch_admin_name=user[1]        

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

    st.write(f"🏢 **{st.session_state.username}**")
    st.write(f"🔑 **{st.session_state.role}**")
    if st.session_state.role == "Super Admin":
        st.write("🌐 **All Branches**")
        # st.write("🧑‍💻 **Super Admin**")
    else:
        # st.write(f"🏢 **{st.session_state.branch_name} **")
        st.write(f"🧑‍💻 **{st.session_state.branch_admin_name}**")    

    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()

    if st.button("⬅️ Logout", use_container_width=True):

        st.session_state.logged_in = False
        st.session_state.role = ""
        st.session_state.username = ""
        st.session_state.branch_id = None
        st.session_state.branch_admin_name=''

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
