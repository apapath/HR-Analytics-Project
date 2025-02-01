# Import necessary libraries
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Page Config
st.set_page_config(page_title="Page 2", page_icon="💼", layout="wide")

# Set up filters
with st.sidebar:
	st.title("**Promotions & Lay-offs**")

# Data Importing and Proccessing----------------------------------------------------------------------------------------
df1 = pd.read_csv("./Data/Employee.csv")
df2 = pd.read_csv("./Data/PerformanceRating.csv")

# Merge the 2 datasets.
df = df1.merge(df2, how="inner", on="EmployeeID")

# Data Transformation
# Convert Hire Date and Review Date to datetime
df["HireDate"] = pd.to_datetime(df["HireDate"])
df["ReviewDate"] = pd.to_datetime(df["ReviewDate"])

# Metrics ---------------------------------------------------------------------------------------------------------------
# Retrencment and Promotion Rate
# Calculate the average ManagerRating for each EmployeeID 
df['AverageManagerRating'] = df.groupby('EmployeeID')['ManagerRating'].transform('mean')

# Find those who have >=8 years since their last promotion, manager rating 4 and above and are still in the company.
eligible_employees = df[ (df["YearsSinceLastPromotion"]>= 8) & (df["AverageManagerRating"]>=3.5) & (df["Attrition"]=="No") ]["EmployeeID"].unique()
# Create a new ToBePromoted column that marks those employs with Yes and everyone else with No.
df["ToBePromoted"] = df['EmployeeID'].apply(lambda x: 'Yes' if x in eligible_employees else 'No')

# Find those who have >=4 years since their last promotion, manager rating below 3 and are still in the company.
retrenched = df[  (df["YearsSinceLastPromotion"]>=4) & (df["AverageManagerRating"]<3) & (df["Attrition"]=="No") ]["EmployeeID"].unique()

# Create a new ToBeRetrenched column that marks those employs with Yes and everyone else with No.
df["ToBeRetrenched"] = df['EmployeeID'].apply(lambda x: 'Yes' if x in retrenched else 'No')

# Active Employees (Still working in the company)
active_df = df[ df["Attrition"]=="No" ]      # subset of dataset for Attrition=No
active = active_df["EmployeeID"].nunique()

# Calculate the promotion rate: ToBePromoted / all active employees
promotion_rate = 100 * active_df[ active_df["ToBePromoted"]=="Yes" ]["EmployeeID"].nunique() / active

# Calculate the retrenchment rate: ToBeRetrenched / all active employees
retrenchment_rate = 100 * active_df[ active_df["ToBeRetrenched"]=="Yes" ]["EmployeeID"].nunique() / active

# Set up columns
col1, col2, col3, col4 = st.columns(4)

# Display Headers and Metrics
with col1:
	st.header("To Be Retrenched")
with col2:
	with st.container(border=True):
		st.metric(label = "Percentage", value=f"{retrenchment_rate:.2f} %")	
with col3:
	st.header("To Be Promoted")
with col4:
	with st.container(border=True):
		st.metric(label = "Percentage", value=f"{promotion_rate:.2f} %")

# Visuals----------------------------------------------------------------------------------------------------------------

# Color pallette for graphs
neutrals=["#EDE6DB", "#C2A68C", "#5A3E36", "#2E8B57", "#556B2F"]

# 1: Employee Distribution by Role: Layoffs and Promotions
# Calculate total employees per role
total_employees = df.groupby("JobRole")["EmployeeID"].nunique().reset_index(name="Total")

# Group by role for layoff and promotion data
layoff_data = df.groupby(["JobRole", "ToBeRetrenched"])["EmployeeID"].nunique().reset_index(name="Count")
promotion_data = df.groupby(["JobRole", "ToBePromoted"])["EmployeeID"].nunique().reset_index(name="Count")

# Sort total employees in descending order
total_employees = total_employees.sort_values(by="Total", ascending=False)

# Store sorted order of JobRoles
sorted_roles = total_employees["JobRole"].tolist()

# Add a column to distinguish between layoff and promotion
layoff_data["Status"] = "Layoff"
promotion_data["Status"] = "Promotion"

# Rename columns for consistency
layoff_data.rename(columns={"ToBeRetrenched": "StatusFlag"}, inplace=True)
promotion_data.rename(columns={"ToBePromoted": "StatusFlag"}, inplace=True)

# Combine both datasets
combined_data = pd.concat([layoff_data, promotion_data])

# Merge with total employees to calculate percentages
combined_data = combined_data.merge(total_employees, on="JobRole")
combined_data["Role Percentage"] = (combined_data["Count"] / combined_data["Total"]) * 100

# Stacked bar chart 
fig = px.bar(combined_data, x="JobRole", y="Count", color="StatusFlag", facet_col="Status", barmode="stack",
                title="Employee Distribution by Role: Layoffs and Promotions",
                labels={"JobRole": "Role", "Count": "Number of Employees", "StatusFlag": "Status Flag"},
                text="Count", hover_data={"Role Percentage": ":.2f", "Total": True},
                color_discrete_sequence=neutrals[1:])

# Manually set category order based on sorted roles
fig.update_xaxes(categoryorder="array", categoryarray=sorted_roles)

# Set a y-axis range to make sure all bars are visible
max_count = combined_data["Count"].max()
fig.update_yaxes(range=[0, max_count * 1.3])

# Display chart
st.plotly_chart (fig)


# 2: Employee Distribution by Department: Layoffs and Promotions
# Calculate total employees per department
total_employees_dept = df.groupby("Department")["EmployeeID"].nunique().reset_index(name="Total")

# Group promotion and layoff data by department
layoff_data_dept = df.groupby(["Department", "ToBeRetrenched"])["EmployeeID"].nunique().reset_index(name="Count")
promotion_data_dept = df.groupby(["Department", "ToBePromoted"])["EmployeeID"].nunique().reset_index(name="Count")

# Add a column to distinguish between layoff and promotion
layoff_data_dept["Status"] = "Layoff"
promotion_data_dept["Status"] = "Promotion"

# Rename columns for consistency
layoff_data_dept.rename(columns={"ToBeRetrenched": "StatusFlag"}, inplace=True)
promotion_data_dept.rename(columns={"ToBePromoted": "StatusFlag"}, inplace=True)

# Combine both datasets
combined_data_dept = pd.concat([layoff_data_dept, promotion_data_dept])

# Merge with total employees to calculate percentages
combined_data_dept = combined_data_dept.merge(total_employees_dept, on="Department")
combined_data_dept["Department Percentage"] = (combined_data_dept["Count"] / combined_data_dept["Total"]) * 100

# Stacked bar chart
fig = px.bar(combined_data_dept, x="Department", y="Count", color="StatusFlag", facet_col="Status", barmode="stack",
            title="Employee Distribution by Department: Layoffs and Promotions",
            labels={"Department": "Department", "Count": "Number of Employees", "StatusFlag": "Status Flag"},
            text="Count", hover_data={"Department Percentage": ":.2f", "Total": True},
            color_discrete_sequence=neutrals[1:])

# Set a y-axis range to make sure all bars are visible
max_count = combined_data_dept["Count"].max()
fig.update_yaxes(range=[0, max_count * 1.3])

# Show graph
st.plotly_chart(fig)

# 3: Employee Distribution by Age Bracket: Layoffs and Promotions
# Group employees into age brackets
bins = [18, 25, 35, 45, 55, 65]  # Define age brackets
labels = ["18-25", "26-35", "36-45", "46-55", "56-65"]
df["AgeBracket"] = pd.cut(df["Age"], bins=bins, labels=labels, right=False)

# Calculate total employees in each age bracket
total_by_age = df.groupby("AgeBracket", observed=True)["EmployeeID"].nunique().reset_index(name="Total")

# Layoffs data for pie chart
layoff_age = df[df["ToBeRetrenched"] == "Yes"].groupby("AgeBracket", observed=True)["EmployeeID"].nunique().reset_index(name="Count")
layoff_age = layoff_age.merge(total_by_age, on="AgeBracket")
layoff_age["Age Bracket Percentage"] = (layoff_age["Count"] / layoff_age["Total"]) * 100

# Promotions data for pie chart
promotion_age = df[df["ToBePromoted"] == "Yes"].groupby("AgeBracket", observed=True)["EmployeeID"].nunique().reset_index(name="Count")
promotion_age = promotion_age.merge(total_by_age, on="AgeBracket")
promotion_age["Age Bracket Percentage"] = (promotion_age["Count"] / promotion_age["Total"]) * 100

# Layoff pie chart
fig_layoffs = px.pie(layoff_age, values="Count", names="AgeBracket",
                    title="Employee Distribution by Age Bracket: Layoffs",
                    labels={"AgeBracket": "Age Bracket", "Count": "Number of Layoffs"},
                    hover_data = {"Age Bracket Percentage": ":.2f"},
                    color_discrete_sequence=neutrals)


# Promotion pie chart
fig_promotions = px.pie(promotion_age, values="Count", names="AgeBracket",
                        title="Employee Distribution by Age Bracket: Promotions",
                        labels={"AgeBracket": "Age Bracket", "Count": "Number of Promotions"},
                        hover_data = {"Age Bracket Percentage": ":.2f"},
                        color_discrete_sequence=neutrals)

# Display the pie charts
col1, col2 = st.columns(2)
with col1:
	st.plotly_chart(fig_layoffs)
with col2:
	st.plotly_chart(fig_promotions)


# 4: Employee Distribution by Gender: Layoffs and Promotions
# Gender Distribution for Layoffs
layoff_gender = df[df["ToBeRetrenched"] == "Yes"].groupby("Gender")["EmployeeID"].nunique().reset_index(name="Count")
total_by_gender = df.groupby("Gender")["EmployeeID"].nunique().reset_index(name="Total")
layoff_gender = layoff_gender.merge(total_by_gender, on="Gender")
layoff_gender["Gender Percentage"] = (layoff_gender["Count"] / layoff_gender["Total"]) * 100

# Gender Distribution for Promotions
promotion_gender = df[df["ToBePromoted"] == "Yes"].groupby("Gender")["EmployeeID"].nunique().reset_index(name="Count")
promotion_gender = promotion_gender.merge(total_by_gender, on="Gender")
promotion_gender["Gender Percentage"] = (promotion_gender["Count"] / promotion_gender["Total"]) * 100

# Layoff Pie Chart
fig_layoff_gender = px.pie(layoff_gender, values="Count", names="Gender",
                            title="Employee Distribution by Gender: Layoffs",
                            hover_data={"Gender Percentage": ":.2f"},
                            labels={"Gender": "Gender", "Count": "Number of Layoffs"},
                            color_discrete_sequence=neutrals)

# Promotion Pie Chart
fig_promotion_gender = px.pie(promotion_gender,values="Count",names="Gender",
                            title="Employee Distribution by Gender: Promotions",
                            hover_data={"Gender Percentage": ":.2f"},
                            labels={"Gender": "Gender", "Count": "Number of Promotions"},
                            color_discrete_sequence=neutrals)

# Display Pie Charts
with col1:
	st.plotly_chart(fig_layoff_gender)
with col2:
	st.plotly_chart(fig_promotion_gender)


# 5: Employee Distribution by Tenure Group: Layoffs and Promotions
# Define tenure ranges
bins = [0, 2, 5, 10, float("inf")]
labels = ["0-2 years", "3-5 years", "6-10 years", "11-15 years" ]
df["TenureGroup"] = pd.cut(df["YearsAtCompany"], bins=bins, labels=labels, right=False)

# Group data by tenure group
layoff_data = df.groupby(["TenureGroup", "ToBeRetrenched"], observed=False)["EmployeeID"].nunique().reset_index(name="Count")
promotion_data = df.groupby(["TenureGroup", "ToBePromoted"], observed=False)["EmployeeID"].nunique().reset_index(name="Count")

# Add a column to distinguish between Layoffs and Promotions
layoff_data["Status"] = "Layoff"
promotion_data["Status"] = "Promotion"

# Rename columns for consistency
layoff_data.rename(columns={"ToBeRetrenched": "StatusFlag"}, inplace=True)
promotion_data.rename(columns={"ToBePromoted": "StatusFlag"}, inplace=True)

# Combine both datasets
combined_tenure_data = pd.concat([layoff_data, promotion_data])

# Calculate total employees in each tenure group
total_by_tenure = df.groupby("TenureGroup", observed=False)["EmployeeID"].nunique().reset_index(name="Total Employees")
combined_tenure_data = combined_tenure_data.merge(total_by_tenure, on="TenureGroup")

# Calculate the bracket percentage
combined_tenure_data["Bracket Percentage"] = (combined_tenure_data["Count"] / combined_tenure_data["Total Employees"]) * 100

# Create a stacked bar chart
fig_tenure_stack = px.bar(combined_tenure_data, x="TenureGroup", y="Count", color="StatusFlag", facet_col="Status", barmode="stack",
                            title="Employee Distribution by Tenure Group: Layoffs and Promotions",
                            labels={"TenureGroup": "Tenure Group", "Count": "Number of Employees", "StatusFlag": "Flag"},
                            hover_data={"Bracket Percentage": ":.2f", "Total Employees": True},
                            color_discrete_sequence=neutrals[1:])


# Layout adjustments for better visuals
fig_tenure_stack.update_layout(
    xaxis_title="Tenure Group",
    yaxis_title="Number of Employees",
    legend_title="Flag",
    margin=dict(t=80, b=40, l=40, r=40),  # Adjust margins for better spacing
    title=dict(x=0.5)  # Center the title
)

# Display the chart
st.plotly_chart(fig_tenure_stack)