import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from streamlit_option_menu import option_menu

st.set_page_config(page_title="Employee Performance", page_icon="📈", layout="wide")

# Generate expanded dummy data
np.random.seed(42)
employees = [f"Emp_{i:03d}" for i in range(1, 21)]
employee_names = [f"Employee {i}" for i in range(1, 21)]
offices = ["MED-626 OH-Liberty", "MED-627 OH-Kensington", "MED-628 OH-Pittsburgh", "MED-629 OH-Beaver Falls"]
districts = ["District 103", "District 104", "District 105", "District 106"]
months = pd.date_range(start="2022-01", periods=12, freq="M").strftime("%Y-%m")

data = {
    "EmployeeDim[Emp Name and ID]": np.random.choice(employees, 100),
    "EmployeeDim[Employee Name]": np.random.choice(employee_names, 100),
    "edw v_MASTER_Office_Employee[OfficeNum & Office Name]": np.random.choice(offices, 100),
    "edw v_MASTER_Office_Employee[District_Number]": np.random.choice(districts, 100),
    "A_Adjusted_POS_Sales": np.random.rand(100) * 100000,
    "A___of_Sales": np.random.rand(100) * 100,
    "A_Commission": np.random.rand(100) * 10000,
    "A_Discounting": np.random.rand(100) * 5000,
    "A_Remake__": np.random.rand(100) * 3000,
    "A_Remake_Error_": np.random.rand(100) * 500,
    "A_Lens_Of_Choice_AR_": np.random.rand(100) * 2000,
    "A_Lens_Of_Choice_PROG_": np.random.rand(100) * 2000,
    "A_EO_": np.random.rand(100) * 100,
    "Month": np.random.choice(months, 100)
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
    st.title("MED Employee Performance Simulator")
    st.image("./Assets/MED.jpg")

def home_tab():
    st.title("MED Employee Performance Simulator")
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
    
def perf_tab():
    st.sidebar.title("Employee Performance Tracking Filters")

    # Filters
    employee_name = st.sidebar.text_input("Employee Name")
    commission = st.sidebar.number_input("Commission", min_value=0, max_value=10000, value=1000, step=100)
    discounting = st.sidebar.number_input("Discounting", min_value=0, max_value=5000, value=500, step=100)
    remake = st.sidebar.number_input("Remake", min_value=0, max_value=3000, value=300, step=50)
    lens_of_choice_ar = st.sidebar.number_input("Lens of Choice AR", min_value=0, max_value=3000, value=500, step=100)
    lens_of_choice_prog = st.sidebar.number_input("Lens of Choice PROG", min_value=0, max_value=3000, value=500, step=100)

    col1, col2, col3 = st.columns(3)
    with col1:
        office = st.selectbox("Select Office", df["edw v_MASTER_Office_Employee[OfficeNum & Office Name]"].unique())
    
    with col2:
        district = st.selectbox("Select District", df["edw v_MASTER_Office_Employee[District_Number]"].unique())

    with col3:
        month = st.selectbox("Select Month", df["Month"].unique())

    # Filter data
    filtered_data = df[
        (df["edw v_MASTER_Office_Employee[OfficeNum & Office Name]"] == office) &
        (df["edw v_MASTER_Office_Employee[District_Number]"] == district) &
        (df["Month"] == month)
    ]
    
    if employee_name:
        filtered_data = filtered_data[filtered_data["EmployeeDim[Employee Name]"].str.contains(employee_name, case=False, na=False)]

    st.write("Filtered Data:", filtered_data)

    # Simulate Employee Performance
    performance_simulated = filtered_data.copy()
    performance_simulated["Simulated Commission"] = performance_simulated["A_Commission"] + commission
    performance_simulated["Simulated Discounting"] = performance_simulated["A_Discounting"] + discounting
    performance_simulated["Simulated Remake"] = performance_simulated["A_Remake__"] + remake
    performance_simulated["Simulated Lens of Choice AR"] = performance_simulated["A_Lens_Of_Choice_AR_"] + lens_of_choice_ar
    performance_simulated["Simulated Lens of Choice PROG"] = performance_simulated["A_Lens_Of_Choice_PROG_"] + lens_of_choice_prog
    
    # Display top employee
    top_employee = performance_simulated.loc[performance_simulated["A___of_Sales"].idxmax(), ["EmployeeDim[Employee Name]", "A___of_Sales"]]
    
    col1, col2 = st.columns([3, 1])
    with col1:
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=performance_simulated["Month"], y=performance_simulated["Simulated Commission"], mode='lines+markers', name="Simulated Commission"))
        fig1.add_trace(go.Scatter(x=performance_simulated["Month"], y=performance_simulated["Simulated Discounting"], mode='lines+markers', name="Simulated Discounting"))
        fig1.add_trace(go.Scatter(x=performance_simulated["Month"], y=performance_simulated["Simulated Remake"], mode='lines+markers', name="Simulated Remake"))
        fig1.update_layout(title="Simulated Performance", xaxis_title="Month", yaxis_title="Amount", template="plotly_white")
        st.plotly_chart(fig1)

        fig2 = px.bar(performance_simulated, x="EmployeeDim[Employee Name]", y=["Simulated Commission", "Simulated Discounting", "Simulated Remake"], barmode="group", title="Performance Comparison")
        st.plotly_chart(fig2)
        
    with col2:
        st.subheader("Top Employee")
        st.write(f"**{top_employee['EmployeeDim[Employee Name]']}**")
        st.write(f"Sales: {top_employee['A___of_Sales']:.2f}")

    # Display simulated performance data
    st.write("Simulated Employee Performance:", performance_simulated)

    # Insights Section
    st.subheader("Insights")
    st.write(f"If Discounting was on Remake, then the Commission earned was highest in {month}.")

def instructions_tab():
    st.title("User Instructions")
    
    st.write("""### Welcome to the Employee Performance Simulator!""")
    
    st.write("""
    1. **Login**: Log in to the system using the credentials in the sidebar. Only authorized users can access the features.
    
    2. **Employee Performance Tracking**:
    - Navigate to the **Employee Performance Simulator** tab from the top menu to begin.
    - The main components in the **Employee Performance Tracking** tab include:
        - **Filters**:
            - Use the input fields on the sidebar to adjust values for **Commission**, **Discounting**, **Remake**, and **Lens of Choice**.
            - All these fields have dummy data pre-set, which you can change to simulate different scenarios for the employee's performance.
        
        - **Select Filters**: Choose the **Office**, **District**, and **Month** from the dropdowns.
            - The **Office** filter lets you select the office from which you want to view the data.
            - The **District** dropdown filters data based on the district number.
            - The **Month** dropdown allows you to select a specific month from which to view data.
        
        - **Simulating Performance**:
            - Once you have filtered the data based on your selections, you can simulate the employee's performance by adjusting the **Commission**, **Discounting**, **Remake**, and **Lens of Choice** values in the sidebar.
            - This will calculate and display the **simulated performance** of the employee, including the simulated values for commission, discounting, and remake.
        
        - **Charts**: 
            - **Line Charts**: These will show the simulated performance metrics (e.g., Commission, Discounting, Remake) over the selected time period (Monthly, Quarterly, or Yearly).
            - **Bar Charts**: Compare the simulated performance metrics for different employees within the selected filters.
            - **Trends Analysis**: Track how these values change over time.
        
        - **Insights**: 
            - Based on the selected filters and simulated performance data, insights like "If Discounting was on Remake, then the Commission earned was highest in the selected month" will be automatically generated.
            - These insights provide useful information for performance analysis and can help in making data-driven decisions for employee performance optimization.
        
    3. **Chart Descriptions**:
        - The **Line Chart** shows how simulated metrics like commission, discounting, and remake perform over time (monthly/quarterly/yearly).
        - The **Bar Chart** allows for easy comparison of simulated performance between employees in the same district and office.
        - The **Trend Chart** helps track performance over months for the given employee based on the simulated data.
        
    4. **Interaction**:
        - Interact with the filters and sliders to explore different scenarios.
        - Adjust the sliders for commission, discounting, remake, and lens of choice to see how the simulated performance changes.
        - Use the charts to visually interpret the employee’s performance and gain insights into their work patterns.
    """)

    st.write("""### Tips:
    - The **Simulated Performance** allows you to adjust parameters and visualize the potential impacts of commission, discounting, remake, and lens of choice on employee performance.
    - The insights generated can be particularly helpful in identifying which factors (e.g., discounting or remake) might be affecting commission most heavily in the selected month.
    - By analyzing the trends, you can predict the future performance or focus on improving specific areas.
    """)


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
        page_options = ["Home", "Employee Performance Simulator","User Instruction"]
        selected_page = option_menu(None, page_options, icons=["house","graph-up", "info"], orientation="horizontal")

        if selected_page == "Home":
            home_tab()
        elif selected_page == "Employee Performance Simulator":
            perf_tab()
        elif selected_page == "User Instruction":
            instructions_tab()
    else:
        login_page()


if __name__ == "__main__":
    main()        
