import streamlit as st
import pandas as pd
from datetime import date
from database_local import get_connection


def show_dashboard():

    # ============================================================
    # MAIN DASHBOARD
    # ============================================================

    st.title("📊 Sales Dashboard and Reports")
    st.caption(f"Welcome back, {st.session_state.username}")
    st.divider()

    st.subheader("🔍 Filter Options")

    # ============================================================
    # LOAD FILTER OPTIONS
    # ============================================================

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT branch_id, branch_name
        FROM branches
        ORDER BY branch_name
    """)
    branch_data = cursor.fetchall()

    cursor.execute("""
        SELECT DISTINCT product_name
        FROM customer_sales
        ORDER BY product_name
    """)
    product_data = cursor.fetchall()

    cursor.close()
    conn.close()

    # ============================================================
    # BRANCH / PRODUCT OPTIONS
    # ============================================================

    if st.session_state.role == "Super Admin":

        branch_options = ["ALL"] + [
            row[1] for row in branch_data
        ]

    else:

        admin_branch = next(
            (
                row[1]
                for row in branch_data
                if row[0] == st.session_state.branch_id
            ),
            None
        )

        branch_options = (
            [admin_branch]
            if admin_branch
            else []
        )

    product_options = ["ALL"] + [
        row[0] for row in product_data
    ]

    # ============================================================
    # DEFAULT APPLIED FILTERS
    # ============================================================

    if "dashboard_filters" not in st.session_state:

        default_branch = (
            "ALL"
            if st.session_state.role == "Super Admin"
            else (branch_options[0] if branch_options else None)
        )

        st.session_state.dashboard_filters = {
            "branch": default_branch,
            "product": "ALL",
            "from_date": date.today(),
            "to_date": date.today()
        }

    # Make sure an Admin can never retain another branch.
    if st.session_state.role == "Admin":

        admin_branch = (
            branch_options[0]
            if branch_options
            else None
        )

        st.session_state.dashboard_filters["branch"] = admin_branch

    # ============================================================
    # FILTER CONTROLS
    # ============================================================

    with st.form("filter_form"):

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:

            branch = st.selectbox(
                "Select Branch",
                options=branch_options,
                index=(
                    branch_options.index(
                        st.session_state.dashboard_filters["branch"]
                    )
                    if st.session_state.dashboard_filters["branch"]
                    in branch_options
                    else 0
                )
            )

        with col2:

            product = st.selectbox(
                "Select Product",
                options=product_options,
                index=(
                    product_options.index(
                        st.session_state.dashboard_filters["product"]
                    )
                    if st.session_state.dashboard_filters["product"]
                    in product_options
                    else 0
                )
            )

        with col3:

            from_date = st.date_input(
                "From Date",
                value=st.session_state.dashboard_filters["from_date"]
            )

        with col4:

            to_date = st.date_input(
                "To Date",
                value=st.session_state.dashboard_filters["to_date"]
            )

        with col5:

            st.write("")
            st.write("")

            apply_filter = st.form_submit_button(
                "Apply Filter",
                use_container_width=True
            )

    # ============================================================
    # APPLY FILTER
    # ============================================================

    if apply_filter:

        if from_date > to_date:

            st.error(
                "From Date cannot be later than To Date."
            )
            st.stop()

        st.session_state.dashboard_filters = {
            "branch": branch,
            "product": product,
            "from_date": from_date,
            "to_date": to_date
        }

        st.rerun()

    # ============================================================
    # USE ONLY THE LAST APPLIED FILTER
    # ============================================================

    applied_branch = st.session_state.dashboard_filters["branch"]
    applied_product = st.session_state.dashboard_filters["product"]
    applied_from_date = st.session_state.dashboard_filters["from_date"]
    applied_to_date = st.session_state.dashboard_filters["to_date"]

    # ============================================================
    # BUILD COMMON SALES FILTER
    # ============================================================

    where_clause = ""
    params = []

    if st.session_state.role == "Admin":

        where_clause += " AND branch_id = %s"
        params.append(st.session_state.branch_id)

    elif applied_branch != "ALL":

        where_clause += """
            AND branch_id = (
                SELECT branch_id
                FROM branches
                WHERE branch_name = %s
            )
        """
        params.append(applied_branch)

    if applied_product != "ALL":

        where_clause += " AND product_name = %s"
        params.append(applied_product)

    where_clause += " AND date BETWEEN %s AND %s"
    params.append(applied_from_date)
    params.append(applied_to_date)

    # ============================================================
    # STATS / FINANCIAL KPI
    # ============================================================

    conn = get_connection()
    cursor = conn.cursor()

    kpi_query = f"""
        SELECT
            COALESCE(SUM(gross_sales), 0),
            COALESCE(SUM(received_amount), 0),
            COALESCE(SUM(pending_amount), 0)
        FROM customer_sales
        WHERE 1=1
        {where_clause}
    """

    cursor.execute(kpi_query, params)
    result = cursor.fetchone()

    if result is None:
        result = (0, 0, 0)

    gross_sales = result[0] or 0
    received_amount = result[1] or 0
    pending_amount = result[2] or 0

    if gross_sales > 0:

        collection_percentage = (
            received_amount / gross_sales
        ) * 100

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
        st.metric(
            "Gross Sales",
            f"₹{gross_sales:,.0f}"
        )

    with card2:
        st.metric(
            "Received Amount",
            f"₹{received_amount:,.0f}"
        )

    with card3:
        st.metric(
            "Pending Amount",
            f"₹{pending_amount:,.0f}"
        )

    with card4:
        st.metric(
            "Collection %",
            f"{collection_percentage:.2f}%"
        )

    # ============================================================
    # CUSTOMER SALES
    # ============================================================

    st.divider()
    st.subheader("📈 Customer Sales")

    conn = get_connection()
    cursor = conn.cursor()

    sales_query = f"""
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
        {where_clause}
        ORDER BY date DESC, sale_id DESC
    """

    cursor.execute(sales_query, params)
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

    df = pd.DataFrame(
        sales,
        columns=column_names
    )

    if df.empty:

        st.info(
            "No sales data found for the selected filters."
        )

    else:

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

    cursor.close()
    conn.close()

    # ============================================================
    # REPORTS / INSIGHTS
    # ============================================================

    if not df.empty:

        st.divider()
        st.subheader("📊 Business Insights")

        # --------------------------------------------------------
        # Branch-wise Sales
        # --------------------------------------------------------

        branch_summary = (
            df.groupby("Branch ID", as_index=False)["Gross Sales"]
            .sum()
            .sort_values("Gross Sales", ascending=False)
        )

        col1, col2 = st.columns(2)

        with col1:

            st.write("### 🏢 Branch-wise Sales")

            st.bar_chart(
                branch_summary.set_index("Branch ID")
            )

        # --------------------------------------------------------
        # Sales Trend
        # --------------------------------------------------------

        daily_sales = (
            df.groupby("Date", as_index=False)["Gross Sales"]
            .sum()
            .sort_values("Date")
        )

        with col2:

            st.write("### 📈 Sales Trend")

            st.line_chart(
                daily_sales.set_index("Date")
            )

        # --------------------------------------------------------
        # Sales Status
        # --------------------------------------------------------

        st.write("### 📌 Sales Status")

        status_summary = (
            df.groupby("Status")
            .size()
            .reset_index(name="Sales Count")
        )

        st.dataframe(
            status_summary,
            use_container_width=True,
            hide_index=True
        )

        # --------------------------------------------------------
        # Branch Performance Summary
        # --------------------------------------------------------

        st.write("### 🏆 Branch Performance Summary")

        performance = (
            df.groupby("Branch ID")
            .agg(
                Total_Sales=("Sale ID", "count"),
                Gross_Sales=("Gross Sales", "sum"),
                Received_Amount=("Received Amount", "sum")
            )
            .reset_index()
        )

        performance["Pending_Amount"] = (
            performance["Gross_Sales"]
            - performance["Received_Amount"]
        )

        performance["Collection_Percentage"] = (
            performance["Received_Amount"]
            .div(performance["Gross_Sales"])
            .fillna(0)
            * 100
        )

        st.dataframe(
            performance,
            use_container_width=True,
            hide_index=True
        )

    # ============================================================
    # PAYMENT METHOD SUMMARY
    # ============================================================

    st.divider()
    st.subheader("💳 Payment Method Summary")

    try:

        conn = get_connection()
        cursor = conn.cursor()

        payment_where = ""
        payment_params = []

        if st.session_state.role == "Admin":

            payment_where += " AND cs.branch_id = %s"
            payment_params.append(st.session_state.branch_id)

        elif applied_branch != "ALL":

            payment_where += """
                AND cs.branch_id = (
                    SELECT branch_id
                    FROM branches
                    WHERE branch_name = %s
                )
            """
            payment_params.append(applied_branch)

        if applied_product != "ALL":

            payment_where += " AND cs.product_name = %s"
            payment_params.append(applied_product)

        payment_where += """
            AND cs.date BETWEEN %s AND %s
        """

        payment_params.append(applied_from_date)
        payment_params.append(applied_to_date)

        payment_query = f"""
            SELECT
                ps.payment_method,
                COALESCE(SUM(ps.amount_paid), 0)
            FROM payment_splits ps
            INNER JOIN customer_sales cs
                ON ps.sale_id = cs.sale_id
            WHERE 1=1
            {payment_where}
            GROUP BY ps.payment_method
            ORDER BY ps.payment_method
        """

        cursor.execute(
            payment_query,
            payment_params
        )

        payment_data = cursor.fetchall()

        cursor.close()
        conn.close()

        if payment_data:

            payment_df = pd.DataFrame(
                payment_data,
                columns=[
                    "Payment Method",
                    "Amount"
                ]
            )

            st.dataframe(
                payment_df,
                use_container_width=True,
                hide_index=True
            )

            st.bar_chart(
                payment_df.set_index("Payment Method")
            )

        else:

            st.info(
                "No payment split data found for the selected filters."
            )

    except Exception:

        try:
            cursor.close()
            conn.close()
        except Exception:
            pass

        st.info(
            "Payment split summary will be available after the "
            "payment_splits module/table is connected."
        )
