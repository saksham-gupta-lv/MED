import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from streamlit_option_menu import option_menu

st.set_page_config(page_title="Bonus Tier App", page_icon="📈", layout="wide")

data = {
    "region": ["Region 1", "Region 2", "Region 3", "Region 4"] * 24,
    "office_name": ["Parkersburg", "Kensington", "Pittsburg", "Beaver Falls"] * 24,
    "sales_band": ["High", "Medium", "Low", "High"] * 24,
    "month": [
        f"{year}-{month:02d}" 
        for year in range(2022, 2024) 
        for month in range(1, 13)
    ] * 4,
    "actual_sales": [
        30000 + i * 500 for i in range(96)
    ],
    "sales_goals": [
        40000 + i * 500 for i in range(96)
    ],
    "actual_cont_per": [75, 85, 80, 90] * 24,
    "budget_cont_per": [80, 90, 85, 95] * 24,
    "cont_per_achieve_tier": ["Tier 1", "Tier 2", "Tier 1", "Tier 3"] * 24
}

df = pd.DataFrame(data)

def login_page():
    st.sidebar.header("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    login_button = st.sidebar.button("Login")

    if login_button and username and password:
        st.session_state["logged_in"] = True
        st.sidebar.success("Logged in successfully!")
    elif login_button:
        st.sidebar.error("Please enter valid credentials.")
    st.title("My Eye Doctor")
    st.image("./Assets/MED.jpg")

def home_tab():
    st.title("My Eye Doctor")
    if st.button("SignOut"):
        st.session_state["logged_in"] = False
        st.experimental_rerun()  # Refresh the page when SignOut is clicked
    st.image("./Assets/MED.jpg")
    

def bonus_tab():
    st.sidebar.title("Bonus Tier Calculation Filters")

    # Filters
    time_view = st.sidebar.radio("Select Time View", ["Monthly", "Quarterly", "Yearly"])
    position = st.sidebar.selectbox("Select Position", ["Associate", "AGM", "GM"])

    col1, col2 = st.columns(2)
    with col1:
        office = st.selectbox("Select Office", df["office_name"].unique())
    with col2:
        # Ensure that the month selection is consistent with available months in filtered data
        available_months = df[df["office_name"] == office]["month"].unique()
        month = st.selectbox("Select Month", available_months)

    # Update sales_band to be numeric from 1 to 5
    df["sales_band"] = pd.Series([1, 2, 3, 4, 5] * 24)

    # Filter data by office
    filtered_data = df[df["office_name"] == office]

    # Handle time view aggregation
    if time_view == "Quarterly":
        filtered_data["quarter"] = filtered_data["month"].str[:4] + "-Q" + (
            (filtered_data["month"].str[5:7].astype(int) - 1) // 3 + 1
        ).astype(str)
    elif time_view == "Yearly":
        filtered_data["year"] = filtered_data["month"].str[:4]

    # Aggregation based on time view
    if time_view == "Monthly":
        # Filter data by selected month (check to avoid empty data after filtering)
        data_view = filtered_data[filtered_data["month"] == month]
        if data_view.empty:
            st.warning("No data available for the selected month.")
            return
    elif time_view == "Quarterly":
        # Aggregate numeric columns by quarter
        numeric_columns = ["actual_sales", "sales_goals", "actual_cont_per", "budget_cont_per"]
        data_view = filtered_data.groupby("quarter")[numeric_columns].mean().reset_index()
    elif time_view == "Yearly":
        # Aggregate numeric columns by year
        numeric_columns = ["actual_sales", "sales_goals", "actual_cont_per", "budget_cont_per"]
        data_view = filtered_data.groupby("year")[numeric_columns].mean().reset_index()

    # Display filtered data
    st.write(f"Filtered Data ({time_view} View):", data_view)

    # Calculate bonus tier based on actual sales and sales goals
    data_view["bonus_tier"] = (data_view["actual_sales"] / data_view["sales_goals"]) * 100

    # Display sliders for actual sales and sales goals
    col3, col4 = st.columns(2)
    with col3:
        actual_sales = st.slider(
            "Adjust Actual Sales", 
            min_value=20000, 
            max_value=80000, 
            value=int(data_view["actual_sales"].iloc[0]), 
            step=1000
        )

    with col4:
        sales_goals = st.slider(
            "Adjust Sales Goals", 
            min_value=20000, 
            max_value=80000, 
            value=int(data_view["sales_goals"].iloc[0]), 
            step=1000
        )

    # Simulated bonus tier calculation based on sliders
    data_view["simulated_bonus_tier"] = (actual_sales / sales_goals) * 100

    # Plotting the bonus tiers with respect to time view
    fig = go.Figure()

    # X-axis will vary based on the time view (monthly, quarterly, or yearly)
    if time_view == "Monthly":
        x_axis = data_view["month"]
    elif time_view == "Quarterly":
        x_axis = data_view["quarter"]
    elif time_view == "Yearly":
        x_axis = data_view["year"]

    fig.add_trace(go.Scatter(x=x_axis, 
                             y=data_view["bonus_tier"], 
                             mode='lines+markers', 
                             name='Original Bonus Tier',
                             line=dict(color='#4BD0FF')))
    fig.add_trace(go.Scatter(x=x_axis, 
                             y=data_view["simulated_bonus_tier"], 
                             mode='lines+markers', 
                             name='Simulated Bonus Tier', 
                             line=dict(dash='dot',  color='darkblue')))

    fig.update_layout(title=f"Bonus Tier Simulation ({time_view} View)",
                      xaxis_title="Time Period",
                      yaxis_title="Bonus Tier (%)",
                      legend_title="Bonus Tier",
                      template="plotly_white")

    st.plotly_chart(fig)
    st.write(f"Simulated actual sales: {actual_sales}, Simulated sales goals: {sales_goals}")


def instructions_tab():
    st.title("User Instructions")
    st.write("""1. Login using the sidebar with your credentials.""")
    st.write("""2. Navigate through the tabs to view Home, Bonus Tier Calculation, or Instructions.""")
    st.write("""3. In Bonus Tier Calculation, filter data using sidebar options to calculate and view bonus tiers.""")
    st.write("""4. Use sliders to simulate changes in actual sales and observe their impact on bonus tiers.""")
    st.write("""5. Switch between monthly, quarterly, or yearly views for better insights.""")


def main():
    st.markdown(
        """
        <style>
        .sidebar .sidebar-content {
            background-color: #ff914d;
        }
        .sidebar .sidebar-content a {
            color: white;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #0847AA;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    header_html = """
    <div style="background-color: #0847AA; padding: 10px; border-radius: 15px; margin-bottom: 20px;">
    <!-- <img src="https://mms.businesswire.com/media/20240325471163/en/2076915/5/MED_logo_WSYV_blue_grey.jpg"style="width: 100%; height: auto; border-radius: 10px;" /> -->
    <img src="https://media.licdn.com/dms/image/v2/C4E16AQFvv9gZE7jnnQ/profile-displaybackgroundimage-shrink_200_800/profile-displaybackgroundimage-shrink_200_800/0/1586208259986?e=2147483647&v=beta&t=n4oCq_IZQxcSc-hjVuurVBFWwLs7SPMltVkN88DI694"style="width: 100%; height: auto; border-radius: 10px;" />
    </div>
    """
    # st.image("./Assets/MED.jpg")
    st.markdown(header_html, unsafe_allow_html=True)
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        page_options = ["Home", "Bonus Tier Calculation","User Instruction"]
        selected_page = option_menu(None, page_options, icons=["user","user", "user"], orientation="horizontal")

        if selected_page == "Home":
            home_tab()
        elif selected_page == "Bonus Tier Calculation":
            bonus_tab()
        elif selected_page == "User Instruction":
            instructions_tab()
    else:
        login_page()


if __name__ == "__main__":
    main()        
