import streamlit as st
import pandas as pd
from database_local import get_connection


def show_data_entry():

    st.title("📋 Data Entry Workspace")
    st.caption(
        f"Logged in as {st.session_state.username} "
        f"({st.session_state.role})"
    )

    # ============================================================
    # DATA ENTRY MENU
    # ============================================================

    if "data_entry_mode" not in st.session_state:
        st.session_state.data_entry_mode = "home"

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "➕ Add Sales Entry",
            use_container_width=True
        ):
            st.session_state.data_entry_mode = "sales"

    with col2:
        if st.button(
            "💳 Add Payment Split",
            use_container_width=True
        ):
            st.session_state.data_entry_mode = "payment"

    st.divider()

    # ============================================================
    # HOME
    # ============================================================

    if st.session_state.data_entry_mode == "home":

        st.info(
            "Choose an option above to continue."
        )

        return

    # ============================================================
    # ADD NEW SALES ENTRY
    # ============================================================

    if st.session_state.data_entry_mode == "sales":

        st.subheader("➕ Add New Sales Entry")

        if st.button("⬅️ Back to Data Entry Menu"):
            st.session_state.data_entry_mode = "home"
            st.rerun()

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT branch_id, branch_name
            FROM branches
            ORDER BY branch_name
        """)

        branch_data = cursor.fetchall()

        cursor.close()
        conn.close()

        branch_map = {
            row[1]: row[0]
            for row in branch_data
        }

        if st.session_state.role == "Super Admin":

            branch_options = [
                row[1]
                for row in branch_data
            ]

            if not branch_options:
                st.error("No branches found.")
                return

            selected_branch = st.selectbox(
                "Select Branch",
                options=branch_options,
                key="entry_branch"
            )

            selected_branch_id = branch_map[
                selected_branch
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

            selected_branch_id = (
                st.session_state.branch_id
            )

            st.text_input(
                "Branch",
                value=admin_branch or "Branch not found",
                disabled=True
            )

        with st.form("sales_entry_form"):

            col1, col2 = st.columns(2)

            with col1:

                sale_date = st.date_input(
                    "Sale Date"
                )

                customer_name = st.text_input(
                    "Customer Name"
                )

                mobile_number = st.text_input(
                    "Mobile Number"
                )

                product_name = st.text_input(
                    "Product Name"
                )

            with col2:

                gross_sales = st.number_input(
                    "Gross Sales",
                    min_value=0.0,
                    step=1000.0,
                    format="%.2f"
                )

                received_amount = st.number_input(
                    "Received Amount",
                    min_value=0.0,
                    step=1000.0,
                    format="%.2f"
                )

                status = st.selectbox(
                    "Status",
                    options=["open", "close"]
                )

            add_sale = st.form_submit_button(
                "➕ Add Sales Entry",
                use_container_width=True
            )

        if add_sale:

            if selected_branch_id is None:

                st.error(
                    "A valid branch is required."
                )

            elif not customer_name.strip():

                st.error(
                    "Please enter the customer name."
                )

            elif not product_name.strip():

                st.error(
                    "Please enter the product name."
                )

            elif gross_sales <= 0:

                st.error(
                    "Gross sales must be greater than zero."
                )

            elif received_amount > gross_sales:

                st.error(
                    "Received amount cannot be greater "
                    "than gross sales."
                )

            else:

                conn = get_connection()
                cursor = conn.cursor()

                try:

                    cursor.execute(
                        """
                        INSERT INTO customer_sales (
                            branch_id,
                            date,
                            name,
                            mobile_number,
                            product_name,
                            gross_sales,
                            received_amount,
                            status
                        )
                        VALUES (
                            %s, %s, %s, %s,
                            %s, %s, %s, %s
                        )
                        """,
                        (
                            selected_branch_id,
                            sale_date,
                            customer_name.strip(),
                            mobile_number.strip(),
                            product_name.strip(),
                            gross_sales,
                            received_amount,
                            status
                        )
                    )

                    conn.commit()

                    st.success(
                        "Sales entry added successfully."
                    )

                except Exception as error:

                    conn.rollback()

                    st.error(
                        f"Unable to add sales entry: {error}"
                    )

                finally:

                    cursor.close()
                    conn.close()

        return

    # ============================================================
    # ADD PAYMENT SPLIT
    # ============================================================

    if st.session_state.data_entry_mode == "payment":

        st.subheader("💳 Add Payment Split")

        if st.button("⬅️ Back to Data Entry Menu"):
            st.session_state.data_entry_mode = "home"
            st.rerun()

        conn = get_connection()
        cursor = conn.cursor()

        if st.session_state.role == "Admin":

            cursor.execute(
                """
                SELECT
                    sale_id,
                    date,
                    name,
                    product_name,
                    gross_sales,
                    received_amount,
                    pending_amount
                FROM customer_sales
                WHERE branch_id = %s
                ORDER BY sale_id DESC
                """,
                (st.session_state.branch_id,)
            )

        else:

            cursor.execute(
                """
                SELECT
                    sale_id,
                    date,
                    name,
                    product_name,
                    gross_sales,
                    received_amount,
                    pending_amount
                FROM customer_sales
                ORDER BY sale_id DESC
                """
            )

        sales_data = cursor.fetchall()

        cursor.close()
        conn.close()

        if not sales_data:

            st.info(
                "No sales records are available "
                "for payment entry."
            )

            return

        sale_labels = {
            (
                f"Sale {row[0]} | "
                f"{row[2]} | "
                f"{row[3]} | "
                f"₹{row[4]:,.2f}"
            ): row
            for row in sales_data
        }

        selected_sale_label = st.selectbox(
            "Select Sale",
            options=list(sale_labels.keys()),
            key="payment_sale"
        )

        selected_sale = sale_labels[
            selected_sale_label
        ]

        sale_id = selected_sale[0]
        current_received = selected_sale[5]
        current_pending = selected_sale[6]

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Gross Sales",
                f"₹{selected_sale[4]:,.2f}"
            )

        with col2:
            st.metric(
                "Received Amount",
                f"₹{current_received:,.2f}"
            )

        with col3:
            st.metric(
                "Pending Amount",
                f"₹{current_pending:,.2f}"
            )

        with st.form("payment_split_form"):

            payment_date = st.date_input(
                "Payment Date"
            )

            amount_paid = st.number_input(
                "Amount Paid",
                min_value=0.0,
                step=500.0,
                format="%.2f"
            )

            payment_method = st.selectbox(
                "Payment Method",
                options=["Cash", "UPI", "Card"]
            )

            add_payment = st.form_submit_button(
                "💳 Add Payment Split",
                use_container_width=True
            )

        if add_payment:

            if amount_paid <= 0:

                st.error(
                    "Payment amount must be greater than zero."
                )

            elif amount_paid > current_pending:

                st.error(
                    "Payment amount cannot be greater "
                    "than the current pending amount."
                )

            else:

                conn = get_connection()
                cursor = conn.cursor()

                try:

                    cursor.execute(
                        """
                        INSERT INTO payment_splits (
                            sale_id,
                            payment_date,
                            amount_paid,
                            payment_method
                        )
                        VALUES (%s, %s, %s, %s)
                        """,
                        (
                            sale_id,
                            payment_date,
                            amount_paid,
                            payment_method
                        )
                    )

                    conn.commit()

                    st.success(
                        "Payment split added successfully."
                    )

                except Exception as error:

                    conn.rollback()

                    st.error(
                        f"Unable to add payment split: {error}"
                    )

                finally:

                    cursor.close()
                    conn.close()

        return
