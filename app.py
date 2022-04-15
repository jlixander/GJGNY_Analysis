#import libraries
import pandas as pd
import numpy as np
from matplotlib.dates import DateFormatter
import matplotlib.dates as mdates
import datetime as dt
from datetime import timedelta
import calendar
import time
from pandas.tseries.offsets import MonthEnd
from dateutil.relativedelta import relativedelta

#dash libraries
import dash
import dash_core_components as dcc
from dash import html, dash_table
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash.dependencies import Input, Output

#Set notebook execution timer
# a = time.time()

#Load GJGNY dataset into a Dataframe (includes successors)
df = pd.read_csv("../Transformed_datasets/GJGNY_Mapping_successors_included.csv",low_memory=False)

#Make sure Setup date column is in datetime format
df['SETUP_MONTH'] = pd.to_datetime(df['SETUP_MONTH'])
df['ACCOUNT_CODE_DATE'] = pd.to_datetime(df['ACCOUNT_CODE_DATE'])
df['LAST_PAYMENT_DATE'] = pd.to_datetime(df['LAST_PAYMENT_DATE'])
#Create function to get year delta (Accounts for leap years)
def subtract_years(dt, years):
    try:
        dt = dt.replace(year=dt.year-years)
    except ValueError:
        dt = dt.replace(year=dt.year-years, day=dt.day-1)
    return dt

#Initialize working dates
least_recent_date = df['SETUP_MONTH'].min() #Get the least recent date on the
most_recent_date = df['SETUP_MONTH'].max() #Get the most recent date on the
three_years_prior_date = subtract_years(most_recent_date, 3) #Get the date of the past 3 years
three_years_prior_date_str= three_years_prior_date.strftime("%Y-%m")
assisted_date = pd.Timestamp('2016-09-30')

# print(most_recent_date," ",
# assisted_date," ",
# three_years_prior_date, " ",
# least_recent_date)


#Create Slider min a max
fico_min= df["CREDIT_SCORE_CURRENT_HIGH"].min()
fico_max= df["CREDIT_SCORE_CURRENT_HIGH"].max()



#Remove Nan values from PLEDGED Column
df.PLEDGED = df.PLEDGED.fillna('Unpledged')


#Remove Nan values from UTILITY Column
df.UTILITY = df.UTILITY.fillna('Non-OBR')

 
 
#Create Table0
#Create average calculations for table
avg_Orig_loan_amount = "$ {:,.2f}".format(df['ORIGINAL_LOAN_AMOUNT'].mean())
avg_int_rate = "{:.2f}%".format(df['INTEREST_RATE'].mean())
avg_FICO_score = "{:.0f}".format(df['CREDIT_SCORE_CURRENT_HIGH'].mean())
avg_DTI = "{:.2f}".format(df['DEBT_TO_INCOME'].mean())
avg_loan_bal = "$ {:,.2f}".format(df['CURRENT_BALANCE'].mean())
perc_loan_delinquent = "{:.2f}%".format(((df['DELINQUENT_AMOUNT']).sum()/df['ORIGINAL_LOAN_AMOUNT'].sum())*1000)
net_co_rate = "{:.2f}%".format(((df['CHARGEOFF_AMOUNT']).sum() / df['ORIGINAL_LOAN_AMOUNT'].sum())*100)


#Plot table0
table0 = go.Figure(data=[go.Table(header=dict(values=['Attributes', 'Value']),
                 cells=dict(values=[['Avg. Original Loan Amount', 'Avg. Interest Rate', 'Avg. FICO Score', 'Avg. DTI', 'Avg. Loan Balance', '% Total Loan Value Delinquent',"Net charge-off rate"], 
                                    [avg_Orig_loan_amount, avg_int_rate, avg_FICO_score, avg_DTI, avg_loan_bal, perc_loan_delinquent, net_co_rate],
                                   ],
                           ))
                     ])
#table0.show()

#Create Table1
#Create OBR summary for table
#Loan counts
National_Grid_cnt = len(df[df["UTILITY"].str.contains('National Grid')])
Rochester_Gas_Electric_cnt = len(df[df["UTILITY"].str.contains('Rochester Gas and Electric')])
NYS_Electric_Gas_cnt = len(df[df["UTILITY"].str.contains('NYS Electric and Gas')])
Consolidated_Edison_cnt = len(df[df["UTILITY"].str.contains('Consolidated Edison')])
Long_Island_Power_Authority_cnt = len(df[df["UTILITY"].str.contains('Long Island Power Authority')])
Central_Hudson_Gas_Electric_cnt = len(df[df["UTILITY"].str.contains('Central Hudson Gas and Electric')])
Municipal_Utilities_cnt = len(df[df["UTILITY"].str.contains('Municipal Utilities')])
Orange_Rockland_Utilities_cnt = len(df[df["UTILITY"].str.contains('Orange and Rockland Utilities')])
Non_OBR_cnt = len(df[df["UTILITY"].str.contains('Non-OBR')])

#Orignal Loan amount sum
National_Grid_orig_sum = "$ {:,.2f}".format(df[df["UTILITY"].str.contains('National Grid')]['ORIGINAL_LOAN_AMOUNT'].sum())
Rochester_Gas_Electric_orig_sum = "$ {:,.2f}".format(df[df["UTILITY"].str.contains('Rochester Gas and Electric')]['ORIGINAL_LOAN_AMOUNT'].sum())
NYS_Electric_Gas_orig_sum = "$ {:,.2f}".format(df[df["UTILITY"].str.contains('NYS Electric and Gas')]['ORIGINAL_LOAN_AMOUNT'].sum())
Consolidated_Edison_orig_sum = "$ {:,.2f}".format(df[df["UTILITY"].str.contains('Consolidated Edison')]['ORIGINAL_LOAN_AMOUNT'].sum())
Long_Island_Power_Authority_orig_sum = "$ {:,.2f}".format(df[df["UTILITY"].str.contains('Long Island Power Authority')]['ORIGINAL_LOAN_AMOUNT'].sum())
Central_Hudson_Gas_Electric_orig_sum = "$ {:,.2f}".format(df[df["UTILITY"].str.contains('Central Hudson Gas and Electric')]['ORIGINAL_LOAN_AMOUNT'].sum())
Municipal_Utilities_orig_sum = "$ {:,.2f}".format(df[df["UTILITY"].str.contains('Municipal Utilities')]['ORIGINAL_LOAN_AMOUNT'].sum())
Orange_Rockland_Utilities_orig_sum = "$ {:,.2f}".format(df[df["UTILITY"].str.contains('Orange and Rockland Utilities')]['ORIGINAL_LOAN_AMOUNT'].sum())
Non_OBR_orig_sum = "$ {:,.2f}".format(df[df["UTILITY"].str.contains('Non-OBR')]['ORIGINAL_LOAN_AMOUNT'].sum())

# #Loan current balance sum
National_Grid_currbal_sum = "$ {:,.2f}".format(df[df["UTILITY"].str.contains('National Grid')]['CURRENT_BALANCE'].sum())
Rochester_Gas_Electric_currbal_sum = "$ {:,.2f}".format(df[df["UTILITY"].str.contains('Rochester Gas and Electric')]['CURRENT_BALANCE'].sum())
NYS_Electric_Gas_currbal_sum = "$ {:,.2f}".format(df[df["UTILITY"].str.contains('NYS Electric and Gas')]['CURRENT_BALANCE'].sum())
Consolidated_Edison_currbal_sum = "$ {:,.2f}".format(df[df["UTILITY"].str.contains('Consolidated Edison')]['CURRENT_BALANCE'].sum())
Long_Island_Power_Authority_currbal_sum = "$ {:,.2f}".format(df[df["UTILITY"].str.contains('Long Island Power Authority')]['CURRENT_BALANCE'].sum())
Central_Hudson_Gas_Electric_currbal_sum = "$ {:,.2f}".format(df[df["UTILITY"].str.contains('Central Hudson Gas and Electric')]['CURRENT_BALANCE'].sum())
Municipal_Utilities_currbal_sum = "$ {:,.2f}".format(df[df["UTILITY"].str.contains('Municipal Utilities')]['CURRENT_BALANCE'].sum())
Orange_Rockland_Utilities_currbal_sum = "$ {:,.2f}".format(df[df["UTILITY"].str.contains('Orange and Rockland Utilities')]['CURRENT_BALANCE'].sum())
Non_OBR_currbal_sum = "$ {:,.2f}".format(df[df["UTILITY"].str.contains('Non-OBR')]['CURRENT_BALANCE'].sum())


#Plot table1
table1 = go.Figure(data=[go.Table(header=dict(values=['Utility', 'Loan Count', 'Loan Amount', 'Remaining Balance']),
                 cells=dict(values=[['National Grid','Rochester Gas and Electric','NYS Electric and Gas',
                                     'Consolidated Edison','Long Island Power Authority','Central Hudson Gas and Electric',
                                     'Municipal Utilities','Orange and Rockland Utilities','Non-OBR'
                                    ], 
                                    [National_Grid_cnt, Rochester_Gas_Electric_cnt, NYS_Electric_Gas_cnt, 
                                     Consolidated_Edison_cnt, Long_Island_Power_Authority_cnt, Central_Hudson_Gas_Electric_cnt,
                                     Municipal_Utilities_cnt,Orange_Rockland_Utilities_cnt,Non_OBR_cnt], 
                                    [National_Grid_orig_sum, Rochester_Gas_Electric_orig_sum, NYS_Electric_Gas_orig_sum, 
                                     Consolidated_Edison_orig_sum, Long_Island_Power_Authority_orig_sum, Central_Hudson_Gas_Electric_orig_sum,
                                     Municipal_Utilities_orig_sum,Orange_Rockland_Utilities_orig_sum,Non_OBR_orig_sum],
                                    [National_Grid_currbal_sum, Rochester_Gas_Electric_currbal_sum, NYS_Electric_Gas_currbal_sum, 
                                     Consolidated_Edison_currbal_sum, Long_Island_Power_Authority_currbal_sum, Central_Hudson_Gas_Electric_currbal_sum,
                                     Municipal_Utilities_currbal_sum,Orange_Rockland_Utilities_currbal_sum,Non_OBR_currbal_sum],
                                    ],       
                           ))
                     ])
#table1.show()


#df.UTILITY.unique().tolist()


#Create Fig1
fig1 = px.line(df, x=df['SETUP_MONTH'].unique(), y=df.groupby('SETUP_MONTH')['ORIGINAL_LOAN_AMOUNT'].agg(sum))
fig1.update_traces(mode="markers+lines", hovertemplate=None)
fig1.update_xaxes(title_text='Year') #set x axis label
fig1.update_yaxes(title_text='Total Loan Amt Originated') #set y axis label
fig1.update_layout(title="GJGNY Total Loan Amount Issued by Year",hovermode="x") #set hover text to y axis

# fig1.show()


#Create Fig2
df_fig2= df.groupby(['SETUP_MONTH','PURPOSE'])['ORIGINAL_LOAN_AMOUNT'].sum().unstack('PURPOSE').reset_index()

#Plot loan purposes
fig2 = px.bar(df_fig2, x='SETUP_MONTH', y=['Energy Efficiency (EE)', 'Solar (PV)', 'Renewable Heat NY (RHNY)',
       'Solar Thermal', 'Ground Source Heat Pump (GSHP)',
       'Air Source Heat Pump (ASHP)'],
)
#Update layout
fig2.update_layout(
    title="Loan Purpose Dollar Amount Originated by Month",
    xaxis_title="Loan Origination Month",
    yaxis_title="Dollar Amount ($)",
    legend_title="Purpose",
    )


#Create Fig3
df_fig3= df.groupby(['SETUP_MONTH','LOAN_TYPE'])['ORIGINAL_LOAN_AMOUNT'].sum().unstack('LOAN_TYPE').reset_index()

#Plot loan purposes
fig3 = px.bar(df_fig3, x='SETUP_MONTH', y=["Smart Energy", "On Bill Recovery",'Bridge', 'Companion'])

#Update layout
fig3.update_layout(
    title="Loan Type Dollar Amount Originated by Month",
    xaxis_title="Loan Origination Month",
    yaxis_title="Dollar Amount ($)",
    legend_title="Loan Type",
#     font=dict(
#         family="Courier New, monospace",
#         size=18,
#         color="RebeccaPurple"
    )


#Create Fig4
df_fig4= df.groupby(['SETUP_MONTH','UNDERWRITING'])['ORIGINAL_LOAN_AMOUNT'].sum().unstack('UNDERWRITING').reset_index()

#Plot loan purposes
fig4 = px.bar(df_fig4, x='SETUP_MONTH', y=['Tier 1', 'Tier 2'],
)
#Update layout
fig4.update_layout(
    title="Loan Purpose Dollar Amount Originated by Tier",
    xaxis_title="Loan Origination Month",
    yaxis_title="Dollar Amount ($)",
    legend_title="Underwriting",
    )

#Create Fig5
#line graph, doullar amount by loan purpose
df_fig5= df.groupby(['SETUP_MONTH','PURPOSE'])['ORIGINAL_LOAN_AMOUNT'].count().unstack('PURPOSE').reset_index()

#Plot loan purposes
fig5 = px.line(df_fig5, x='SETUP_MONTH', y=['Energy Efficiency (EE)', 'Solar (PV)', 'Renewable Heat NY (RHNY)',
       'Solar Thermal', 'Ground Source Heat Pump (GSHP)',
       'Air Source Heat Pump (ASHP)'],
)

#Update layout
fig5.update_layout(
    title="Loan Purpose Count Originated by Month",
    xaxis_title="Loan Origination Month",
    yaxis_title="Loan Count",
    legend_title="Purpose",
    )
fig5.show()
 
 
#Create Fig6
#contractor performance top 15
 

#####Design your app layout
# create app
app = dash.Dash(__name__)

successor_options = {
    'Yes': [np.nan,'S-0','S-1','S-2','S-3','s-0','S-4','S-5','S-6','s-1','s-2','s-3'],
    'No': [np.nan,'S-0','s-0']
}

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.P(children="📈", style={'fontSize': "30px",'textAlign': 'center'}, className="header-emoji"), #emoji
                html.H1(
                    children="GJGNY Residential Loan Portfolio Analytics",style={'textAlign': 'center'}, className="header-title" 
                ), #Header title
                html.H2(
                    children="Loan Performance Analytics - 2010 through present day",
                    className="header-description", style={'textAlign': 'center'},
                ),
            ],
            className="header",style={'backgroundColor':'#F5F5F5'}
        ),
        
        
        #Set dashboard filters here
        html.Div(
            children=[
                #Date range selector
                html.Label(['Choose Loan Origination Dates to visualize:'],
                          style={'font-weight':'bold'}),
                dcc.DatePickerRange(
                    id='my-date-picker-range',
                    min_date_allowed= least_recent_date,
                    max_date_allowed= most_recent_date,
                    initial_visible_month=three_years_prior_date,
                    start_date= least_recent_date,
                    end_date=most_recent_date
                ), html.Div(id='output-container-date-picker-range'),
                
                html.Label(['Filter Loan based on Loan Type:'],
                          style={'font-weight':'bold'}),
                dcc.Checklist(
                    id='loan-type-input',
                    options=['Smart Energy', 'On Bill Recovery', 'Companion', 'Bridge'],
                    value=['Smart Energy', 'On Bill Recovery', 'Companion', 'Bridge'],
                    inline=True,
                    inputStyle={'cursor':'pointer'}, #makes pointer upon hovering checkbox
                    labelStyle={'background':'#A5D6A7', #style of the label that wraps the checkbox
                               'padding':'0.5rem 1rem',
                               'border-radius':'0.5rem'}
                ),
                
                #second filter section
                html.Label(['Filter Loans based on Underwriting:'],
                          style={'font-weight':'bold'}),
                dcc.Checklist(
                    id='tier-type-input',
                    options=['Tier 1', 'Tier 2'],
                    value=['Tier 1', 'Tier 2'],
                    inline=True,
                    inputStyle={'cursor':'pointer'}, #makes pointer upon hovering checkbox
                    labelStyle={'background':'#99e6ff', #style of the label that wraps the checkbox
                               'padding':'0.5rem 1rem',
                               'border-radius':'0.5rem'}
                ),
                
                #Third filter section
                html.Label(['Filter Loans Based on Purpose:'],
                          style={'font-weight':'bold'}),
                dcc.Checklist(
                    id='purpose-type-input',
                    options=['Energy Efficiency (EE)', 'Solar (PV)',
                             'Solar Thermal','Renewable Heat NY (RHNY)',
                             'Ground Source Heat Pump (GSHP)','Air Source Heat Pump (ASHP)'],
                    
                    value=['Energy Efficiency (EE)', 'Solar (PV)',
                             'Solar Thermal','Renewable Heat NY (RHNY)',
                             'Ground Source Heat Pump (GSHP)','Air Source Heat Pump (ASHP)'],
                    inline=True,
                    inputStyle={'cursor':'pointer'}, #makes pointer upon hovering checkbox
                    labelStyle={'background':'#D2B4DE', #style of the label that wraps the checkbox
                               'padding':'0.5rem 1rem',
                               'border-radius':'0.5rem'}
                ),
                
                #Fourth filter section
                html.Label(['Filter Loans Based on Pledge Status:'],
                          style={'font-weight':'bold'}),
                dcc.Dropdown(
                    id='pledge-status-type-input',
                    options=['Unpledged','Series 2013A EE Bonds', 'Series 2019A EE & PV Bonds', 'Series 2015A EE Bonds', 
                             'Series 2016A EE Bonds','Series 2015A PV Bonds', 'Series 2018A PV Bonds'],
                    value=['Unpledged','Series 2013A EE Bonds', 'Series 2019A EE & PV Bonds', 'Series 2015A EE Bonds', 
                             'Series 2016A EE Bonds','Series 2015A PV Bonds', 'Series 2018A PV Bonds'],
                    multi=True
                ),
                
                #Fifth filter section
                html.Label(['Select FICO Score range to visualize:'],
                          style={'font-weight':'bold'}),
                html.P(),
                dcc.RangeSlider(
                    id='fico-range-slider',
                    step=10,
                    min=300,
                    max=850,
                    dots=True,
                    value=[300,850]
                ),
                
                #Sixth filter section
                html.Label(['Filter Utilities (On Bill Loans):'],
                          style={'font-weight':'bold'}),
                html.P(),
                dcc.Dropdown(
                    id='utility-type-input',
                    options=['National Grid', 'Rochester Gas and Electric','NYS Electric and Gas', 'Consolidated Edison',
                             'Long Island Power Authority', 'Central Hudson Gas and Electric','Municipal Utilities', 
                             'Orange and Rockland Utilities','Non-OBR'],
                    value=['National Grid', 'Rochester Gas and Electric','NYS Electric and Gas', 'Consolidated Edison',
                             'Long Island Power Authority', 'Central Hudson Gas and Electric','Municipal Utilities', 
                             'Orange and Rockland Utilities','Non-OBR'],
                    multi=True
                ),
                
                #Seventh filter section
                html.Label(['Select DTI range to visualize:'],
                          style={'font-weight':'bold'}),
                dcc.RangeSlider(
                    id='dti-range-slider',
                    step=0.05,
                    min=0,
                    max=1,
                    dots=True,
                    value=[0,1]
                ),
                
                #Eighth Filter section
                html.Label(['Include OBR Successors in visuals?'],
                           style={'font-weight':'bold'}),
                html.P(),
                dcc.RadioItems(
                    ['Yes','No'],
                    'Yes',
                    id='obr-successor-radio'
                ),
            
                
                
            ]
        ), #end of filters section
        
        #Table0
        html.H2("Loan Selection Summary"),
        html.Div([
            #dash_table.DataTable(
            dcc.Graph(
                id='table0'),
        ]),
            
        #Table1
        html.H2("OBR Loan Utility Summary"),
        html.Div([
            #dash_table.DataTable(
            dcc.Graph(
                id='table1'),
        ]),
        html.H3("Loan Selection Graphs"),        
        #Fig1
        html.Div([
            dcc.Graph(
                id='graph1'),
        ]),
        
        #Fig2
        html.Div([
            dcc.Graph(
                id='graph2'),
        ]),
        
        #Fig3
        html.Div([
            dcc.Graph(
                id='graph3'),
        ]),
        
        #Fig4
        html.Div([
            dcc.Graph(
                id='graph4'),
        ]),
        
        #Fig5
        html.Div([
            dcc.Graph(
                id='graph5'),
        ]),
        
    ] #main children
) #main html.Div

# -------------------------------------------------------------------------------------------------
#table0 callback
@app.callback(Output('table0', 'figure'),
              Input('my-date-picker-range', 'start_date'),
              Input('my-date-picker-range', 'end_date'),
              Input(component_id='loan-type-input', component_property='value'),
              Input(component_id='tier-type-input', component_property='value'),
              Input(component_id='purpose-type-input', component_property='value'),
              Input(component_id='pledge-status-type-input', component_property='value'),
              Input(component_id='fico-range-slider', component_property='value'),
              Input(component_id='utility-type-input', component_property='value'),
              Input(component_id='dti-range-slider', component_property='value'),
              Input(component_id='obr-successor-radio', component_property='value')
              )

def update_table0(start_date, end_date,
                  loan_types_chosen, tier_type_chosen,
                  purpose_type_chosen, pledged_status_chosen,
                  fico_score_chosen, utilities_chosen,
                  dti_range_chosen, successors_chosen):
    
    #successor filter
    successors_chosen = [i for i in successor_options[successors_chosen]]

    
    dff = df[((df["SETUP_MONTH"] >= start_date) & (df['SETUP_MONTH'] <= end_date)) &
             (df['LOAN_TYPE'].isin(loan_types_chosen)) &
             (df['UNDERWRITING'].isin(tier_type_chosen)) &
             (df['PURPOSE'].isin(purpose_type_chosen)) &
             (df['PLEDGED'].isin(pledged_status_chosen)) &
             ((df["CREDIT_SCORE_CURRENT_HIGH"] >= fico_score_chosen[0]) & (df['CREDIT_SCORE_CURRENT_HIGH'] <= fico_score_chosen[1])) & 
             (df['UTILITY'].isin(utilities_chosen)) &
             ((df["DEBT_TO_INCOME"] >= dti_range_chosen[0]) & (df['DEBT_TO_INCOME'] <= dti_range_chosen[1])) &
             (df['SUCCESSOR_NUMBER'].isin(successors_chosen))
            ] #the graph/dataframe will be filterd by chosen values
    

    #Create average calculations for table0
    avg_Orig_loan_amount = "$ {:,.2f}".format(dff['ORIGINAL_LOAN_AMOUNT'].mean())
    avg_int_rate = "{:.2f}%".format(dff['INTEREST_RATE'].mean())
    avg_FICO_score = "{:.0f}".format(dff['CREDIT_SCORE_CURRENT_HIGH'].mean())
    avg_DTI = "{:.2f}".format(dff['DEBT_TO_INCOME'].mean())
    avg_loan_bal = "$ {:,.2f}".format(dff['CURRENT_BALANCE'].mean())
    perc_loan_delinquent = "{:.2f}%".format(((dff['DELINQUENT_AMOUNT']).sum()/dff['ORIGINAL_LOAN_AMOUNT'].sum())*1000)
    net_co_rate = "{:.2f}%".format(((dff['CHARGEOFF_AMOUNT']).sum() / dff['ORIGINAL_LOAN_AMOUNT'].sum())*100)
    
    #plot table0
    table0 = go.Figure(data=[go.Table(header=dict(values=['Attributes', 'Value']),
                 cells=dict(values=[['Avg Original Loan Amount', 'Avg. Interest Rate', 'Avg. FICO Score', 'Avg. DTI', 'Avg. Loan Balance', '% Total Loan Value Delinquent',"Net charge-off rate"], 
                                    [avg_Orig_loan_amount, 
                                     avg_int_rate, 
                                     avg_FICO_score, 
                                     avg_DTI,
                                     avg_loan_bal,
                                     perc_loan_delinquent, 
                                     net_co_rate]]))
                     ])

    return (table0)

# -------------------------------------------------------------------------------------------------
#table0 callback
@app.callback(Output('table1', 'figure'),
              Input('my-date-picker-range', 'start_date'),
              Input('my-date-picker-range', 'end_date'),
              Input(component_id='loan-type-input', component_property='value'),
              Input(component_id='tier-type-input', component_property='value'),
              Input(component_id='purpose-type-input', component_property='value'),
              Input(component_id='pledge-status-type-input', component_property='value'),
              Input(component_id='fico-range-slider', component_property='value'),
              Input(component_id='utility-type-input', component_property='value'),
              Input(component_id='dti-range-slider', component_property='value'),
              Input(component_id='obr-successor-radio', component_property='value')
              )

def update_table1(start_date, end_date,
                  loan_types_chosen, tier_type_chosen,
                  purpose_type_chosen, pledged_status_chosen,
                  fico_score_chosen, utilities_chosen,
                  dti_range_chosen, successors_chosen):
    
    #successor filter
    successors_chosen = [i for i in successor_options[successors_chosen]]

    
    dff = df[((df["SETUP_MONTH"] >= start_date) & (df['SETUP_MONTH'] <= end_date)) &
             (df['LOAN_TYPE'].isin(loan_types_chosen)) &
             (df['UNDERWRITING'].isin(tier_type_chosen)) &
             (df['PURPOSE'].isin(purpose_type_chosen)) &
             (df['PLEDGED'].isin(pledged_status_chosen)) &
             ((df["CREDIT_SCORE_CURRENT_HIGH"] >= fico_score_chosen[0]) & (df['CREDIT_SCORE_CURRENT_HIGH'] <= fico_score_chosen[1])) & 
             (df['UTILITY'].isin(utilities_chosen)) &
             ((df["DEBT_TO_INCOME"] >= dti_range_chosen[0]) & (df['DEBT_TO_INCOME'] <= dti_range_chosen[1])) &
             (df['SUCCESSOR_NUMBER'].isin(successors_chosen))
            ] #the graph/dataframe will be filterd by chosen values
    

    #Create calculations for table1
    #Loan counts
    National_Grid_cnt = len(df[df["UTILITY"].str.contains('National Grid')])
    Rochester_Gas_Electric_cnt = len(df[df["UTILITY"].str.contains('Rochester Gas and Electric')])
    NYS_Electric_Gas_cnt = len(df[df["UTILITY"].str.contains('NYS Electric and Gas')])
    Consolidated_Edison_cnt = len(df[df["UTILITY"].str.contains('Consolidated Edison')])
    Long_Island_Power_Authority_cnt = len(df[df["UTILITY"].str.contains('Long Island Power Authority')])
    Central_Hudson_Gas_Electric_cnt = len(df[df["UTILITY"].str.contains('Central Hudson Gas and Electric')])
    Municipal_Utilities_cnt = len(df[df["UTILITY"].str.contains('Municipal Utilities')])
    Orange_Rockland_Utilities_cnt = len(df[df["UTILITY"].str.contains('Orange and Rockland Utilities')])
    Non_OBR_cnt = len(df[df["UTILITY"].str.contains('Non-OBR')])

    #Orignal Loan amount sum
    National_Grid_orig_sum = "$ {:,.2f}".format(df[df["UTILITY"].str.contains('National Grid')]['ORIGINAL_LOAN_AMOUNT'].sum())
    Rochester_Gas_Electric_orig_sum = "$ {:,.2f}".format(df[df["UTILITY"].str.contains('Rochester Gas and Electric')]['ORIGINAL_LOAN_AMOUNT'].sum())
    NYS_Electric_Gas_orig_sum = "$ {:,.2f}".format(df[df["UTILITY"].str.contains('NYS Electric and Gas')]['ORIGINAL_LOAN_AMOUNT'].sum())
    Consolidated_Edison_orig_sum = "$ {:,.2f}".format(df[df["UTILITY"].str.contains('Consolidated Edison')]['ORIGINAL_LOAN_AMOUNT'].sum())
    Long_Island_Power_Authority_orig_sum = "$ {:,.2f}".format(df[df["UTILITY"].str.contains('Long Island Power Authority')]['ORIGINAL_LOAN_AMOUNT'].sum())
    Central_Hudson_Gas_Electric_orig_sum = "$ {:,.2f}".format(df[df["UTILITY"].str.contains('Central Hudson Gas and Electric')]['ORIGINAL_LOAN_AMOUNT'].sum())
    Municipal_Utilities_orig_sum = "$ {:,.2f}".format(df[df["UTILITY"].str.contains('Municipal Utilities')]['ORIGINAL_LOAN_AMOUNT'].sum())
    Orange_Rockland_Utilities_orig_sum = "$ {:,.2f}".format(df[df["UTILITY"].str.contains('Orange and Rockland Utilities')]['ORIGINAL_LOAN_AMOUNT'].sum())
    Non_OBR_orig_sum = "$ {:,.2f}".format(df[df["UTILITY"].str.contains('Non-OBR')]['ORIGINAL_LOAN_AMOUNT'].sum())

    #Loan current balance sum
    National_Grid_currbal_sum = "$ {:,.2f}".format(df[df["UTILITY"].str.contains('National Grid')]['CURRENT_BALANCE'].sum())
    Rochester_Gas_Electric_currbal_sum = "$ {:,.2f}".format(df[df["UTILITY"].str.contains('Rochester Gas and Electric')]['CURRENT_BALANCE'].sum())
    NYS_Electric_Gas_currbal_sum = "$ {:,.2f}".format(df[df["UTILITY"].str.contains('NYS Electric and Gas')]['CURRENT_BALANCE'].sum())
    Consolidated_Edison_currbal_sum = "$ {:,.2f}".format(df[df["UTILITY"].str.contains('Consolidated Edison')]['CURRENT_BALANCE'].sum())
    Long_Island_Power_Authority_currbal_sum = "$ {:,.2f}".format(df[df["UTILITY"].str.contains('Long Island Power Authority')]['CURRENT_BALANCE'].sum())
    Central_Hudson_Gas_Electric_currbal_sum = "$ {:,.2f}".format(df[df["UTILITY"].str.contains('Central Hudson Gas and Electric')]['CURRENT_BALANCE'].sum())
    Municipal_Utilities_currbal_sum = "$ {:,.2f}".format(df[df["UTILITY"].str.contains('Municipal Utilities')]['CURRENT_BALANCE'].sum())
    Orange_Rockland_Utilities_currbal_sum = "$ {:,.2f}".format(df[df["UTILITY"].str.contains('Orange and Rockland Utilities')]['CURRENT_BALANCE'].sum())
    Non_OBR_currbal_sum = "$ {:,.2f}".format(df[df["UTILITY"].str.contains('Non-OBR')]['CURRENT_BALANCE'].sum())

    
    #plot table1
    table1 = go.Figure(data=[go.Table(header=dict(values=['Utility', 'Loan Count', 'Loan Amount', 'Remaining Balance']),
                 cells=dict(values=[['National Grid','Rochester Gas and Electric','NYS Electric and Gas',
                                     'Consolidated Edison','Long Island Power Authority','Central Hudson Gas and Electric',
                                     'Municipal Utilities','Orange and Rockland Utilities','Non-OBR'
                                    ], 
                                    [National_Grid_cnt, Rochester_Gas_Electric_cnt, NYS_Electric_Gas_cnt, 
                                     Consolidated_Edison_cnt, Long_Island_Power_Authority_cnt, Central_Hudson_Gas_Electric_cnt,
                                     Municipal_Utilities_cnt,Orange_Rockland_Utilities_cnt,Non_OBR_cnt], 
                                    [National_Grid_orig_sum, Rochester_Gas_Electric_orig_sum, NYS_Electric_Gas_orig_sum, 
                                     Consolidated_Edison_orig_sum, Long_Island_Power_Authority_orig_sum, Central_Hudson_Gas_Electric_orig_sum,
                                     Municipal_Utilities_orig_sum,Orange_Rockland_Utilities_orig_sum,Non_OBR_orig_sum],
                                    [National_Grid_currbal_sum, Rochester_Gas_Electric_currbal_sum, NYS_Electric_Gas_currbal_sum, 
                                     Consolidated_Edison_currbal_sum, Long_Island_Power_Authority_currbal_sum, Central_Hudson_Gas_Electric_currbal_sum,
                                     Municipal_Utilities_currbal_sum,Orange_Rockland_Utilities_currbal_sum,Non_OBR_currbal_sum],
                                    ],       
                           ))
                     ])

    return (table1)



# -------------------------------------------------------------------------------------------------
#fig1 callback
@app.callback(Output('graph1', 'figure'),
              Input('my-date-picker-range', 'start_date'),
              Input('my-date-picker-range', 'end_date'),
              Input(component_id='loan-type-input', component_property='value'),
              Input(component_id='tier-type-input', component_property='value'),
              Input(component_id='purpose-type-input', component_property='value'),
              Input(component_id='pledge-status-type-input', component_property='value'),
              Input(component_id='fico-range-slider', component_property='value'),
              Input(component_id='utility-type-input', component_property='value'),
              Input(component_id='dti-range-slider', component_property='value'),
              Input(component_id='obr-successor-radio', component_property='value')
             )

def update_graph1(start_date, end_date, 
                  loan_types_chosen, tier_type_chosen,
                  purpose_type_chosen, pledged_status_chosen,
                  fico_score_chosen, utilities_chosen,
                  dti_range_chosen, successors_chosen):
    
    #successor filter
    successors_chosen = [i for i in successor_options[successors_chosen]]
    
    dff = df[((df["SETUP_MONTH"] >= start_date) & (df['SETUP_MONTH'] <= end_date)) &
             (df['LOAN_TYPE'].isin(loan_types_chosen)) & 
             (df['UNDERWRITING'].isin(tier_type_chosen)) &
             (df['PURPOSE'].isin(purpose_type_chosen)) & 
             (df['PLEDGED'].isin(pledged_status_chosen)) &
             ((df["CREDIT_SCORE_CURRENT_HIGH"] >= fico_score_chosen[0]) & (df['CREDIT_SCORE_CURRENT_HIGH'] <= fico_score_chosen[1])) & 
             (df['UTILITY'].isin(utilities_chosen)) &
             ((df["DEBT_TO_INCOME"] >= dti_range_chosen[0]) & (df['DEBT_TO_INCOME'] <= dti_range_chosen[1])) &
             (df['SUCCESSOR_NUMBER'].isin(successors_chosen))
            ] #the graph/dataframe will be filterd by chosen values
    
    #print(dff['LOAN_TYPE'].unique())
    #print(dff['UNDERWRITING'].unique())
    
    #fig1 update
    fig1 = px.line(
        data_frame=dff,
        x=dff['SETUP_MONTH'].unique(), 
        y=dff.groupby(['SETUP_MONTH'])['ORIGINAL_LOAN_AMOUNT'].agg('sum'),
        labels=dict(x="Loan Origination Month", y="Cumulative Dollar Amount ($)")
             )
    fig1.update_traces(mode="markers+lines", hovertemplate=None)
    fig1.update_layout(title_text="Total Loan Dollar Amount Originated"
                      )
    return (fig1)

#---------------------------------------------------------------------------------------------------------------
#fig2 callback
@app.callback(Output('graph2', 'figure'),
              Input('my-date-picker-range', 'start_date'),
              Input('my-date-picker-range', 'end_date'),
              Input(component_id='loan-type-input', component_property='value'),
              Input(component_id='tier-type-input', component_property='value'),
              Input(component_id='purpose-type-input', component_property='value'),
              Input(component_id='pledge-status-type-input', component_property='value'),
              Input(component_id='fico-range-slider', component_property='value'),
              Input(component_id='utility-type-input', component_property='value'),
              Input(component_id='dti-range-slider', component_property='value'),
              Input(component_id='obr-successor-radio', component_property='value')
             )

def update_graph2(start_date, end_date, 
                  loan_types_chosen, tier_type_chosen, 
                  purpose_type_chosen, pledged_status_chosen,
                  fico_score_chosen, utilities_chosen,
                  dti_range_chosen, successors_chosen):
    
    #successor filter
    successors_chosen = [i for i in successor_options[successors_chosen]]
    
    #dataframe filters
    dff = df[((df["SETUP_MONTH"] >= start_date) & (df['SETUP_MONTH'] <= end_date)) &
             (df['LOAN_TYPE'].isin(loan_types_chosen)) & 
            (df['UNDERWRITING'].isin(tier_type_chosen)) &
            (df['PURPOSE'].isin(purpose_type_chosen)) & 
            (df['PLEDGED'].isin(pledged_status_chosen)) &
            ((df["CREDIT_SCORE_CURRENT_HIGH"] >= fico_score_chosen[0]) & (df['CREDIT_SCORE_CURRENT_HIGH'] <= fico_score_chosen[1])) & 
            (df['UTILITY'].isin(utilities_chosen)) &
            ((df["DEBT_TO_INCOME"] >= dti_range_chosen[0]) & (df['DEBT_TO_INCOME'] <= dti_range_chosen[1])) &
             (df['SUCCESSOR_NUMBER'].isin(successors_chosen))
            ] #the graph/dataframe will be filterd by chosen values
    
    #fig2 update
    ##fig2 df update
    dff_fig2 = dff.groupby(['SETUP_MONTH','PURPOSE'])['ORIGINAL_LOAN_AMOUNT'].sum().unstack('PURPOSE').reset_index()
    purpose_list = dff_fig2.columns.tolist()
    
    ##fig2 plot
    fig2 = px.bar(dff_fig2, x='SETUP_MONTH', y=purpose_list)
                 
    
    fig2.update_layout(
        title="Loan Purpose Dollar Amount Originated by Month",
        xaxis_title="Loan Origination Month",
        yaxis_title="Cumulative Dollar Amount ($)",
        legend_title="Purpose"
    )
    
    return (fig2)

#----------------------------------------------------------------------------------------------------------------
# #fig3 callback
@app.callback(Output('graph3', 'figure'),
              Input('my-date-picker-range', 'start_date'),
              Input('my-date-picker-range', 'end_date'),
              Input(component_id='loan-type-input', component_property='value'),
              Input(component_id='tier-type-input', component_property='value'),
              Input(component_id='purpose-type-input', component_property='value'),
              Input(component_id='pledge-status-type-input', component_property='value'),
              Input(component_id='fico-range-slider', component_property='value'),
              Input(component_id='utility-type-input', component_property='value'),
              Input(component_id='dti-range-slider', component_property='value'),
              Input(component_id='obr-successor-radio', component_property='value')
             )

def update_graph3(start_date, end_date, 
                  loan_types_chosen, tier_type_chosen, 
                  purpose_type_chosen, pledged_status_chosen,
                  fico_score_chosen, utilities_chosen,
                  dti_range_chosen, successors_chosen):
    
    #successor filter
    successors_chosen = [i for i in successor_options[successors_chosen]]
    
    #dataframe filters
    dff = df[((df["SETUP_MONTH"] >= start_date) & (df['SETUP_MONTH'] <= end_date)) &
             (df['LOAN_TYPE'].isin(loan_types_chosen)) & 
             (df['UNDERWRITING'].isin(tier_type_chosen)) &
             (df['PURPOSE'].isin(purpose_type_chosen)) & 
             (df['PLEDGED'].isin(pledged_status_chosen)) &
             ((df["CREDIT_SCORE_CURRENT_HIGH"] >= fico_score_chosen[0]) & (df['CREDIT_SCORE_CURRENT_HIGH'] <= fico_score_chosen[1])) & 
             (df['UTILITY'].isin(utilities_chosen)) &
            ((df["DEBT_TO_INCOME"] >= dti_range_chosen[0]) & (df['DEBT_TO_INCOME'] <= dti_range_chosen[1])) &
             (df['SUCCESSOR_NUMBER'].isin(successors_chosen))
            ] #the graph/dataframe will be filterd by chosen values
    
    #fig3 update
    ##fig3 df update
    dff_fig3 = dff.groupby(['SETUP_MONTH','LOAN_TYPE'])['ORIGINAL_LOAN_AMOUNT'].sum().unstack('LOAN_TYPE').reset_index()
    loan_type_list = dff_fig3.columns.tolist()
    
    ##fig2 plot
    fig3 = px.bar(dff_fig3, x='SETUP_MONTH', y=loan_type_list)
                 
    
    fig3.update_layout(
        title="Loan Type Dollar Amount Originated by Month",
        xaxis_title="Loan Origination Month",
        yaxis_title="Cumulative Dollar Amount ($)",
        legend_title="Loan Type"
    )
    
    return (fig3)

#----------------------------------------------------------------------------------------------------------------
# #fig4 callback
@app.callback(Output('graph4', 'figure'),
              Input('my-date-picker-range', 'start_date'),
              Input('my-date-picker-range', 'end_date'),
              Input(component_id='loan-type-input', component_property='value'),
              Input(component_id='tier-type-input', component_property='value'),
              Input(component_id='purpose-type-input', component_property='value'),
              Input(component_id='pledge-status-type-input', component_property='value'),
              Input(component_id='fico-range-slider', component_property='value'),
              Input(component_id='utility-type-input', component_property='value'),
              Input(component_id='dti-range-slider', component_property='value'),
              Input(component_id='obr-successor-radio', component_property='value')
             )

def update_graph4(start_date, end_date, 
                  loan_types_chosen, tier_type_chosen, 
                  purpose_type_chosen, pledged_status_chosen,
                  fico_score_chosen, utilities_chosen,
                  dti_range_chosen, successors_chosen):
    
    #successor filter
    successors_chosen = [i for i in successor_options[successors_chosen]]
    
    #dataframe filters
    dff = df[((df["SETUP_MONTH"] >= start_date) & (df['SETUP_MONTH'] <= end_date)) &
             (df['LOAN_TYPE'].isin(loan_types_chosen)) & 
             (df['UNDERWRITING'].isin(tier_type_chosen)) &
             (df['PURPOSE'].isin(purpose_type_chosen)) & 
             (df['PLEDGED'].isin(pledged_status_chosen)) &
             ((df["CREDIT_SCORE_CURRENT_HIGH"] >= fico_score_chosen[0]) & (df['CREDIT_SCORE_CURRENT_HIGH'] <= fico_score_chosen[1])) & 
             (df['UTILITY'].isin(utilities_chosen)) &
            ((df["DEBT_TO_INCOME"] >= dti_range_chosen[0]) & (df['DEBT_TO_INCOME'] <= dti_range_chosen[1])) &
             (df['SUCCESSOR_NUMBER'].isin(successors_chosen))
            ] #the graph/dataframe will be filterd by chosen values
    
    #fig4 update
    ##fig4 df update
    df_fig4= dff.groupby(['SETUP_MONTH','UNDERWRITING'])['ORIGINAL_LOAN_AMOUNT'].sum().unstack('UNDERWRITING').reset_index()
    #Plot loan purposes
    fig4 = px.bar(df_fig4, x='SETUP_MONTH', y=['Tier 1', 'Tier 2'],
                 )
    #Update layout
    fig4.update_layout(
        title="Loan Purpose Dollar Amount Originated by Tier",
        xaxis_title="Loan Origination Month",
        yaxis_title="Dollar Amount ($)",
        legend_title="Underwriting",
    )

    return (fig4)

#----------------------------------------------------------------------------------------------------------------
# #fig5 callback
@app.callback(Output('graph5', 'figure'),
              Input('my-date-picker-range', 'start_date'),
              Input('my-date-picker-range', 'end_date'),
              Input(component_id='loan-type-input', component_property='value'),
              Input(component_id='tier-type-input', component_property='value'),
              Input(component_id='purpose-type-input', component_property='value'),
              Input(component_id='pledge-status-type-input', component_property='value'),
              Input(component_id='fico-range-slider', component_property='value'),
              Input(component_id='utility-type-input', component_property='value'),
              Input(component_id='dti-range-slider', component_property='value'),
              Input(component_id='obr-successor-radio', component_property='value')
             )

def update_graph5(start_date, end_date, 
                  loan_types_chosen, tier_type_chosen, 
                  purpose_type_chosen, pledged_status_chosen,
                  fico_score_chosen, utilities_chosen,
                  dti_range_chosen, successors_chosen):
    
    #successor filter
    successors_chosen = [i for i in successor_options[successors_chosen]]
    
    #dataframe filters
    dff = df[((df["SETUP_MONTH"] >= start_date) & (df['SETUP_MONTH'] <= end_date)) &
             (df['LOAN_TYPE'].isin(loan_types_chosen)) & 
             (df['UNDERWRITING'].isin(tier_type_chosen)) &
             (df['PURPOSE'].isin(purpose_type_chosen)) & 
             (df['PLEDGED'].isin(pledged_status_chosen)) &
             ((df["CREDIT_SCORE_CURRENT_HIGH"] >= fico_score_chosen[0]) & (df['CREDIT_SCORE_CURRENT_HIGH'] <= fico_score_chosen[1])) & 
             (df['UTILITY'].isin(utilities_chosen)) &
            ((df["DEBT_TO_INCOME"] >= dti_range_chosen[0]) & (df['DEBT_TO_INCOME'] <= dti_range_chosen[1])) &
             (df['SUCCESSOR_NUMBER'].isin(successors_chosen))
            ] #the graph/dataframe will be filterd by chosen values
    
    #fig5 update
    ##fig5 df update
    fig5 = px.line(df_fig5, x='SETUP_MONTH', y=['Energy Efficiency (EE)', 'Solar (PV)', 'Renewable Heat NY (RHNY)',
       'Solar Thermal', 'Ground Source Heat Pump (GSHP)',
       'Air Source Heat Pump (ASHP)'],
                  )
    #Update layout
    fig5.update_layout(
        title="Loan Purpose Count Originated by Month",
        xaxis_title="Loan Origination Month",
        yaxis_title="Loan Count",
        legend_title="Purpose",
    )

    return (fig5)

# run app
if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False) # Turn off reloader if inside Jupyter