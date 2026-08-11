import streamlit as st
import pandas as pd
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

    # CRITICAL: dashboard code cannot run before login.
    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("📒 Sales Management")
    st.divider()

    if st.button("📊 DashBoard and Reports", use_container_width=True):
        pass

    if st.button("📋 Data Entry Workspace", use_container_width=True):
        pass

    if st.button("🗃️ Advanced SQL Engine", use_container_width=True):
        pass

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
# MAIN DASHBOARD
# ============================================================

st.title("📊 Dashboard and Reports")
st.caption(f"Welcome back, {st.session_state.username}")
st.divider()

st.subheader("🔍 Filter Options")


# ============================================================
# FILTER DATA
# ============================================================

conn = get_connection()
cursor = conn.cursor()

cursor.execute(
    """
    SELECT branch_id, branch_name
    FROM branches
    ORDER BY branch_name
    """
)
branch_data = cursor.fetchall()

cursor.execute(
    """
    SELECT DISTINCT product_name
    FROM customer_sales
    ORDER BY product_name
    """
)
product_data = cursor.fetchall()

cursor.close()
conn.close()


# ============================================================
# BRANCH / PRODUCT OPTIONS
# ============================================================

if st.session_state.role == "Super Admin":

    branch_options = ["ALL"] + [row[1] for row in branch_data]

else:

    admin_branch = next(
        (
            row[1]
            for row in branch_data
            if row[0] == st.session_state.branch_id
        ),
        None
    )

    branch_options = [admin_branch] if admin_branch else []

product_options = ["ALL"] + [row[0] for row in product_data]


# ============================================================
# FILTER CONTROLS
# ============================================================
with st.form("filter_form"):
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
      branch = st.selectbox("Select Branch", options=branch_options)

    with col2:
      product = st.selectbox("Select Product", options=product_options)

    with col3:
      from_date = st.date_input("From Date")

    with col4:
      to_date = st.date_input("To Date")

    with col5:
      st.write("")
      st.write("")
      apply_filter = st.form_submit_button(
          "Apply Filter",
          use_container_width=True
    )


# ============================================================
# STATS
# ============================================================

conn = get_connection()
cursor = conn.cursor()

query = """
    SELECT
        SUM(gross_sales),
        SUM(received_amount),
        SUM(pending_amount)
    FROM customer_sales
    WHERE 1=1
"""

params = []


# Branch filter
if st.session_state.role == "Admin":

    query += " AND branch_id = %s"
    params.append(st.session_state.branch_id)

elif branch != "ALL":

    query += """
        AND branch_id = (
            SELECT branch_id
            FROM branches
            WHERE branch_name = %s
        )
    """
    params.append(branch)


# Product filter
if product != "ALL":

    query += " AND product_name = %s"
    params.append(product)


# Date filter
query += " AND date BETWEEN %s AND %s"
params.append(from_date)
params.append(to_date)


# Execute
cursor.execute(query, params)
result = cursor.fetchone()

if result is None:
    result = (0, 0, 0)


# KPI values
gross_sales = result[0] or 0
received_amount = result[1] or 0
pending_amount = result[2] or 0

if gross_sales > 0:
    collection_percentage = (received_amount / gross_sales) * 100
else:
    collection_percentage = 0

cursor.close()
conn.close()


# ============================================================
# FINANCIAL SUMMARY
# ============================================================

st.divider()
st.subheader("💰 Financial Summary")

card1, card2, card3, card4 = st.columns(4)

with card1:
    st.metric("Gross Sales", f"₹{gross_sales:,.0f}")

with card2:
    st.metric("Received Amount", f"₹{received_amount:,.0f}")

with card3:
    st.metric("Pending Amount", f"₹{pending_amount:,.0f}")

with card4:
    st.metric("Collection %", f"{collection_percentage:.2f}%")


# ============================================================
# CUSTOMER SALES
# ============================================================

st.divider()
st.subheader("📈 Customer Sales")

conn = get_connection()
cursor = conn.cursor()

if st.session_state.role == "Super Admin":

    query = """
        SELECT
            sale_id,
            branch_id,
            date,
            name,
            mobile_number,
            product_name,
            gross_sales,
            received_amount,
            status
        FROM customer_sales
        WHERE 1=1
    """

    cursor.execute(query)

else:

    query = """
        SELECT
            sale_id,
            branch_id,
            date,
            name,
            mobile_number,
            product_name,
            gross_sales,
            received_amount,
            status
        FROM customer_sales
        WHERE branch_id = %s
    """

    cursor.execute(query, (st.session_state.branch_id,))


sales = cursor.fetchall()

column_names = [
    "Sale ID",
    "Branch ID",
    "Date",
    "Customer Name",
    "Mobile Number",
    "Product Name",
    "Gross Sales",
    "Received Amount",
    "Status"
]

df = pd.DataFrame(sales, columns=column_names)

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)

cursor.close()
conn.close()
