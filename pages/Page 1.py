# Import necessary libraries
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Page Config
st.set_page_config(page_title="Page 1", page_icon="https://static-00.iconduck.com/assets.00/demographic-icon-2048x1908-4opu48c0.png", layout="wide")

# Data Importing and Proccessing----------------------------------------------------------------------------------------
df1 = pd.read_csv("./Data/Employee.csv")
df2 = pd.read_csv("./Data/PerformanceRating.csv")

# Merge the 2 datasets.
df = df1.merge(df2, how="inner", on="EmployeeID")

# Data Transformation
# Convert Hire Date and Review Date to datetime
df["HireDate"] = pd.to_datetime(df["HireDate"])
df["ReviewDate"] = pd.to_datetime(df["ReviewDate"])

# Filters ----------------------------------------------------------------------------------------------------

# Set up filters
with st.sidebar:
	st.title("**Workforce Demographics**")
	st.title("Dashboard Filters ⚙️ ")	

	# Slicer: Select a department
	selected_department = st.multiselect("Select Department", df["Department"].unique())

	# Slicer: Select gender
	selected_gender = st.multiselect("Select Gender", df["Gender"].unique())

	# Slicer: Select employee status
	selected_status = st.multiselect("Select Employee Status ", ["Active", "Inactive"])

# Filter logic implementation
# Filters for department
if selected_department:
	filtered_df = df[ df["Department"].isin(selected_department) ]
else:
	filtered_df = df

# Filters for gender
if selected_gender:
	filtered_df = filtered_df[ filtered_df["Gender"].isin(selected_gender) ]

# Filters for employee status:
if selected_status:
    if selected_status == ["Active"]:
        selected_status = ["No"]
    elif selected_status == ["Inactive"]:
        selected_status = ["Yes"]
    filtered_df = filtered_df[filtered_df["Attrition"].isin(selected_status)]

# Metrics -------------------------------------------------------------------------------------------------

# Total employees 
all_employees = filtered_df["EmployeeID"].nunique()

# Attrition Rate
# Inactive Employees (Not working in the company now)
inactive_df = filtered_df[ filtered_df["Attrition"]=="Yes" ]      # subset of dataset for Attrition=Yes
inactive = inactive_df["EmployeeID"].nunique()   # unique employee IDs in subset = inactive employees

# Calculate the attrition rate: inactive / all_employees
attrition_rate = 100 * inactive / all_employees

# Average salary (company-wide)
average_employee_salary = filtered_df.groupby('EmployeeID')['Salary'].mean()
average_salary = average_employee_salary.mean()

# Set up columns
col1, col2, col3 = st.columns(3)

# Metric Cards
with col1:
	with st.container(border=True):
		st.metric(label="Total Employees:", value=f"{all_employees}")

with col2:
	with st.container(border=True):
		st.metric(label="Attrition Rate", value=f"{attrition_rate:.2f}%")

with col3:
	# Average salary
	average_employee_salary = filtered_df.groupby('EmployeeID')['Salary'].mean()
	average_salary = average_employee_salary.mean()
	with st.container(border=True):
		st.metric(label="Average Salary", value = f"{average_salary:,.0f} $")

# Visuals----------------------------------------------------------------------------------------------

# Color pallette for graphs
neutrals=["#EDE6DB", "#C2A68C", "#5A3E36", "#2E8B57", "#556B2F"]

# Set up columns - Row1
col1, col2, col3 = st.columns(3)

with col1:
	# Gender distribution pie chart
	gender_company = filtered_df.groupby("Gender")["EmployeeID"].nunique().reset_index(name="Count")
	fig = px.pie(gender_company, names="Gender", values="Count", title="Employee Distribution by Gender", color_discrete_sequence=neutrals)
	st.plotly_chart(fig)

with col2:
	# Employee Distribution by Tenure 
	# Define tenure ranges
	bins = [0, 2, 5, 10, float("inf")]
	labels = ["0-2 years", "3-5 years", "6-10 years", "11-15 years" ]
	filtered_df["TenureGroup"] = pd.cut(filtered_df["YearsAtCompany"], bins=bins, labels=labels, right=False)
	# Calculate total employees in each tenure group
	tenure_distr = filtered_df.groupby("TenureGroup", observed=True)["EmployeeID"].nunique().reset_index(name="Number of Employees")
	# Create a stacked bar chart
	fig = px.bar(tenure_distr, x="TenureGroup", y="Number of Employees", 
                            title="Employee Distribution by Tenure",
                            color_discrete_sequence=neutrals[1:])
	st.plotly_chart(fig)

with col3:
	# Marital status breakdown pie chart.
	status_company = filtered_df.groupby("MaritalStatus")["EmployeeID"].nunique().reset_index(name="Count")
	fig = px.pie(status_company, names="MaritalStatus", values="Count", title="Employee Distribution by Marital Status", color_discrete_sequence=neutrals)
	st.plotly_chart(fig)


# Set up columns - Row2
col1, col2 = st.columns(2)

with col1:
	# Salary distribution histogram
	average_employee_salary = filtered_df.groupby('EmployeeID')['Salary'].mean()
	salary_df = average_employee_salary.reset_index()
	fig = px.histogram(salary_df, x="Salary", title="Employee Distribution by Salary", histnorm="percent", nbins=100, marginal="box", color_discrete_sequence=neutrals[1:2])
	fig.update_layout(bargap=0.1, yaxis_title="Percentage (%)")
	st.plotly_chart(fig)

with col2:
	# Age distribution bar chart
	age_company = filtered_df.groupby("Age")["EmployeeID"].nunique().reset_index(name="Count")
	fig = px.bar(age_company, "Age", "Count", title="Employee Distribution by Age", color_discrete_sequence=neutrals[1:2])
	st.plotly_chart(fig)