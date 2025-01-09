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
    st.title("MED Bonus Simulator")
    st.image("./Assets/MED.jpg")

def home_tab():
    st.title("MED Bonus Simulator")
    img_html = """
    <div style="background-color: white; padding: 10px; border-radius: 15px; margin-bottom: 20px;">
    <!-- <img src="https://mms.businesswire.com/media/20240325471163/en/2076915/5/MED_logo_WSYV_blue_grey.jpg"style="width: 100%; height: auto; border-radius: 10px;" /> -->
    <img src="https://d2q79iu7y748jz.cloudfront.net/s/_customcontent/0fd10b3309d47d6f5006b2700ba70b31"style="width: 100%; height: auto; border-radius: 10px; filter: brightness(0.8);" />
    </div>
    """
    st.markdown(img_html, unsafe_allow_html=True)
    if st.button("SignOut"):
        st.session_state["logged_in"] = False
        st.experimental_rerun()  
    

def bonus_tab():
    st.sidebar.title("Bonus Tier Calculation Filters")

    # Filters
    time_view = st.sidebar.radio("Select Time View", ["Monthly", "Quarterly", "Yearly"])
    position = st.sidebar.selectbox("Select Position", ["Associate", "AGM", "GM"])

    col1, col2 = st.columns(2)
    with col1:
        office = st.selectbox("Select Office", df["office_name"].unique())
    
    # Prepare month dropdown with human-readable format
    filtered_months = df[df["office_name"] == office]["month"].unique()
    formatted_months = pd.to_datetime(filtered_months).strftime("%B %Y")  # e.g., "January 2022"
    month_mapping = dict(zip(formatted_months, filtered_months))  # Map formatted to original values

    with col2:
        # Display dropdown with formatted month names
        selected_month = st.selectbox("Select Month", formatted_months)
        month = month_mapping[selected_month]  # Convert back to the original format

    # Filter data based on office and selected month
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
        data_view = filtered_data[filtered_data["month"] == month]
        if data_view.empty:
            st.warning("No data available for the selected month.")
            return
    elif time_view == "Quarterly":
        numeric_columns = ["actual_sales", "sales_goals", "actual_cont_per", "budget_cont_per"]
        data_view = filtered_data.groupby("quarter")[numeric_columns].mean().reset_index()
    elif time_view == "Yearly":
        numeric_columns = ["actual_sales", "sales_goals", "actual_cont_per", "budget_cont_per"]
        data_view = filtered_data.groupby("year")[numeric_columns].mean().reset_index()

    # Display filtered data
    st.write(f"Filtered Data ({time_view} View):", data_view)

    # Calculate bonus tier
    data_view["bonus_tier"] = (data_view["actual_sales"] / data_view["sales_goals"]) * 100

    # Sliders for simulation
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

    # Simulated bonus tier calculation
    data_view["simulated_bonus_tier"] = (actual_sales / sales_goals) * 100


    bonus_lookup = {
        0: {"Associate": 0, "AGM": 0, "GM": 0},
        1: {"Associate": 250, "AGM": 500, "GM": 1000},
        2: {"Associate": 300, "AGM": 600, "GM": 1200},
        3: {"Associate": 500, "AGM": 750, "GM": 1500},
        4: {"Associate": 800, "AGM": 1200, "GM": 2000}
    }

    # Determine bonus tier and bonus amount
    simulated_bonus_tier = int(data_view["simulated_bonus_tier"].iloc[0] // 100)  # Assuming tiers are integers
    bonus_amount = bonus_lookup.get(simulated_bonus_tier, {"Associate": 0, "AGM": 0, "GM": 0}).get(position, 0)

    # Display the bonus statement
    st.subheader("Bonus Information")
    st.write(f"The Bonus amount for the **{position}** with the bonus **tier {simulated_bonus_tier}** is **{bonus_amount}** $.")

    # Plotting bonus tiers
    fig = go.Figure()
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
                             line=dict(dash='dot', color='darkblue')))

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
    st.markdown(header_html, unsafe_allow_html=True)
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        page_options = ["Home", "Bonus Tier Calculation","User Instruction"]
        selected_page = option_menu(None, page_options, icons=["house","graph-up", "info"], orientation="horizontal")

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
