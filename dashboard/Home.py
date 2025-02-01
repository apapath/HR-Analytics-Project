import streamlit as st
from streamlit_extras import add_vertical_space as avs 

# Page Config
st.set_page_config(page_title="Home Page", page_icon="🏠", layout="wide")

# Page Header
st.title("Welcome to the HR Analytics Project Interactive Dashboard")

col1, col2 = st.columns(2)

with col1:
	
	st.write("### Dashboard Overview")
	st.write("""
	- **Page 1**: A workforce demographics dashboard showcasing key metrics.
	- **Page 2**: A promotions and layoffs dashboard for tracking goals and department-level metrics.
	- **Page 3**: An attrition analysis dashboard.
	- **Page 4**: An attrition prediction model developed by our team.
	""")

	avs.add_vertical_space(1) 

	st.image("https://cdn2.fptshop.com.vn/unsafe/1920x0/filters:quality(100)/2023_10_13_638327858006688384_hr-la-gi-1.jpg", width = 400)


with col2: 
	 
	st.subheader("Analysis Objectives")
	st.markdown("""
	Leverage anonymized employee data to uncover actionable insights that will guide HR strategies in:
	- Workforce Management
	- Employee Retention
	- Strategic Hiring""")

	avs.add_vertical_space(2) 

	st.subheader("Goals:")
	st.markdown(""" 
	- Enhance HR decision-making with data-driven insights.
	- Develop retention strategies based on employee trends.
	- Optimize hiring efforts to align with business needs.""")


# Connect with us section
st.subheader("Connect with us!")

with st.container(border=True):
	col1, col2, col3 = st.columns(3)
	with col1:
		st.markdown("""
		#### **Andriani Papatheodoropoulou**  
		**BSc Chemistry**  """)
		st.image("https://drive.google.com/file/d/1Q1HLPf4NN13tJ0Rc5bZ6QPF-fPZ3lt3X/view", width=400)

	with col2:
		st.markdown("""
		#### **Androniki Paragyiou**  
		**BSc Economics**  """)
		st.image("C:/Users/andri/OneDrive/Desktop/github_apath/HR-Analytics-Project/Data/androniki plus qr.jpg", width=400)

	with col3:
		st.markdown("""
		#### **Nikolas Bourantas**  
		**MSc Agricultural Economics and Rural Development**  """)
		st.image("C:/Users/andri/OneDrive/Desktop/github_apath/HR-Analytics-Project/Data/nikolas plus qr.jpg", width=400)

