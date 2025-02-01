# Import necessary libraries
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler

# Page Config
st.set_page_config(page_title="Page 4", page_icon="🧠", layout="wide")

# Data Importing and Proccessing----------------------------------------------------------------------------------------
df1 = pd.read_csv("../Data/Employee.csv")
df2 = pd.read_csv("../Data/PerformanceRating.csv")

# Merge the 2 datasets.
df = df1.merge(df2, how="inner", on="EmployeeID")

# Data Transformation
# Convert Hire Date and Review Date to datetime
df["HireDate"] = pd.to_datetime(df["HireDate"])
df["ReviewDate"] = pd.to_datetime(df["ReviewDate"])

# For each unique employee id find the last review date and use it in a new column.
df['LastReview'] = df.groupby('EmployeeID')['ReviewDate'].transform('max')

# Extract Year from Hire Date and Last Review
df["HireYear"] = df["HireDate"].dt.year
df["LastReview"] = df["LastReview"].dt.year

# Drop the YearsAtCompany column because it contains mistakes. We will calculate the metric on our own.
df = df.drop(columns=['YearsAtCompany'])

# Create Tenure column. 
df["Tenure"] = df["LastReview"] - df["HireYear"]
df["Tenure"] = df["Tenure"].apply(lambda x: np.nan if x < 0 else x)

# Create AttritionNumerical column.
df["AttritionNumerical"] = df["Attrition"].map({"Yes": 1, "No": 0})

# Model Development ----------------------------------------------------------------------------------

# Based on our correlation analysis we will choose the following variables for our model:
categ = ['JobRole',  'OverTime',  'MaritalStatus']
numer =  ['Tenure',	'Age', 'YearsWithCurrManager', 'YearsInMostRecentRole', 'YearsSinceLastPromotion']

chosen_columns = categ + numer + ['AttritionNumerical']

# Grouping our df by EmployeeID and aggregating relevant columns
df_grouped = df.groupby('EmployeeID').agg({
    'Tenure': 'mean', 
    'Age': 'mean',    
    'YearsWithCurrManager': 'mean',
    'YearsInMostRecentRole': 'mean',
    'YearsSinceLastPromotion': 'mean',
    'AttritionNumerical': 'max',  
    'JobRole': 'last',   
    'OverTime': 'last',  
    'MaritalStatus': 'last',  
})

df_chosen =  df_grouped[chosen_columns]

# One-hot encoding for categorical variables
df_encoded = pd.get_dummies(df_chosen, columns=categ)

# Handle missing data
df_encoded.dropna(inplace=True)

# Now we are ready to split our data.

# Separate the features (X) and target variable (y)
X = df_encoded.drop(columns=['AttritionNumerical'])
y = df_encoded['AttritionNumerical']

# Training and testing sets (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize the scaler
scaler = StandardScaler()

# Scale the training and test data and assign back to the original variable names
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Logistic Regression Model

# Initialize Logistic Regression
model_lr = LogisticRegression(class_weight={0: 1, 1: 1}, random_state=42, max_iter=1000)

# Train the model on the training data
model_lr.fit(X_train, y_train)

# Make predictions on the test set
y_pred_lr = model_lr.predict(X_test)

# Function to make predictions
def predict_attrition(data):
    
    # Scale the input data using the same scaler as before
    data_scaled = scaler.transform(data)
    
    # Make the prediction and get the probability
    prediction = model_lr.predict(data_scaled)
    prob = model_lr.predict_proba(data_scaled)[0][1]

    return prediction, prob

# Expected feature order (from training)
expected_columns = ['Tenure', 
                    'Age', 
                    'YearsWithCurrManager', 
                    'YearsInMostRecentRole',
                    'YearsSinceLastPromotion', 
                    'JobRole_Analytics Manager', 
                    'JobRole_Data Scientist',
                    'JobRole_Engineering Manager', 
                    'JobRole_HR Business Partner',
                    'JobRole_HR Executive', 
                    'JobRole_HR Manager',
                    'JobRole_Machine Learning Engineer', 
                    'JobRole_Manager',
                    'JobRole_Recruiter', 
                    'JobRole_Sales Executive',
                    'JobRole_Sales Representative', 
                    'JobRole_Senior Software Engineer',
                    'JobRole_Software Engineer', 
                    'OverTime_No', 
                    'OverTime_Yes',
                    'MaritalStatus_Divorced', 
                    'MaritalStatus_Married',
                    'MaritalStatus_Single']

# Dashboard Building ---------------------------------------------------------------------------------------------------
# Page Title
st.header("Employee Attrition Prediction Model")

# Brief intro
st.markdown("This model predicts the probability of an employee staying or leaving based on various factors such as tenure, job role, years in role/with current manager/since last promotion, overtime, and marital status.")

# Set up columns
col1, col2 = st.columns(2)

with col2: 
	# Input fields for the user to provide data in streamlit
	tenure = st.slider("Years in the Company", min_value=0, max_value=50, step=1)
	age = st.slider('Age', min_value=18, max_value=70, step=1)
	years_with_curr_manager = st.slider('Years under Current Manager', min_value=0, max_value=50, step=1)
	years_in_most_recent_role = st.slider('Years in Most Recent Role', min_value=0, max_value=50, step=1)
	years_since_last_promotion = st.slider('Years Since Last Promotion', min_value=0, max_value=50, step=1)

with col1: 
	job_role = st.radio('Job Role', options=['Analytics Manager', 'Data Scientist', 'Engineering Manager', 'HR Business Partner', 'HR 	Executive', 'HR Manager', 'Machine Learning Engineer', 'Manager', 'Recruiter', 'Sales 	Executive', 'Sales Representative', 'Senior Software Engineer', 'Software Engineer'])
	overtime = st.checkbox('Overtime')
	marital_status = st.radio('Marital Status', options=['Married', 'Single', 'Divorced'])


# Encode categorical variables and create the input data for prediction
input_data = {
    'Tenure': tenure,
    'Age': age,
    'YearsWithCurrManager': years_with_curr_manager,
    'YearsInMostRecentRole': years_in_most_recent_role,
    'YearsSinceLastPromotion': years_since_last_promotion,
    'JobRole_Analytics Manager': 1 if job_role == 'Analytics Manager' else 0,
    'JobRole_Data Scientist': 1 if job_role == 'Data Scientist' else 0,
    'JobRole_Engineering Manager': 1 if job_role == 'Engineering Manager' else 0,
    'JobRole_HR Business Partner': 1 if job_role == 'HR Business Partner' else 0,
    'JobRole_HR Executive': 1 if job_role == 'HR Executive' else 0,
    'JobRole_HR Manager': 1 if job_role == 'HR Manager' else 0,
    'JobRole_Machine Learning Engineer': 1 if job_role == 'Machine Learning Engineer' else 0,
    'JobRole_Manager': 1 if job_role == 'Manager' else 0,
    'JobRole_Recruiter': 1 if job_role == 'Recruiter' else 0,
    'JobRole_Sales Executive': 1 if job_role == 'Sales Executive' else 0,
    'JobRole_Sales Representative': 1 if job_role == 'Sales Representative' else 0,
    'JobRole_Senior Software Engineer': 1 if job_role == 'Senior Software Engineer' else 0,
    'JobRole_Software Engineer': 1 if job_role == 'Software Engineer' else 0,
    'OverTime_No': 1 if overtime == False else 0,
    'OverTime_Yes': 1 if overtime == True else 0,
    'MaritalStatus_Divorced': 1 if marital_status == 'Divorced' else 0,
    'MaritalStatus_Married': 1 if marital_status == 'Married' else 0,
    'MaritalStatus_Single': 1 if marital_status == 'Single' else 0
}

# Convert dictionary to a pandas DataFrame and ensure column order matches the training set
input_df = pd.DataFrame(input_data, index=[0])

# Reorder the columns to match the expected order from training
input_df = input_df[expected_columns]

# Prediction button
with st.container(border=True):
	if st.button('Predict Attrition'):
    		prediction, prob = predict_attrition(input_df)
    		if prediction == 1:
        		st.subheader(f"The model predicts the employee will leave with a probability of {100*prob:.2f}%.")
    		else:
        		st.subheader(f"The model predicts the employee will stay with a probability of {100 - 100*prob:.2f}%.")