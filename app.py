import streamlit as st
import pandas as pd
import seaborn as sns
import plotly.express as px
import numpy as np
import calendar



st.set_page_config(page_title="Memebership  Dashboard",
                   page_icon=":barchart",
                   layout='wide')


@st.cache_data
def load_data():
    df=pd.read_csv('membership.csv')
    return df

df=load_data()
df=df.iloc[:,1:]
## create a date column to strip off the time
df['date']=pd.to_datetime(df.date_order).dt.date
df['year']=pd.to_datetime(df['date_order']).dt.year
df['month']=pd.to_datetime(df['date_order']).dt.month

# Convert the 'dob' column to datetime format
df['beneficiary_dob'] = pd.to_datetime(df['beneficiary_dob'])
df['dependent_dob'] = pd.to_datetime(df['dependent_dob'])


# Calculate current date
current_date = pd.Timestamp('today')

# Calculate age by subtracting DOB from the current date and dividing by timedelta of one year
df['beneficiary_age'] = ((current_date - df['beneficiary_dob']).dt.days / 365.25)
df['dependent_age'] = ((current_date - df['dependent_dob']).dt.days / 365.25)

df['beneficiary_age'].fillna(value=-1,inplace=True)
df['beneficiary_age']=df['beneficiary_age'].astype(int)
df['dependent_age'].fillna(value=-1,inplace=True)
df['dependent_age']=df['dependent_age'].astype(int)

# Assuming you have a DataFrame named 'df' with columns: template_id, beneficiary_age, dependent_age

def get_consultation_type(row):
    template_id = row['product_template_id']
    beneficiary_age = row['beneficiary_age']
    dependent_age = row['dependent_age']

    if template_id == 3179:
        return 'Doctor Consultation'
    elif template_id == 7844:
        return 'Dental Consultation'
    elif template_id == 18449:
        return 'Eye Consultation'
    elif (beneficiary_age <= 5 or dependent_age <= 5) and template_id in [3534, 3538, 3541, 3539, 5338, 3537, 3542, 3535, 5337, 7866, 7886]:
        return 'Immunization/Vaccination'
    else:
        return None  # Return None for cases not covered by your conditions

# Apply the custom function to create a new column 'consultation_type' in the DataFrame
df['consultation_type'] = df.apply(get_consultation_type, axis=1)

# Now you have a new column 'consultation_type' in your DataFrame with the corresponding values based on the conditions



# Assuming you have a DataFrame named 'df' with a column 'product_template_id'
conditions = [
    (df['product_template_id'] == 3185),
    (df['product_template_id'] == 5205),
    (df['product_template_id'] == 18345),
    (df['product_template_id'] == 31395),
    (df['product_template_id'] == 18344),
    (df['product_template_id'] == 31277),
    (df['product_template_id'] == 31289),
    (df['product_template_id'] == 8121),
    (df['product_template_id'] == 8123),
    (df['product_template_id'] == 8124),
    (df['product_template_id'] == 8122)
]

choices = [
    'ECG',
    'Vision Check',
    'Dental Check',
    'Dental Check',
    'Dental Check',
    'Home Care',
    'Ambulance',
    'Anual Health Check',
    'Anual Health Check',
    'Anual Health Check',
    'Anual Health Check'
]

# Create a new column 'template_category' based on the conditions and choices
df['limited_benefit'] = np.select(conditions, choices, default=None)
df['estimated_savings']=(df['actual_amount']/ (1 - 0.20))-(df['actual_amount'])



st.sidebar.header('please filter here')
primary_holder=st.sidebar.selectbox(
    "Select the beneficiary Gender",
    options=df['primary_holder'].unique(),
    #default='EHA Clinics Limited'


)

df_selection=df.query(
    'primary_holder==@primary_holder'
)

year=st.sidebar.radio(
    "Membership Plan",
    options=df_selection['year'].unique(),
    #default=2023

)


df_selection=df.query(
    'year==@year & primary_holder==@primary_holder'
)




st.dataframe(df_selection)

## Main Page
st.title("EHA Membership Dashboard")
st.markdown('##')

# interesting KPIs
total_ben=df_selection.total_qty.iloc[0]
if total_ben==0:
    total_ben=1
   
used_dental=df_selection.query('limited_benefit == "Dental Check"')['limited_benefit'].count()
used_vision=df_selection.query('limited_benefit == "Vision Check"')['limited_benefit'].count()
used_ambulance=df_selection.query('limited_benefit == "Ambulance"')['limited_benefit'].count()
used_home=df_selection.query('limited_benefit == "Home Care"')['limited_benefit'].count()
used_ahc=df_selection.query('limited_benefit == "Anual Health Check"')['limited_benefit'].count()

used_ecg=df_selection.query('limited_benefit == "ECG"')['limited_benefit'].count()

## style sheet
with open('style.css') as style:
    st.markdown(f'<style>{style.read()}</style>',unsafe_allow_html=True)



#     #col B
# st.markdown ('### Metrics')
# col1,col2,col3=st.columns(3)
# col1.metric('Title','Figure','subtitle
ben_spending=df_selection.groupby('month').sum()['actual_amount']
# month_names = [calendar.month_name[m] for m in ben_spending.index]
month_abbr = [calendar.month_abbr[m] for m in ben_spending.index]

fig_ben_spending=px.bar(
    ben_spending,
    x=month_abbr,
    y=ben_spending.values,
    title="<b>Spending</b>",
    color_discrete_sequence=['#00ACEC']*len(ben_spending),
    template="plotly_white",
    text=(ben_spending.values / 1000).round(2),
  
)

fig_ben_spending.update_layout(
   # plot_bgcolor="rbga(0,0,0,0,)",
    xaxis=(dict(showgrid=False,title='')),
    yaxis=(dict(showgrid=False,title='',tickvals=[])),
    width=520, height=300,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    
    

)
fig_ben_spending.update_traces(textposition='auto',
 texttemplate='%{text:.2s}K',  # Format text labels to display values in thousands with "K"
    textfont_size=12,)  

# Estimated savings

estimated_savings=df_selection.groupby('month').sum()['estimated_savings']
month_abbr = [calendar.month_abbr[m] for m in estimated_savings.index]

fig_est_savings=px.bar(
    estimated_savings,
    x=month_abbr,
    y=estimated_savings.values,
    title="Estimated savings",
    color_discrete_sequence=['#00ACEC']*len(ben_spending),
    template="plotly_white",
    text=(estimated_savings.values / 1000).round(2),
)

fig_est_savings.update_layout(
    xaxis=(dict(showgrid=False,title='')),
    yaxis=(dict(showgrid=False,title='',tickvals=[])),width=500, height=500,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)
fig_est_savings.update_traces(textposition='outside',
 texttemplate='%{text:.2s}K',  # Format text labels to display values in thousands with "K"
    textfont_size=12,)  # Adjust the text position


### Visit trend
visit_rate=df_selection.groupby(['month','primary_holder_no','beneficiary_no']).count()['date']#/df_selection.groupby(['month','primary_holder_no','beneficiary_no'])['date'].nunique()
visit_rate=visit_rate.reset_index(name='visit')
visit_rate=visit_rate.groupby('month').mean()['visit']
# month_names = [calendar.month_name[m] for m in visit_rate.index]
month_abbr = [calendar.month_abbr[m] for m in visit_rate.index]


fig_visit=px.line(
    visit_rate,
    x=month_abbr,
    y=visit_rate.values,
    title="Beneficiary Visits",
    color_discrete_sequence=['#00ACEC']*len(ben_spending,),
    template="plotly_white",
    # text=visit_rate.values  # Add the text parameter

)
fig_visit.update_layout(
    xaxis=(dict(showgrid=False,title='',)),
    yaxis=(dict(showgrid=True,gridcolor='rgba(0, 0, 0, 0.03)',title='')),
    width=500, height=500,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)
# fig_visit.update_traces(textposition='top center')  # Adjust the text position



# Pie chart  calculations
used_health_check=df_selection.query('limited_benefit == "Anual Health Check"')['limited_benefit'].count()
unused_health_check=total_ben-used_health_check

# Calculate the total sum of both categories
total = used_health_check + unused_health_check

# Calculate the percentage of Unused
used_percentage = (used_health_check / total) * 100

# Create a dictionary
dix = {
    "Used": [used_health_check],
    "Unused": [unused_health_check]
}

# Create a donut chart
fig_donut = px.pie(
    names=list(dix.keys()),    # Use dictionary keys as labels
    values=[val[0] for val in dix.values()],  # Use first element of each value list for pie slices
    #title="<b>Donut Chart</b>",
    hole=0.5,  # Adjust the size of the central hole (0.5 creates a standard donut chart)
    template="plotly_white",
    color_discrete_sequence=["#ddd", "#00ACEC"],  # Customize colors for Unused and Used
    
)

# Add annotation for the unused percentage in the center hole
fig_donut.add_annotation(
    text=f"{used_percentage:.1f}%",
    x=0.5, y=0.5,  # Center of the donut chart
    font=dict(size=15),
    showarrow=False
)

fig_donut.update_traces(textinfo='none')
fig_donut.update_layout(showlegend=False,width=250, height=250,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)')






#hide style
hide_st_style= """
<style>
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}
</style>
"""
st.markdown(hide_st_style,unsafe_allow_html=True)


### Layout chart elements
left,right,extra=st.columns([4,4,2])

with left:
    st.plotly_chart(fig_visit)
with right:st.plotly_chart(fig_est_savings)
with extra:
    st.plotly_chart(fig_donut) # donut chart
    st.image("design.png",width=220,)
    st.write(f'<h6 style= margin-top:-55px;color:#fff;padding-left:10px;>{used_health_check}</h6>',unsafe_allow_html=True)
    st.write("<p style=text-align:left;padding:5px;font-size:13px;>This indicates the number of beneficiaries or dependents that have completed their Annual Health Check</p>", unsafe_allow_html=True)
   

left,ecg,dental,vision,ambulance,home=st.columns([7,2,2,2,2,2])
with ecg:
    
    st.markdown("###### ECG")
    st.write(f"Entntitlement: {total_ben}")
    st.write(f"Used: {used_ecg}")
    st.write(f"Left: {total_ben-used_ecg}")
with dental:

    st.markdown("###### Dental Check")
    st.write(f"Entitlement: {total_ben}")
    if list(df_selection.plan.head(1))[0]=='Premium':
        st.write(f"Used: {used_dental}")
        st.write(f"Left: {total_ben-used_dental}")
    else:
        st.button("Upgrade",key='one')
with vision:
    st.write("###### Vision Check")
    st.write(f"Entitlement: {total_ben}")
    if list(df_selection.plan.head(1))[0]=='Premium':
        st.write(f"Used: {used_vision}")
        st.write(f"Left: {total_ben-used_vision}")
    else:
        st.button("Upgrade",key='two')
with ambulance:
    st.write("###### Ambulance")
    st.write(f"Entitlement: {total_ben}")
    if list(df_selection.plan.head(1))[0]=='Premium':
        st.write(f"Used: {used_ambulance}")
        st.write(f"Left: {total_ben-used_ambulance}")
    else:
        st.button("Upgrade",key='three')
with home:
    st.markdown("###### Home Care")
    st.write(f"Entitlement: {total_ben*12}")
    if list(df_selection.plan.head(1))[0]=='Premium':
        st.write(f"Used: {used_home}")
        st.write(f"Left: {(total_ben*12)-used_home}")
    else:
        st.button('Upgrade',key='four')

with left: st.plotly_chart(fig_ben_spending)








    





  







