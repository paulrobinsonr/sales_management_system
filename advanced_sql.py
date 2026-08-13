import streamlit as st
import pandas as pd
from database_local import get_connection


def show_advanced_sql():

    # ============================================================
    # PAGE STYLE
    # ============================================================

    st.markdown(
        """
        <style>
        .block-container {
            max-width: 1450px;
            padding-left: 2rem;
            padding-right: 2rem;
            padding-top: 1.5rem;
            padding-bottom: 2rem;
        }

        div[data-testid="stDataFrame"] {
            border-radius: 10px;
            overflow: hidden;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # ============================================================
    # MAIN HEADER
    # ============================================================

    st.title("🧮 Advanced SQL Query")
    st.caption(
        f"Welcome back, {st.session_state.username} "
        f"({st.session_state.role})"
    )

    st.divider()

    # ============================================================
    # 15 PREDEFINED SQL QUERIES
    # ============================================================

    queries = {
        "1. Retrieve all records from customer_sales": """\nSELECT * FROM customer_sales;\n        """,\n        "2. Retrieve all records from branches": """\nSELECT * FROM branches;\n        """,\n        "3. Retrieve all records from payment_splits": """\nSELECT * FROM payment_splits;\n        """,\n        "4. Display all sales with status = 'Open'": """\nSELECT * FROM customer_sales WHERE status = 'Open';\n        """,\n        "5. Calculate total gross sales across all branches": """\nSELECT COALESCE(SUM(gross_sales), 0) AS total_gross_sales FROM customer_sales;\n        """,\n        "6. Calculate total received amount across all sales": """\nSELECT COALESCE(SUM(received_amount), 0) AS total_received_amount FROM customer_sales;\n        """,\n        "7. Calculate total pending amount across all sales": """\nSELECT COALESCE(SUM(pending_amount), 0) AS total_pending_amount FROM customer_sales;\n        """,\n        "8. Count total number of sales per branch": """\nSELECT branch_id, COUNT(*) AS total_sales FROM customer_sales GROUP BY branch_id ORDER BY branch_id;\n        """,\n        "9. Retrieve sales details along with branch name": """\nSELECT cs.sale_id, cs.branch_id, b.branch_name, cs.date, cs.name, cs.mobile_number, cs.product_name, cs.gross_sales, cs.received_amount, cs.pending_amount, cs.status
FROM customer_sales cs
INNER JOIN branches b ON cs.branch_id = b.branch_id
ORDER BY cs.sale_id;\n        """,\n        "10. Retrieve sales details with total payment received": """\nSELECT cs.sale_id, cs.name, cs.product_name, cs.gross_sales, cs.received_amount,
COALESCE(SUM(ps.amount_paid), 0) AS total_payment_received
FROM customer_sales cs
LEFT JOIN payment_splits ps ON cs.sale_id = ps.sale_id
GROUP BY cs.sale_id, cs.name, cs.product_name, cs.gross_sales, cs.received_amount
ORDER BY cs.sale_id;\n        """,\n        "11. Show branch-wise total gross sales": """\nSELECT b.branch_id, b.branch_name,
COALESCE(SUM(cs.gross_sales), 0) AS total_gross_sales
FROM branches b
LEFT JOIN customer_sales cs ON b.branch_id = cs.branch_id
GROUP BY b.branch_id, b.branch_name
ORDER BY total_gross_sales DESC;\n        """,\n        "12. Display sales along with payment method used": """\nSELECT cs.sale_id, cs.name, cs.product_name, cs.gross_sales,
ps.payment_method, ps.amount_paid, ps.payment_date
FROM customer_sales cs
INNER JOIN payment_splits ps ON cs.sale_id = ps.sale_id
ORDER BY cs.sale_id;\n        """,\n        "13. Find sales where pending amount is greater than 5000": """\nSELECT * FROM customer_sales WHERE pending_amount > 5000 ORDER BY pending_amount DESC;\n        """,\n        "14. Retrieve top 3 highest gross sales": """\nSELECT * FROM customer_sales ORDER BY gross_sales DESC LIMIT 3;\n        """,\n        "15. Find the branch with highest total gross sales": """\nSELECT b.branch_id, b.branch_name,
SUM(cs.gross_sales) AS total_gross_sales
FROM branches b
INNER JOIN customer_sales cs ON b.branch_id = cs.branch_id
GROUP BY b.branch_id, b.branch_name
ORDER BY total_gross_sales DESC
LIMIT 1;\n        """
    }

    # ============================================================
    # QUERY SELECTOR
    # ============================================================

    st.subheader("🔎 Select a Predefined Query")

    selected_query_name = st.selectbox(
        "SQL Query",
        options=list(queries.keys())
    )

    selected_query = queries[selected_query_name]

    # ============================================================
    # QUERY PREVIEW
    # ============================================================

    st.subheader("📝 SQL Query")

    st.code(
        selected_query.strip(),
        language="sql"
    )

    # ============================================================
    # EXECUTE
    # ============================================================

    execute_query = st.button(
        "▶️ Execute Query",
        use_container_width=True
    )

    if execute_query:

        conn = None
        cursor = None

        try:

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(selected_query)

            rows = cursor.fetchall()

            column_names = [
                column[0]
                for column in cursor.description
            ]

            result_df = pd.DataFrame(
                rows,
                columns=column_names
            )

            st.subheader("📊 Query Result")

            if result_df.empty:

                st.info(
                    "The query executed successfully, "
                    "but returned no records."
                )

            else:

                st.dataframe(
                    result_df,
                    use_container_width=True,
                    hide_index=True
                )

                st.caption(
                    f"{len(result_df)} record(s) returned."
                )

        except Exception as error:

            st.error(
                f"Query execution failed: {error}"
            )

        finally:

            if cursor is not None:
                cursor.close()

            if conn is not None:
                conn.close()

    # ============================================================
    # PROJECT RESULTS
    # ============================================================

    st.divider()

    st.subheader("✅ Project Results")

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            """
            - Structured relational database
            - Automatic financial calculations
            - Accurate payment tracking system
            - Functional Streamlit admin dashboard
            """
        )

    with col2:

        st.markdown(
            """
            - Real-time branch-level reporting
            - Clean and normalized database design
            - Role-based access control
            - Predefined SQL reporting queries
            """
        )
