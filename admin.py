import streamlit as st
from streamlit_option_menu import option_menu
from datetime import datetime
import plotly.express as px
import pandas as pd
import time


def admin_view(auth_service):
    with st.sidebar:
        selected = option_menu(
            menu_title="Admin Menu",
            options=["User Statistics", "HR Statistics","Manage HR", "Register HR", "Manage Users", "Logout"],
            icons=["bar-chart", "bar-chart","people", "person-plus", "person",  "box-arrow-right"],
            menu_icon="gear",
            default_index=0,
            orientation="vertical",
        )


    @st.dialog("Confirm Deletion")
    def confirm_delete(account_id, role, username):
        st.warning(f"Are you sure you want to delete {role} '{username}'? This action cannot be undone.")
        if st.button("Yes, Delete", type="primary"):
            auth_service.delete_user(account_id)
            st.success(f"{role} '{username}' deleted successfully.")
            time.sleep(2)
            st.rerun()

    @st.dialog("Update Information")
    def update_account(account_id, username, email, full_name, industry=None, role="HR"):
        st.subheader(f"Update Information for {role}: {username}")
        updated_full_name = st.text_input("Full Name", value=full_name)
        updated_email = st.text_input("Email", value=email)
        new_password = st.text_input("New Password (optional)", type="password")

        if role == "User":
            updated_industry = st.selectbox(
                "Industry",
                ["Software", "Finance", "Healthcare", "Education"],
                index=["Software", "Finance", "Healthcare", "Education"].index(industry)
                if industry else 0,
            )

        if st.button("Save Changes"):
            try:
                auth_service.update_user(
                    account_id,
                    updated_full_name,
                    updated_email,
                    new_password,
                    updated_industry if role == "User" else None,
                )
                st.success(f"{role} '{username}' information updated successfully.")
                time.sleep(2)
                st.rerun()
            except ValueError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

    def search_accounts(accounts, search_query):
        if not search_query:
            return accounts

        search_query_lower = search_query.lower()
        return [
            acc for acc in accounts
            if any(
                search_query_lower in str(field).lower() if field else ""
                for field in acc[:5]
            )
        ]

    def display_search(role):
        search_query = st.text_input("Search Accounts", placeholder="Search by name, username, email, etc.")
        return search_query

    def display_accounts(accounts, role):
        st.header(f"Manage {role} Accounts", divider="blue")
        search_query = display_search(role)
        searched_accounts = search_accounts(accounts, search_query)

        st.write("")

        if searched_accounts:
            if role == "User":
                col1, col2, col3, col4, col5, col6 = st.columns([0.2, 0.2, 0.2, 0.15, 0.15, 0.1])
                with col1:
                    st.write("###### Name")
                with col2:
                    st.write("###### Username")
                with col3:
                    st.write("###### Email")
                with col4:
                    st.write("###### Industry")
                with col5:
                    st.write("###### Registered At")
                with col6:
                    st.write("###### Actions")
            else:
                col1, col2, col3, col4, col5 = st.columns([0.25, 0.25, 0.25, 0.15, 0.1])
                with col1:
                    st.write("##### Name")
                with col2:
                    st.write("##### Username")
                with col3:
                    st.write("##### Email")
                with col4:
                    st.write("##### Registered At")
                with col5:
                    st.write("##### Actions")

            st.write("---")

            for account in searched_accounts:
                if role == "User":
                    account_id, full_name, username, email, industry, registered_at = account[:6]
                    col1, col2, col3, col4, col5, col6 = st.columns([0.2, 0.2, 0.2, 0.15, 0.15, 0.1])
                else:
                    account_id, full_name, username, email, registered_at = account[:5]
                    col1, col2, col3, col4, col5 = st.columns([0.25, 0.25, 0.25, 0.15, 0.1])

                with col1:
                    st.write(full_name)
                with col2:
                    st.write(username)
                with col3:
                    st.write(email)
                if role == "User":
                    with col4:
                        st.write(industry)
                with col4 if role == "HR" else col5:
                    try:
                        registered_at_dt = (
                            registered_at if isinstance(registered_at, datetime)
                            else datetime.strptime(registered_at, "%Y-%m-%d %H:%M:%S")
                        )
                        st.write(registered_at_dt.strftime("%Y-%m-%d %H:%M:%S"))
                    except Exception:
                        st.write("N/A")
                with col5 if role == "HR" else col6:
                    action_key = f"action_{role.lower()}_{account_id}"
                    action = st.selectbox(
                        " ",
                        ["Select", "Update", "Delete"],
                        key=action_key,
                        label_visibility="collapsed",
                    )
                    if action == "Delete":
                        confirm_delete(account_id, role, username)
                    elif action == "Update":
                        update_account(account_id, username, email, full_name, industry if role == "User" else None, role)

        else:
            st.info(f"No {role} accounts match the search query.")

    def register_hr():
        registration_details = None

        with st.container():
            col1, col2 = st.columns([0.5, 0.5])
            with col1:
                full_name = st.text_input("Full Name")
            with col2:
                username = st.text_input("Username")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit_button = st.button("Register HR")

            if submit_button:
                try:
                    auth_service.register_user(full_name, username, email, password, None, role_name="HR")
                    registration_details = {
                        "Full Name": full_name,
                        "Username": username,
                        "Email": email,
                        "Password": password,
                        "Registered At": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    }
                    st.success(f"HR {username} registered successfully.")
                except ValueError as e:
                    st.error(str(e))
                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}")

        if registration_details:
            st.markdown("---")
            st.subheader("Registration Details")
            st.write(f"**Full Name:** {registration_details['Full Name']}")
            st.write(f"**Username:** {registration_details['Username']}")
            st.write(f"**Email:** {registration_details['Email']}")
            st.write(f"**Registered At:** {registration_details['Registered At']}")
            details_txt = (
                f"Registration Details\n"
                f"---------------------\n"
                f"Full Name: {registration_details['Full Name']}\n"
                f"Username: {registration_details['Username']}\n"
                f"Email: {registration_details['Email']}\n"
                f"Password: {registration_details['Password']}\n"
                f"Registered At: {registration_details['Registered At']}\n"
            )
            st.download_button(
                label="📥 Download Registration Details (includes password)",
                data=details_txt,
                file_name=f"{registration_details['Username']}_registration.txt",
                mime="text/plain",
            )

    def show_user_statistics():
        st.header("User Statistics", divider="blue")
        user_data = auth_service.get_all_user_accounts()
        df = pd.DataFrame(user_data, columns=["ID", "Name", "Username", "Email", "Industry", "Registered At"])
        df["Registered At"] = pd.to_datetime(df["Registered At"])
    
        st.write("### Overview Metrics")
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Total Users", len(df))
        with col2:
            st.metric("Industries Covered", df["Industry"].nunique())
        with col3:
            st.metric("Most Popular Industry", df["Industry"].mode()[0])
        with col4:
            st.metric("Latest Registration", df["Registered At"].max().strftime("%Y-%m-%d"))
        with col5:
            st.metric("Earliest Registration", df["Registered At"].min().strftime("%Y-%m-%d"))
    
        st.write("## Charts")
        col1, col2, col3 = st.columns(3)
        with col1:
            fig1 = px.histogram(df, x="Industry", title="User Count by Industry")
            st.plotly_chart(fig1, use_container_width=True)
    
        with col2:
            fig2 = px.line(df.sort_values("Registered At"), x="Registered At", title="User Registration Over Time")
            st.plotly_chart(fig2, use_container_width=True)
    
        with col3:
            fig3 = px.pie(df, names="Industry", title="User Industry Distribution")
            st.plotly_chart(fig3, use_container_width=True)
    
        col1, col2, col3 = st.columns(3)
        with col1:
            fig4 = px.bar(
                df.groupby("Industry").size().reset_index(name="Count"),
                x="Industry",
                y="Count",
                title="User Count per Industry"
            )
            st.plotly_chart(fig4, use_container_width=True)
    
        with col2:
            fig5 = px.box(df, x="Industry", y=df["Registered At"].dt.month, title="Registration Month by Industry")
            st.plotly_chart(fig5, use_container_width=True)
    
        with col3:
            fig6 = px.scatter(df, x="Registered At", y="Industry", color="Industry", title="Registration Timeline by Industry")
            st.plotly_chart(fig6, use_container_width=True)
    
        col1, col2, col3 = st.columns(3)
        with col1:
            fig7 = px.density_heatmap(df, x="Industry", y=df["Registered At"].dt.year, title="Industry Registrations by Year")
            st.plotly_chart(fig7, use_container_width=True)
    
        with col2:
            fig8 = px.histogram(df, x=df["Registered At"].dt.year, title="Registrations Per Year")
            st.plotly_chart(fig8, use_container_width=True)
    
        with col3:
            fig9 = px.ecdf(df, x="Registered At", title="Cumulative Registrations Over Time")
            st.plotly_chart(fig9, use_container_width=True)
    
    
    def show_hr_statistics():
        st.header("HR Statistics", divider="blue")
        hr_data = auth_service.get_all_hr_accounts()
        df = pd.DataFrame(hr_data, columns=["ID", "Name", "Username", "Email", "Registered At"])
        df["Registered At"] = pd.to_datetime(df["Registered At"])
    
        st.write("### Overview Metrics")
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Total HRs", len(df))
        with col2:
            st.metric("Most Recent HR", df.sort_values("Registered At", ascending=False)["Name"].iloc[0])
        with col3:
            st.metric("Earliest HR Registration", df["Registered At"].min().strftime("%Y-%m-%d"))
        with col4:
            st.metric("Average Registration Year", int(df["Registered At"].dt.year.mean()))
        with col5:
            st.metric("Median Registration Year", int(df["Registered At"].dt.year.median()))
    
        st.write("### Charts")
        col1, col2, col3 = st.columns(3)
        with col1:
            fig1 = px.histogram(df, x="Registered At", title="HR Registration Over Time")
            st.plotly_chart(fig1, use_container_width=True)
    
        with col2:
            fig2 = px.pie(df, names="Name", title="HR Contribution Share")
            st.plotly_chart(fig2, use_container_width=True)
    
        with col3:
            fig3 = px.scatter(
                df,
                x="Registered At",
                y=df["Registered At"].dt.year,
                title="HR Registration by Year"
            )
            st.plotly_chart(fig3, use_container_width=True)
    
        col1, col2, col3 = st.columns(3)
        with col1:
            fig4 = px.box(df, y="Registered At", title="HR Registration Date Spread")
            st.plotly_chart(fig4, use_container_width=True)
    
        with col2:
            fig5 = px.bar(
                df.groupby(df["Registered At"].dt.year).size().reset_index(name="Count"),
                x="Registered At",
                y="Count",
                title="HR Count per Year"
            )
            st.plotly_chart(fig5, use_container_width=True)
    
        with col3:
            fig6 = px.line(df, x="Registered At", y=df.index, title="HR Registrations Timeline")
            st.plotly_chart(fig6, use_container_width=True)
    
        col1, col2, col3 = st.columns(3)
        with col1:
            fig7 = px.density_heatmap(df, x="Registered At", y=df.index, title="Registration Heatmap")
            st.plotly_chart(fig7, use_container_width=True)
    
        with col2:
            fig8 = px.histogram(df, x=df["Registered At"].dt.year, title="Registrations Per Year")
            st.plotly_chart(fig8, use_container_width=True)
    
        with col3:
            fig9 = px.ecdf(df, x="Registered At", title="Cumulative Registrations Over Time")
            st.plotly_chart(fig9, use_container_width=True)
    
    
    if selected == "Register HR":
        _, col1, _ = st.columns([0.25, 0.50, 0.25])
        with col1:
            with st.container():
                st.header("💼 Register HR", divider="blue")
                st.write("")
                register_hr()

    elif selected == "Manage HR":
        hr_accounts = auth_service.get_all_hr_accounts()
        display_accounts(hr_accounts, role="HR")

    elif selected == "Manage Users":
        user_accounts = auth_service.get_all_user_accounts()
        display_accounts(user_accounts, role="User")

    elif selected == "User Statistics":
        show_user_statistics()

    elif selected == "HR Statistics":
        show_hr_statistics()

    elif selected == "Logout":
        st.session_state.clear()
        st.rerun()
