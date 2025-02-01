# Import necessary libraries
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Page Config
st.set_page_config(page_title="Page 3", page_icon="📈", layout="wide")

# Data Importing and Proccessing----------------------------------------------------------------------------------------
df1 = pd.read_csv("C:/Users/andri/OneDrive/Desktop/hr-analytics/Data/Employee.csv")
df2 = pd.read_csv("C:/Users/andri/OneDrive/Desktop/hr-analytics/Data/PerformanceRating.csv")

# Merge the 2 datasets.
df = df1.merge(df2, how="inner", on="EmployeeID")

# Data Transformation
# Convert Hire Date and Review Date to datetime
df["HireDate"] = pd.to_datetime(df["HireDate"])
df["ReviewDate"] = pd.to_datetime(df["ReviewDate"])

# Filters ----------------------------------------------------------------------------------------------------

# Set up filters
with st.sidebar:
	st.title("**Attrition Analysis**")
	st.title("Dashboard Filters ⚙️ ")

	# Slicer: Select a department
	selected_department = st.multiselect("Select Department", df["Department"].unique())

	# Slicer: Select gender
	selected_gender = st.multiselect("Select Gender", df["Gender"].unique())

	# Slicer: Select employee status
	selected_location = st.multiselect("Select Location ", df["State"].unique())


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
if selected_location:
	filtered_df = filtered_df[ filtered_df["State"].isin(selected_location) ]


# Metrics -------------------------------------------------------------------------------------------------

# Attrition Rate
# Total employees 
all_employees = filtered_df["EmployeeID"].nunique()
all_female = filtered_df[filtered_df["Gender"]=="Female" ]["EmployeeID"].nunique()
all_male = filtered_df[filtered_df["Gender"]=="Male" ]["EmployeeID"].nunique()

# Inactive Employees (Not working in the company now)
inactive_df = filtered_df[ df["Attrition"]=="Yes" ].copy()      # subset of dataset for Attrition=Yes
inactive = inactive_df["EmployeeID"].nunique()   # unique employee IDs in subset = inactive employees

# Calculate the attrition rate: inactive / all_employees
attrition_rate = 100 * inactive / all_employees

# Calculate percentage of attrition in women 
inactive_women = inactive_df[ inactive_df["Gender"]=="Female"]["EmployeeID"].nunique()
try:
	attrition_women = 100 * inactive_women / all_female
except ZeroDivisionError:
	attrition_women = 0

# Calculate percentage of attrition in men
inactive_men = inactive_df[ inactive_df["Gender"]=="Male"]["EmployeeID"].nunique()
try:
    attrition_men = 100 * inactive_men / all_male
except ZeroDivisionError:
    attrition_men = 0

# Set up columns for metrics
col1, col2, col3 = st.columns(3)

with col1: 
	with st.container(border=True):
		st.metric(label="Attrition Rate", value = f"{attrition_rate:.2f}%")

with col2:
	with st.container(border=True):
		st.metric(label="Female Attrition Rate", value = f"{attrition_women:.2f}%")

with col3:
	with st.container(border=True):
		st.metric(label="Male Attrition Rate", value = f"{attrition_men:.2f}%")

# Visuals----------------------------------------------------------------------------------------------
# Color pallette for graphs
neutrals=["#EDE6DB", "#C2A68C", "#5A3E36", "#2E8B57", "#556B2F"]

# Set up columns for visuals
col1, col2, col3 = st.columns(3)

with col1:
	# Attrition by Tenure
	tenure_attrition = inactive_df.groupby("YearsAtCompany")["EmployeeID"].nunique().reset_index(name="Count")
	fig = px.bar(tenure_attrition, y="YearsAtCompany", x="Count", title="Attrition by Tenure", orientation="h", color_discrete_sequence=neutrals[0:])
	st.plotly_chart(fig)

	# Attrition by Age
	# Group employees into age brackets
	bins = [18, 25, 35, 45, 55, 65]
	labels = ["18-25", "26-35", "36-45", "46-55", "56-65"]
	inactive_df["AgeBracket"] = pd.cut(inactive_df["Age"], bins=bins, labels=labels, right=False)
	# Pie chart for percentage of inactive employees per age bracket
	age_attrition = inactive_df.groupby("AgeBracket", observed=True)["EmployeeID"].nunique().reset_index(name="Count")
	# Create a pie chart
	fig = px.pie(age_attrition, names="AgeBracket", values="Count", title="Attrition by Age Bracket", color_discrete_sequence=neutrals)
	st.plotly_chart(fig)

	# Attrition by Distance
	# Group employees into Distance brackets
	bins = [0, 5, 15, 25, 35, 45]
	labels = ["Very Short", "Short", "Medium", "Long", "Very Long"]
	inactive_df["DistanceBracket"] = pd.cut(inactive_df["DistanceFromHome (KM)"], bins=bins, labels=labels, right=False)
	distance_attrition = inactive_df.groupby("DistanceBracket", observed=True)["EmployeeID"].nunique().reset_index(name="Count")
	# Bar Chart for number of inactive employees per Distance Bracket
	fig = px.bar(distance_attrition, y="DistanceBracket", x="Count", title="Attrition by Distance From Home (km)", 	color_discrete_sequence=neutrals[1:])
	st.plotly_chart(fig)

with col2:
	# Attrition by Education
	# Group inactive employees by education level and calculate the count
	education_attrition = inactive_df.groupby("Education")["EmployeeID"].nunique().reset_index(name="Count")
	# Map education levels to their descriptions
	education_level = {
    1: "No Formal Qualifications",
    2: "High School",
    3: "Bachelor's",
    4: "Master's",
    5: "Doctorate"}
	education_attrition["Education"] = education_attrition["Education"].map(education_level)
	# Bar chart for attrition by education level
	fig = px.pie(education_attrition, names="Education", values="Count", title="Attrition by Education", 
                color_discrete_sequence= neutrals[1:])
	# Show the chart
	st.plotly_chart(fig)
	
	# Attrition by Overtime
	overtime_attrition = inactive_df.groupby("OverTime")["EmployeeID"].nunique().reset_index(name="Count")
	# Pie Chart for percentage of inactive employees by overtime
	fig = px.pie(overtime_attrition, names="OverTime", values="Count", title="Attrition by Overtime", color_discrete_sequence=neutrals)
	st.plotly_chart(fig)

	# Attrition by Job Satisfaction
	# Group by Job Satisfaction Level and map an explanatory dictionary
	attrition_satisfaction = inactive_df.groupby("JobSatisfaction")["EmployeeID"].nunique().reset_index(name="Count")
	satisfaction_level = {1:"Very Dissatisfied",
                      2:"Dissatisfied",
                      3:"Neutral",
                      4:"Satisfied", 
                      5:"Very Satisfied"}
	attrition_satisfaction["JobSatisfaction"] = attrition_satisfaction["JobSatisfaction"].map(satisfaction_level)
	# Bar chart for number of inactive employees per job satisfaction level
	fig = px.bar(attrition_satisfaction, x="JobSatisfaction", y="Count", title="Attrition by Job Satisfaction", color_discrete_sequence=neutrals[1:])
	st.plotly_chart(fig)

with col3:

	# Attrition by Job Role
	job_attrition = inactive_df.groupby("JobRole")["EmployeeID"].nunique().reset_index(name="Count")
	# Bar Chart for number of inactive employees per Job Role
	fig = px.bar(job_attrition, y="JobRole", x="Count", title="Attrition by Job Role", color_discrete_sequence= neutrals[1:])
	st.plotly_chart(fig)

	# Attrition by Stock Options
	stock_attrition = inactive_df.groupby("StockOptionLevel")["EmployeeID"].nunique().reset_index(name="Count")
	# Bar Chart for count of inactive employees by stock options
	fig = px.bar(stock_attrition, x="StockOptionLevel", y="Count", title="Attrition by Stock Option Level", color_discrete_sequence= neutrals[1:])
	st.plotly_chart(fig)

	# Attrition by employee average salary
	# Calculate the average salary for each employee
	average_employee_salary_inactive = inactive_df.groupby('EmployeeID')['Salary'].mean()
	salary_df = average_employee_salary_inactive.reset_index()
	# Histogram for attrition by salary
	fig = px.histogram(salary_df, x="Salary", title="Attrition by Salary", histnorm="percent", nbins=100, marginal="box", color_discrete_sequence= neutrals[0:])
	fig.update_layout(bargap=0.1)
	st.plotly_chart(fig)