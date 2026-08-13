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
        f"({st.session_state.branch_admin_name})"
    )
    st.divider()

    # ============================================================
    # PREDEFINED QUERIES
    # ============================================================

    queries = {
        "1. Retrieve all records from customer_sales": 'SELECT * FROM customer_sales;',
        "2. Retrieve all records from branches": 'SELECT * FROM branches;',
        "3. Retrieve all records from payment_splits": 'SELECT * FROM payment_splits;',
        "4. Display all sales with status = 'Open'": "SELECT * FROM customer_sales WHERE status = 'Open';",
        "5. Calculate total gross sales across all branches": 'SELECT COALESCE(SUM(gross_sales), 0) AS total_gross_sales FROM customer_sales;',
        "6. Calculate total received amount across all sales": 'SELECT COALESCE(SUM(received_amount), 0) AS total_received_amount FROM customer_sales;',
        "7. Calculate total pending amount across all sales": 'SELECT COALESCE(SUM(pending_amount), 0) AS total_pending_amount FROM customer_sales;',
        "8. Count total number of sales per branch": 'SELECT branch_id, COUNT(*) AS total_sales FROM customer_sales GROUP BY branch_id ORDER BY branch_id;',
        "9. Retrieve sales details along with branch name": 'SELECT cs.sale_id, cs.branch_id, b.branch_name, cs.date, cs.name, cs.mobile_number, cs.product_name, cs.gross_sales, cs.received_amount, cs.pending_amount, cs.status FROM customer_sales AS cs INNER JOIN branches AS b ON cs.branch_id = b.branch_id ORDER BY cs.sale_id;',
        "10. Retrieve sales details with total payment received": 'SELECT cs.sale_id, cs.name, cs.product_name, cs.gross_sales, cs.received_amount, COALESCE(SUM(ps.amount_paid), 0) AS total_payment_received FROM customer_sales AS cs LEFT JOIN payment_splits AS ps ON cs.sale_id = ps.sale_id GROUP BY cs.sale_id, cs.name, cs.product_name, cs.gross_sales, cs.received_amount ORDER BY cs.sale_id;',
        "11. Show branch-wise total gross sales": 'SELECT b.branch_id, b.branch_name, COALESCE(SUM(cs.gross_sales), 0) AS total_gross_sales FROM branches AS b LEFT JOIN customer_sales AS cs ON b.branch_id = cs.branch_id GROUP BY b.branch_id, b.branch_name ORDER BY total_gross_sales DESC;',
        "12. Display sales along with payment method used": 'SELECT cs.sale_id, cs.name, cs.product_name, cs.gross_sales, ps.payment_method, ps.amount_paid, ps.payment_date FROM customer_sales AS cs INNER JOIN payment_splits AS ps ON cs.sale_id = ps.sale_id ORDER BY cs.sale_id;',
        "13. Find sales where pending amount is greater than 5000": 'SELECT * FROM customer_sales WHERE pending_amount > 5000 ORDER BY pending_amount DESC;',
        "14. Retrieve top 3 highest gross sales": 'SELECT * FROM customer_sales ORDER BY gross_sales DESC LIMIT 3;',
        "15. Find the branch with highest total gross sales": 'SELECT b.branch_id, b.branch_name, SUM(cs.gross_sales) AS total_gross_sales FROM branches AS b INNER JOIN customer_sales AS cs ON b.branch_id = cs.branch_id GROUP BY b.branch_id, b.branch_name ORDER BY total_gross_sales DESC LIMIT 1;',
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

    # # ============================================================
    # # QUERY PREVIEW
    # # ============================================================

    # st.subheader("📝 SQL Query")

    # st.code(
    #     selected_query,
    #     language="sql"
    # )

    # ============================================================
    # EXECUTE QUERY
    # ============================================================

    if st.button(
        "▶️ Execute Query",
        use_container_width=True
    ):

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

