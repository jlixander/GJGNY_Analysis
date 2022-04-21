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
from dash import dcc
import dash_bootstrap_components as dbc
from dash import html, dash_table
import plotly.express as px
import plotly.graph_objects as go
import plotly
from plotly.subplots import make_subplots
from dash.dependencies import Input, Output

#Mapping libraries
from urllib.request import urlopen
import json

#Load GJGNY dataset into a Dataframe (includes successors)
df = pd.read_csv("GJGNY_Mapping_successors_included.csv",low_memory=False)

#Load map counties
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

#load county fips table and transform as needed to combine with loan data
df_fips = pd.read_csv("fips2county.tsv", sep='\t', header='infer', dtype=str, encoding='latin-1')
df_fips.drop(columns=['StateFIPS','CountyFIPS_3', 'StateAbbr', 'STATE_COUNTY'], inplace=True)
df_fips = df_fips.rename(columns={"CountyName": "PROPERTY_COUNTY", "StateName": "PROPERTY_STATE"})
df_fips = df_fips.loc[df_fips.PROPERTY_STATE == 'New York']
df_fips['PROPERTY_COUNTY'] = df_fips['PROPERTY_COUNTY'].replace('St. Lawrence', 'St Lawrence')

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

#Create Slider min a max
fico_min= df["CREDIT_SCORE_CURRENT_HIGH"].min()
fico_max= df["CREDIT_SCORE_CURRENT_HIGH"].max()

#Remove Nan values from PLEDGED Column
df.PLEDGED = df.PLEDGED.fillna('Unpledged')

#Remove Nan values from UTILITY Column
df.UTILITY = df.UTILITY.fillna('Non-OBR')

##Mapping Data Wrangling
df['PROPERTY_STATE']='New York' #Add state column to dataset


#load county fips table
df_fips = pd.read_csv("fips2county.tsv", sep='\t', header='infer', dtype=str, encoding='latin-1')
df_fips.drop(columns=['StateFIPS','CountyFIPS_3', 'StateAbbr', 'STATE_COUNTY'], inplace=True)
df_fips = df_fips.rename(columns={"CountyName": "PROPERTY_COUNTY", "StateName": "PROPERTY_STATE"})
df_fips = df_fips.loc[df_fips.PROPERTY_STATE == 'New York']
df_fips['PROPERTY_COUNTY'] = df_fips['PROPERTY_COUNTY'].replace('St. Lawrence', 'St Lawrence')

# create app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

successor_options = {
    'Yes': [np.nan, 'S-0', 'S-1', 'S-2', 'S-3', 's-0', 'S-4', 'S-5', 'S-6', 's-1', 's-2', 's-3'],
    'No': [np.nan, 'S-0', 's-0']
}

app.layout = html.Div([
    # Header
    dbc.Row(dbc.Col(html.H1("GJGNY Residential Loan Portfolio Analytics"),
                    width={'size': 6, 'offset': 3},
                    ),
            ),
    dbc.Row(dbc.Col(html.H2("Loan Performance Analytics - 2010 Through Present Day"),
                    width={'size': 6, 'offset': 3},
                    ),
            ),

    # filter rows
    # Date range selector
    dbc.Row(dbc.Col(html.H6('Choose Loan Origination Dates to visualize:'),
                    ),
            ),
    dcc.DatePickerRange(
        id='my-date-picker-range',
        min_date_allowed=least_recent_date,
        max_date_allowed=most_recent_date,
        initial_visible_month=three_years_prior_date,
        start_date=least_recent_date,
        end_date=most_recent_date
    ), html.Div(id='output-container-date-picker-range'),

    # Loan type filter
    dbc.Row(dbc.Col(html.H6('Filter Loans based on Loan Type:'),
                    ),
            ),
    dcc.Checklist(
        id='loan-type-input',
        options=['Smart Energy', 'On Bill Recovery', 'Companion', 'Bridge'],
        value=['Smart Energy', 'On Bill Recovery', 'Companion', 'Bridge'],
        inline=True,
        # inputStyle={'cursor':'pointer'}, #makes pointer upon hovering checkbox
        labelStyle={'background': '#1B76FF',  # style of the label that wraps the checkbox
                    'padding': '0.5rem 1rem',
                    'border-radius': '0.5rem'}
    ),

    # second filter section (Tier filter)
    dbc.Row(dbc.Col(html.H6('Filter Loans based on Underwriting:'),
                    ),
            ),
    dcc.Checklist(
        id='tier-type-input',
        options=['Tier 1', 'Tier 2'],
        value=['Tier 1', 'Tier 2'],
        inline=True,
        # inputStyle={'cursor':'pointer'}, #makes pointer upon hovering checkbox
        labelStyle={'background': '#3498DB',  # style of the label that wraps the checkbox
                    'padding': '0.5rem 1rem',
                    'border-radius': '0.5rem'}
    ),

    # Third filter section (Filter Purpose)
    dbc.Row(dbc.Col(html.H6('Filter Loans Based on Purpose:'),
                    ),
            ),
    dcc.Checklist(
        id='purpose-type-input',
        options=['Energy Efficiency (EE)', 'Solar (PV)',
                 'Solar Thermal', 'Renewable Heat NY (RHNY)',
                 'Ground Source Heat Pump (GSHP)', 'Air Source Heat Pump (ASHP)'],
        value=['Energy Efficiency (EE)', 'Solar (PV)',
               'Solar Thermal', 'Renewable Heat NY (RHNY)',
               'Ground Source Heat Pump (GSHP)', 'Air Source Heat Pump (ASHP)'],
        inline=True,
        # inputStyle={'cursor':'pointer'}, #makes pointer upon hovering checkbox
        labelStyle={'background': '#0EEAFF',  # style of the label that wraps the checkbox
                    'padding': '0.5rem 1rem',
                    'border-radius': '0.5rem'}
    ),

    # Fourth filter section (Pledge Status)
    dbc.Row(dbc.Col(html.H6('Filter Loans Based on Pledge Status:'),
                    ),
            ),
    dcc.Dropdown(
        id='pledge-status-type-input',
        options=['Unpledged', 'Series 2013A EE Bonds', 'Series 2019A EE & PV Bonds', 'Series 2015A EE Bonds',
                 'Series 2016A EE Bonds', 'Series 2015A PV Bonds', 'Series 2018A PV Bonds'],
        value=['Unpledged', 'Series 2013A EE Bonds', 'Series 2019A EE & PV Bonds', 'Series 2015A EE Bonds',
               'Series 2016A EE Bonds', 'Series 2015A PV Bonds', 'Series 2018A PV Bonds'],
        multi=True
    ),

    # Fifth filter section (FICO)
    dbc.Row(dbc.Col(html.H6('Select FICO Score range to visualize:'),
                    ),
            ),
    dcc.RangeSlider(
        id='fico-range-slider',
        step=25,
        min=300,
        max=850,
        dots=True,
        value=[300, 850]
    ),

    # Sixth filter section (Utility)
    dbc.Row(dbc.Col(html.H6('Filter Utilities (On Bill Loans):'),
                    ),
            ),
    dcc.Dropdown(
        id='utility-type-input',
        options=['National Grid', 'Rochester Gas and Electric', 'NYS Electric and Gas', 'Consolidated Edison',
                 'Long Island Power Authority', 'Central Hudson Gas and Electric', 'Municipal Utilities',
                 'Orange and Rockland Utilities', 'Non-OBR'],
        value=['National Grid', 'Rochester Gas and Electric', 'NYS Electric and Gas', 'Consolidated Edison',
               'Long Island Power Authority', 'Central Hudson Gas and Electric', 'Municipal Utilities',
               'Orange and Rockland Utilities', 'Non-OBR'],
        multi=True
    ),

    # Seventh filter section (DTI)
    dbc.Row(dbc.Col(html.H6('Select DTI range to visualize:'),
                    ),
            ),
    dcc.RangeSlider(
        id='dti-range-slider',
        step=0.05,
        min=0,
        max=1,
        dots=True,
        value=[0, 1]
    ),

    # Eighth Filter section (OBR Successors)
    dbc.Row(dbc.Col(html.H6('Include OBR Successors in visuals?'),
                    ),
            ),
    dcc.RadioItems(['Yes', 'No'],
                   'Yes',
                   id='obr-successor-radio'
                   ),

    # Summary row
    dbc.Row(
        [
            dbc.Col(
                dcc.Graph(
                    id='table0'),
                width={'size': 6, "offset": 0, 'order': 'first'}
            ),  # end of first table
            dbc.Col(
                dcc.Graph(
                    id='table1'),
                width={'size': 6, "offset": 0, 'order': 'last'}
            ),  # end of second table
        ]
    ),

    # Pie Chart rows
    dbc.Row(
        [
            dbc.Col(dcc.Graph(id='pie_chart1', figure={}),
                    width={'size': True, "offset": 0, 'order': 'first'}
                    ),
            dbc.Col(dcc.Graph(id='pie_chart2', figure={}),
                    width={'size': True, "offset": 0, 'order': 'last'}
                    ),
        ]
    ),
    dbc.Row(
        [
            dbc.Col(dcc.Graph(id='pie_chart3', figure={}),
                    width={'size': True, "offset": 0, 'order': 'first'}
                    ),
            dbc.Col(dcc.Graph(id='pie_chart4', figure={}),
                    width={'size': True, "offset": 0, 'order': 'last'}
                    ),
        ]
    ),

    # Figure rows
    # Fig1
    dbc.Row(
        dcc.Graph(
            id='graph1'),
    ),
    # Fig2
    dbc.Row(
        dcc.Graph(
            id='graph2'),
    ),
    # Fig3
    dbc.Row(
        dcc.Graph(
            id='graph3'),
    ),
    # Fig4
    dbc.Row(
        dcc.Graph(
            id='graph4'),
    ),
    # Fig5
    dbc.Row(
        dcc.Graph(
            id='graph5'),
    ),
    # map1
    dbc.Container(
        dbc.Row(
            dcc.Graph(
                id='map1'), className="h-100"
        ), style={"height": "100vh"},
    )

])


# -------------------------------------------------------------------------------------------------
# table0 callback
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
    # successor filter
    successors_chosen = [i for i in successor_options[successors_chosen]]

    dff = df[((df["SETUP_MONTH"] >= start_date) & (df['SETUP_MONTH'] <= end_date)) &
             (df['LOAN_TYPE'].isin(loan_types_chosen)) &
             (df['UNDERWRITING'].isin(tier_type_chosen)) &
             (df['PURPOSE'].isin(purpose_type_chosen)) &
             (df['PLEDGED'].isin(pledged_status_chosen)) &
             ((df["CREDIT_SCORE_CURRENT_HIGH"] >= fico_score_chosen[0]) & (
                         df['CREDIT_SCORE_CURRENT_HIGH'] <= fico_score_chosen[1])) &
             (df['UTILITY'].isin(utilities_chosen)) &
             ((df["DEBT_TO_INCOME"] >= dti_range_chosen[0]) & (df['DEBT_TO_INCOME'] <= dti_range_chosen[1])) &
             (df['SUCCESSOR_NUMBER'].isin(successors_chosen))
             ]  # the graph/dataframe will be filterd by chosen values

    # Create average calculations for table0
    avg_Orig_loan_amount = "$ {:,.2f}".format(dff['ORIGINAL_LOAN_AMOUNT'].mean())
    avg_int_rate = "{:.2f}%".format(dff['INTEREST_RATE'].mean())
    avg_FICO_score = "{:.0f}".format(dff['CREDIT_SCORE_CURRENT_HIGH'].mean())
    avg_DTI = "{:.2f}".format(dff['DEBT_TO_INCOME'].mean())
    avg_loan_bal = "$ {:,.2f}".format(dff['CURRENT_BALANCE'].mean())
    perc_loan_delinquent = "{:.2f}%".format(
        ((dff['DELINQUENT_AMOUNT']).sum() / dff['ORIGINAL_LOAN_AMOUNT'].sum()) * 1000)
    net_co_rate = "{:.2f}%".format(((dff['CHARGEOFF_AMOUNT']).sum() / dff['ORIGINAL_LOAN_AMOUNT'].sum()) * 100)

    # plot table0
    table0 = go.Figure(data=[go.Table(header=dict(values=['Attributes', 'Value']),
                                      cells=dict(values=[
                                          ['Avg Original Loan Amount', 'Avg. Interest Rate', 'Avg. FICO Score',
                                           'Avg. DTI', 'Avg. Loan Balance', '% Total Loan Value Delinquent',
                                           "Net charge-off rate"],
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
# table1 callback
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
    # successor filter
    successors_chosen = [i for i in successor_options[successors_chosen]]

    dff = df[((df["SETUP_MONTH"] >= start_date) & (df['SETUP_MONTH'] <= end_date)) &
             (df['LOAN_TYPE'].isin(loan_types_chosen)) &
             (df['UNDERWRITING'].isin(tier_type_chosen)) &
             (df['PURPOSE'].isin(purpose_type_chosen)) &
             (df['PLEDGED'].isin(pledged_status_chosen)) &
             ((df["CREDIT_SCORE_CURRENT_HIGH"] >= fico_score_chosen[0]) & (
                         df['CREDIT_SCORE_CURRENT_HIGH'] <= fico_score_chosen[1])) &
             (df['UTILITY'].isin(utilities_chosen)) &
             ((df["DEBT_TO_INCOME"] >= dti_range_chosen[0]) & (df['DEBT_TO_INCOME'] <= dti_range_chosen[1])) &
             (df['SUCCESSOR_NUMBER'].isin(successors_chosen))
             ]  # the graph/dataframe will be filterd by chosen values

    # Create calculations for table1
    # Loan counts
    National_Grid_cnt = len(dff[dff["UTILITY"].str.contains('National Grid')])
    Rochester_Gas_Electric_cnt = len(dff[dff["UTILITY"].str.contains('Rochester Gas and Electric')])
    NYS_Electric_Gas_cnt = len(dff[dff["UTILITY"].str.contains('NYS Electric and Gas')])
    Consolidated_Edison_cnt = len(dff[dff["UTILITY"].str.contains('Consolidated Edison')])
    Long_Island_Power_Authority_cnt = len(dff[dff["UTILITY"].str.contains('Long Island Power Authority')])
    Central_Hudson_Gas_Electric_cnt = len(dff[dff["UTILITY"].str.contains('Central Hudson Gas and Electric')])
    Municipal_Utilities_cnt = len(dff[dff["UTILITY"].str.contains('Municipal Utilities')])
    Orange_Rockland_Utilities_cnt = len(dff[dff["UTILITY"].str.contains('Orange and Rockland Utilities')])
    Non_OBR_cnt = len(dff[dff["UTILITY"].str.contains('Non-OBR')])

    # Orignal Loan amount sum
    National_Grid_orig_sum = "$ {:,.2f}".format(
        dff[dff["UTILITY"].str.contains('National Grid')]['ORIGINAL_LOAN_AMOUNT'].sum())
    Rochester_Gas_Electric_orig_sum = "$ {:,.2f}".format(
        dff[dff["UTILITY"].str.contains('Rochester Gas and Electric')]['ORIGINAL_LOAN_AMOUNT'].sum())
    NYS_Electric_Gas_orig_sum = "$ {:,.2f}".format(
        dff[dff["UTILITY"].str.contains('NYS Electric and Gas')]['ORIGINAL_LOAN_AMOUNT'].sum())
    Consolidated_Edison_orig_sum = "$ {:,.2f}".format(
        dff[dff["UTILITY"].str.contains('Consolidated Edison')]['ORIGINAL_LOAN_AMOUNT'].sum())
    Long_Island_Power_Authority_orig_sum = "$ {:,.2f}".format(
        dff[dff["UTILITY"].str.contains('Long Island Power Authority')]['ORIGINAL_LOAN_AMOUNT'].sum())
    Central_Hudson_Gas_Electric_orig_sum = "$ {:,.2f}".format(
        dff[dff["UTILITY"].str.contains('Central Hudson Gas and Electric')]['ORIGINAL_LOAN_AMOUNT'].sum())
    Municipal_Utilities_orig_sum = "$ {:,.2f}".format(
        dff[dff["UTILITY"].str.contains('Municipal Utilities')]['ORIGINAL_LOAN_AMOUNT'].sum())
    Orange_Rockland_Utilities_orig_sum = "$ {:,.2f}".format(
        dff[dff["UTILITY"].str.contains('Orange and Rockland Utilities')]['ORIGINAL_LOAN_AMOUNT'].sum())
    Non_OBR_orig_sum = "$ {:,.2f}".format(dff[dff["UTILITY"].str.contains('Non-OBR')]['ORIGINAL_LOAN_AMOUNT'].sum())

    # Loan current balance sum
    National_Grid_currbal_sum = "$ {:,.2f}".format(
        dff[dff["UTILITY"].str.contains('National Grid')]['CURRENT_BALANCE'].sum())
    Rochester_Gas_Electric_currbal_sum = "$ {:,.2f}".format(
        dff[dff["UTILITY"].str.contains('Rochester Gas and Electric')]['CURRENT_BALANCE'].sum())
    NYS_Electric_Gas_currbal_sum = "$ {:,.2f}".format(
        dff[dff["UTILITY"].str.contains('NYS Electric and Gas')]['CURRENT_BALANCE'].sum())
    Consolidated_Edison_currbal_sum = "$ {:,.2f}".format(
        dff[dff["UTILITY"].str.contains('Consolidated Edison')]['CURRENT_BALANCE'].sum())
    Long_Island_Power_Authority_currbal_sum = "$ {:,.2f}".format(
        dff[dff["UTILITY"].str.contains('Long Island Power Authority')]['CURRENT_BALANCE'].sum())
    Central_Hudson_Gas_Electric_currbal_sum = "$ {:,.2f}".format(
        dff[dff["UTILITY"].str.contains('Central Hudson Gas and Electric')]['CURRENT_BALANCE'].sum())
    Municipal_Utilities_currbal_sum = "$ {:,.2f}".format(
        dff[dff["UTILITY"].str.contains('Municipal Utilities')]['CURRENT_BALANCE'].sum())
    Orange_Rockland_Utilities_currbal_sum = "$ {:,.2f}".format(
        dff[dff["UTILITY"].str.contains('Orange and Rockland Utilities')]['CURRENT_BALANCE'].sum())
    Non_OBR_currbal_sum = "$ {:,.2f}".format(dff[dff["UTILITY"].str.contains('Non-OBR')]['CURRENT_BALANCE'].sum())

    # plot table1
    table1 = go.Figure(data=[go.Table(header=dict(values=['Utility', 'Loan Count', 'Loan Amount', 'Remaining Balance']),
                                      cells=dict(values=[
                                          ['National Grid', 'Rochester Gas and Electric', 'NYS Electric and Gas',
                                           'Consolidated Edison', 'Long Island Power Authority',
                                           'Central Hudson Gas and Electric',
                                           'Municipal Utilities', 'Orange and Rockland Utilities', 'Non-OBR'
                                           ],
                                          [National_Grid_cnt, Rochester_Gas_Electric_cnt, NYS_Electric_Gas_cnt,
                                           Consolidated_Edison_cnt, Long_Island_Power_Authority_cnt,
                                           Central_Hudson_Gas_Electric_cnt,
                                           Municipal_Utilities_cnt, Orange_Rockland_Utilities_cnt, Non_OBR_cnt],
                                          [National_Grid_orig_sum, Rochester_Gas_Electric_orig_sum,
                                           NYS_Electric_Gas_orig_sum,
                                           Consolidated_Edison_orig_sum, Long_Island_Power_Authority_orig_sum,
                                           Central_Hudson_Gas_Electric_orig_sum,
                                           Municipal_Utilities_orig_sum, Orange_Rockland_Utilities_orig_sum,
                                           Non_OBR_orig_sum],
                                          [National_Grid_currbal_sum, Rochester_Gas_Electric_currbal_sum,
                                           NYS_Electric_Gas_currbal_sum,
                                           Consolidated_Edison_currbal_sum, Long_Island_Power_Authority_currbal_sum,
                                           Central_Hudson_Gas_Electric_currbal_sum,
                                           Municipal_Utilities_currbal_sum, Orange_Rockland_Utilities_currbal_sum,
                                           Non_OBR_currbal_sum],
                                          ],
                                                 ))
                             ])

    return (table1)


# -------------------------------------------------------------------------------------------------
# piechart1 callback
@app.callback(Output('pie_chart1', 'figure'),
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
def update_pie_chart1(start_date, end_date,
                      loan_types_chosen, tier_type_chosen,
                      purpose_type_chosen, pledged_status_chosen,
                      fico_score_chosen, utilities_chosen,
                      dti_range_chosen, successors_chosen):
    # successor filter
    successors_chosen = [i for i in successor_options[successors_chosen]]

    dff = df[((df["SETUP_MONTH"] >= start_date) & (df['SETUP_MONTH'] <= end_date)) &
             (df['LOAN_TYPE'].isin(loan_types_chosen)) &
             (df['UNDERWRITING'].isin(tier_type_chosen)) &
             (df['PURPOSE'].isin(purpose_type_chosen)) &
             (df['PLEDGED'].isin(pledged_status_chosen)) &
             ((df["CREDIT_SCORE_CURRENT_HIGH"] >= fico_score_chosen[0]) & (
                         df['CREDIT_SCORE_CURRENT_HIGH'] <= fico_score_chosen[1])) &
             (df['UTILITY'].isin(utilities_chosen)) &
             ((df["DEBT_TO_INCOME"] >= dti_range_chosen[0]) & (df['DEBT_TO_INCOME'] <= dti_range_chosen[1])) &
             (df['SUCCESSOR_NUMBER'].isin(successors_chosen))
             ]  # the graph/dataframe will be filterd by chosen values

    # create df
    df_piefig1 = dff.groupby('PURPOSE')['ORIGINAL_LOAN_AMOUNT'].agg(['sum', 'count']).reset_index()

    # plot
    pie_fig1 = px.pie(df_piefig1, names='PURPOSE', values='sum',
                      title='Loan Purpose % Distribution by $ Amt',
                      hover_data=['count'],
                      labels={'Tot Loan Amt': 'sum', 'Loan Count': 'count'},
                      custom_data=['count']
                      )
    pie_fig1.update_layout(showlegend=True, title_x=0.5).update_traces(textposition='outside', textinfo='label+percent',
                                                                       hovertemplate="Purpose: %{label}: <br>Tot Loan Amt: $%{value} </br> Loan Count: %{customdata}"
                                                                       )

    return (pie_fig1)


# -------------------------------------------------------------------------------------------------
# piechart2 callback
@app.callback(Output('pie_chart2', 'figure'),
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
def update_pie_chart2(start_date, end_date,
                      loan_types_chosen, tier_type_chosen,
                      purpose_type_chosen, pledged_status_chosen,
                      fico_score_chosen, utilities_chosen,
                      dti_range_chosen, successors_chosen):
    # successor filter
    successors_chosen = [i for i in successor_options[successors_chosen]]

    dff = df[((df["SETUP_MONTH"] >= start_date) & (df['SETUP_MONTH'] <= end_date)) &
             (df['LOAN_TYPE'].isin(loan_types_chosen)) &
             (df['UNDERWRITING'].isin(tier_type_chosen)) &
             (df['PURPOSE'].isin(purpose_type_chosen)) &
             (df['PLEDGED'].isin(pledged_status_chosen)) &
             ((df["CREDIT_SCORE_CURRENT_HIGH"] >= fico_score_chosen[0]) & (
                         df['CREDIT_SCORE_CURRENT_HIGH'] <= fico_score_chosen[1])) &
             (df['UTILITY'].isin(utilities_chosen)) &
             ((df["DEBT_TO_INCOME"] >= dti_range_chosen[0]) & (df['DEBT_TO_INCOME'] <= dti_range_chosen[1])) &
             (df['SUCCESSOR_NUMBER'].isin(successors_chosen))
             ]  # the graph/dataframe will be filterd by chosen values

    # create df
    df_piefig2 = dff.groupby('LOAN_TYPE')['ORIGINAL_LOAN_AMOUNT'].agg(['sum', 'count']).reset_index()

    # plot
    pie_fig2 = px.pie(df_piefig2, names='LOAN_TYPE', values='sum',
                      title='Loan Type % Distribution by $ Amt',
                      hover_data=['count'],
                      labels={'Tot Loan Amt': 'sum', 'Loan Count': 'count'},
                      custom_data=['count']
                      )
    pie_fig2.update_layout(showlegend=True, title_x=0.5).update_traces(textposition='outside', textinfo='label+percent',
                                                                       hovertemplate="Loan Type: %{label}: <br>Tot Loan Amt: $%{value} </br> Loan Count: %{customdata}"
                                                                       )

    return (pie_fig2)


# -------------------------------------------------------------------------------------------------
# piechart3 callback
@app.callback(Output('pie_chart3', 'figure'),
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
def update_pie_chart3(start_date, end_date,
                      loan_types_chosen, tier_type_chosen,
                      purpose_type_chosen, pledged_status_chosen,
                      fico_score_chosen, utilities_chosen,
                      dti_range_chosen, successors_chosen):
    # successor filter
    successors_chosen = [i for i in successor_options[successors_chosen]]

    dff = df[((df["SETUP_MONTH"] >= start_date) & (df['SETUP_MONTH'] <= end_date)) &
             (df['LOAN_TYPE'].isin(loan_types_chosen)) &
             (df['UNDERWRITING'].isin(tier_type_chosen)) &
             (df['PURPOSE'].isin(purpose_type_chosen)) &
             (df['PLEDGED'].isin(pledged_status_chosen)) &
             ((df["CREDIT_SCORE_CURRENT_HIGH"] >= fico_score_chosen[0]) & (
                         df['CREDIT_SCORE_CURRENT_HIGH'] <= fico_score_chosen[1])) &
             (df['UTILITY'].isin(utilities_chosen)) &
             ((df["DEBT_TO_INCOME"] >= dti_range_chosen[0]) & (df['DEBT_TO_INCOME'] <= dti_range_chosen[1])) &
             (df['SUCCESSOR_NUMBER'].isin(successors_chosen))
             ]  # the graph/dataframe will be filterd by chosen values

    # create df
    df_piefig3 = dff.groupby('UNDERWRITING')['ORIGINAL_LOAN_AMOUNT'].agg(['sum', 'count']).reset_index()

    # plot
    pie_fig3 = px.pie(df_piefig3, names='UNDERWRITING', values='sum',
                      title='Loan Tier % Distribution by $ Amt',
                      hover_data=['count'],
                      labels={'Tot Loan Amt': 'sum', 'Loan Count': 'count'},
                      custom_data=['count']
                      )
    pie_fig3.update_layout(showlegend=True, title_x=0.5).update_traces(textposition='outside', textinfo='label+percent',
                                                                       hovertemplate="Tier: %{label}: <br>Tot Loan Amt: $%{value} </br> Loan Count: %{customdata}"
                                                                       )

    return (pie_fig3)


# -------------------------------------------------------------------------------------------------
# piechart4 callback
@app.callback(Output('pie_chart4', 'figure'),
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
def update_pie_chart4(start_date, end_date,
                      loan_types_chosen, tier_type_chosen,
                      purpose_type_chosen, pledged_status_chosen,
                      fico_score_chosen, utilities_chosen,
                      dti_range_chosen, successors_chosen):
    # successor filter
    successors_chosen = [i for i in successor_options[successors_chosen]]

    dff = df[((df["SETUP_MONTH"] >= start_date) & (df['SETUP_MONTH'] <= end_date)) &
             (df['LOAN_TYPE'].isin(loan_types_chosen)) &
             (df['UNDERWRITING'].isin(tier_type_chosen)) &
             (df['PURPOSE'].isin(purpose_type_chosen)) &
             (df['PLEDGED'].isin(pledged_status_chosen)) &
             ((df["CREDIT_SCORE_CURRENT_HIGH"] >= fico_score_chosen[0]) & (
                         df['CREDIT_SCORE_CURRENT_HIGH'] <= fico_score_chosen[1])) &
             (df['UTILITY'].isin(utilities_chosen)) &
             ((df["DEBT_TO_INCOME"] >= dti_range_chosen[0]) & (df['DEBT_TO_INCOME'] <= dti_range_chosen[1])) &
             (df['SUCCESSOR_NUMBER'].isin(successors_chosen))
             ]  # the graph/dataframe will be filterd by chosen values

    # create df
    df_piefig4 = dff.groupby('PLEDGED')['ORIGINAL_LOAN_AMOUNT'].agg(['sum', 'count']).reset_index()

    # plot
    pie_fig4 = px.pie(df_piefig4, names='PLEDGED', values='sum',
                      title='Loan Pledged Status % Distribution by $ Amt',
                      hover_data=['count'],
                      labels={'Tot Loan Amt': 'sum', 'Loan Count': 'count'},
                      custom_data=['count']
                      )
    pie_fig4.update_layout(showlegend=True, title_x=0.5).update_traces(textposition='outside', textinfo='label+percent',
                                                                       hovertemplate="Tier: %{label}: <br>Tot Loan Amt: $%{value} </br> Loan Count: %{customdata}"
                                                                       )

    return (pie_fig4)


# -------------------------------------------------------------------------------------------------
# fig1 callback
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
    # successor filter
    successors_chosen = [i for i in successor_options[successors_chosen]]

    dff = df[((df["SETUP_MONTH"] >= start_date) & (df['SETUP_MONTH'] <= end_date)) &
             (df['LOAN_TYPE'].isin(loan_types_chosen)) &
             (df['UNDERWRITING'].isin(tier_type_chosen)) &
             (df['PURPOSE'].isin(purpose_type_chosen)) &
             (df['PLEDGED'].isin(pledged_status_chosen)) &
             ((df["CREDIT_SCORE_CURRENT_HIGH"] >= fico_score_chosen[0]) & (
                         df['CREDIT_SCORE_CURRENT_HIGH'] <= fico_score_chosen[1])) &
             (df['UTILITY'].isin(utilities_chosen)) &
             ((df["DEBT_TO_INCOME"] >= dti_range_chosen[0]) & (df['DEBT_TO_INCOME'] <= dti_range_chosen[1])) &
             (df['SUCCESSOR_NUMBER'].isin(successors_chosen))
             ]  # the graph/dataframe will be filterd by chosen values

    # create df
    df_fig1 = dff.groupby('SETUP_MONTH')["ORIGINAL_LOAN_AMOUNT"].agg(['sum', 'count']).reset_index()

    # plot
    fig1 = px.line(df_fig1, x='SETUP_MONTH', y='sum')
    fig1.update_traces(mode="markers+lines", text=df_fig1['count'],
                       hovertemplate='<b>Month</b>: %{x}<br>'
                                     + '<i>Sum</i>: $%{y:,.2f}<br>'
                                     + '<i>Count</i>: %{text}</b>',
                       )
    fig1.update_layout(title_text="Total Loan Value ($) Originated",
                       xaxis_title="Loan Origination Month",
                       yaxis_title="Cumulative Dollar Amount ($)")

    return (fig1)


# ---------------------------------------------------------------------------------------------------------------
# fig2 callback
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
    # successor filter
    successors_chosen = [i for i in successor_options[successors_chosen]]

    # dataframe filters
    dff = df[((df["SETUP_MONTH"] >= start_date) & (df['SETUP_MONTH'] <= end_date)) &
             (df['LOAN_TYPE'].isin(loan_types_chosen)) &
             (df['UNDERWRITING'].isin(tier_type_chosen)) &
             (df['PURPOSE'].isin(purpose_type_chosen)) &
             (df['PLEDGED'].isin(pledged_status_chosen)) &
             ((df["CREDIT_SCORE_CURRENT_HIGH"] >= fico_score_chosen[0]) & (
                         df['CREDIT_SCORE_CURRENT_HIGH'] <= fico_score_chosen[1])) &
             (df['UTILITY'].isin(utilities_chosen)) &
             ((df["DEBT_TO_INCOME"] >= dti_range_chosen[0]) & (df['DEBT_TO_INCOME'] <= dti_range_chosen[1])) &
             (df['SUCCESSOR_NUMBER'].isin(successors_chosen))
             ]  # the graph/dataframe will be filterd by chosen values

    # fig2 update
    # Create df subset
    df_fig2 = dff.groupby(['SETUP_MONTH', 'PURPOSE'])['ORIGINAL_LOAN_AMOUNT'] \
        .agg(['sum', 'count', 'mean']).reset_index().rename(columns={'SETUP_MONTH': 'Origination Month',
                                                                     'PURPOSE': 'Loan Purpose',
                                                                     'sum': 'Sum',
                                                                     'count': 'Count',
                                                                     'mean': 'Mean'}
                                                            )

    # Plot loan purposes
    fig2 = px.bar(df_fig2,
                  barmode='stack',
                  x='Origination Month',
                  y='Sum',
                  color='Loan Purpose',
                  custom_data=[df_fig2['Loan Purpose'],
                               df_fig2['Count'],
                               df_fig2['Mean']]
                  )

    # Update layout
    fig2.update_layout(
        title="Loan Purpose Dollar Amount Originated by Month",
        xaxis_title="Loan Origination Month",
        yaxis_title="Dollar Amount ($)",
        legend_title="Purpose"
    )

    fig2.update_traces(hovertemplate='<b>Loan Purpose</b>: %{customdata[0]}<br>' +
                                     '<i>Origination Month</i>: %{x}<br>' +
                                     '<i>Sum</i>: $%{y:,.2f}<br>' +
                                     '<i>Count</i>: %{customdata[1]}<br>' +
                                     '<i>Average</i>: $%{customdata[2]:,.2f}</b>'
                       )

    return (fig2)


# ----------------------------------------------------------------------------------------------------------------
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
    # successor filter
    successors_chosen = [i for i in successor_options[successors_chosen]]

    # dataframe filters
    dff = df[((df["SETUP_MONTH"] >= start_date) & (df['SETUP_MONTH'] <= end_date)) &
             (df['LOAN_TYPE'].isin(loan_types_chosen)) &
             (df['UNDERWRITING'].isin(tier_type_chosen)) &
             (df['PURPOSE'].isin(purpose_type_chosen)) &
             (df['PLEDGED'].isin(pledged_status_chosen)) &
             ((df["CREDIT_SCORE_CURRENT_HIGH"] >= fico_score_chosen[0]) & (
                         df['CREDIT_SCORE_CURRENT_HIGH'] <= fico_score_chosen[1])) &
             (df['UTILITY'].isin(utilities_chosen)) &
             ((df["DEBT_TO_INCOME"] >= dti_range_chosen[0]) & (df['DEBT_TO_INCOME'] <= dti_range_chosen[1])) &
             (df['SUCCESSOR_NUMBER'].isin(successors_chosen))
             ]  # the graph/dataframe will be filterd by chosen values

    # fig3 update
    ##fig3 df update
    df_fig3 = dff.groupby(['SETUP_MONTH', 'LOAN_TYPE'])['ORIGINAL_LOAN_AMOUNT'] \
        .agg(['sum', 'count', 'mean']).reset_index().rename(columns={'SETUP_MONTH': 'Origination Month',
                                                                     'LOAN_TYPE': 'Loan Type',
                                                                     'sum': 'Sum',
                                                                     'count': 'Count',
                                                                     'mean': 'Mean'}
                                                            )
    # Plot loan type
    fig3 = px.bar(df_fig3,
                  barmode='stack',
                  x='Origination Month',
                  y='Sum',
                  color='Loan Type',
                  custom_data=[df_fig3['Loan Type'],
                               df_fig3['Count'],
                               df_fig3['Mean']]
                  )

    # Update layout
    fig3.update_layout(
        title="Loan Type Dollar Amount Originated by Month",
        xaxis_title="Loan Origination Month",
        yaxis_title="Dollar Amount ($)",
        legend_title="Type"
    )

    fig3.update_traces(hovertemplate='<b>Loan Type</b>: %{customdata[0]}<br>' +
                                     '<i>Origination Month</i>: %{x}<br>' +
                                     '<i>Sum</i>: $%{y:,.2f}<br>' +
                                     '<i>Count</i>: %{customdata[1]}<br>' +
                                     '<i>Average</i>: $%{customdata[2]:,.2f}</b>'
                       )

    return (fig3)


# ----------------------------------------------------------------------------------------------------------------
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
    # successor filter
    successors_chosen = [i for i in successor_options[successors_chosen]]

    # dataframe filters
    dff = df[((df["SETUP_MONTH"] >= start_date) & (df['SETUP_MONTH'] <= end_date)) &
             (df['LOAN_TYPE'].isin(loan_types_chosen)) &
             (df['UNDERWRITING'].isin(tier_type_chosen)) &
             (df['PURPOSE'].isin(purpose_type_chosen)) &
             (df['PLEDGED'].isin(pledged_status_chosen)) &
             ((df["CREDIT_SCORE_CURRENT_HIGH"] >= fico_score_chosen[0]) & (
                         df['CREDIT_SCORE_CURRENT_HIGH'] <= fico_score_chosen[1])) &
             (df['UTILITY'].isin(utilities_chosen)) &
             ((df["DEBT_TO_INCOME"] >= dti_range_chosen[0]) & (df['DEBT_TO_INCOME'] <= dti_range_chosen[1])) &
             (df['SUCCESSOR_NUMBER'].isin(successors_chosen))
             ]  # the graph/dataframe will be filterd by chosen values

    # fig4 update
    ##fig4 df update
    df_fig4 = dff.groupby(['SETUP_MONTH', 'UNDERWRITING'])['ORIGINAL_LOAN_AMOUNT'] \
        .agg(['sum', 'count', 'mean']).reset_index().rename(columns={'SETUP_MONTH': 'Origination Month',
                                                                     'UNDERWRITING': 'Tier',
                                                                     'sum': 'Sum',
                                                                     'count': 'Count',
                                                                     'mean': 'Mean'}
                                                            )
    # Plot loan underwriting type
    fig4 = px.bar(df_fig4,
                  barmode='stack',
                  x='Origination Month',
                  y='Sum',
                  color='Tier',
                  custom_data=[df_fig4['Tier'],
                               df_fig4['Count'],
                               df_fig4['Mean']]
                  )

    # Update layout
    fig4.update_layout(
        title="Loan Tier Dollar Amount Originated by Month",
        xaxis_title="Loan Origination Month",
        yaxis_title="Dollar Amount ($)",
        legend_title="Underwriting",
    )

    fig4.update_traces(hovertemplate='<b>Loan Tier</b>: %{customdata[0]}<br>' +
                                     '<i>Origination Month</i>: %{x}<br>' +
                                     '<i>Sum</i>: $%{y:,.2f}<br>' +
                                     '<i>Count</i>: %{customdata[1]}<br>' +
                                     '<i>Average</i>: $%{customdata[2]:,.2f}</b>'
                       )

    return (fig4)


# ----------------------------------------------------------------------------------------------------------------
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
    # successor filter
    successors_chosen = [i for i in successor_options[successors_chosen]]

    # dataframe filters
    dff = df[((df["SETUP_MONTH"] >= start_date) & (df['SETUP_MONTH'] <= end_date)) &
             (df['LOAN_TYPE'].isin(loan_types_chosen)) &
             (df['UNDERWRITING'].isin(tier_type_chosen)) &
             (df['PURPOSE'].isin(purpose_type_chosen)) &
             (df['PLEDGED'].isin(pledged_status_chosen)) &
             ((df["CREDIT_SCORE_CURRENT_HIGH"] >= fico_score_chosen[0]) & (
                         df['CREDIT_SCORE_CURRENT_HIGH'] <= fico_score_chosen[1])) &
             (df['UTILITY'].isin(utilities_chosen)) &
             ((df["DEBT_TO_INCOME"] >= dti_range_chosen[0]) & (df['DEBT_TO_INCOME'] <= dti_range_chosen[1])) &
             (df['SUCCESSOR_NUMBER'].isin(successors_chosen))
             ]  # the graph/dataframe will be filterd by chosen values

    df_fig5_cnt = dff.groupby(['SETUP_MONTH', 'PURPOSE'])['ORIGINAL_LOAN_AMOUNT'].count().unstack(
        'PURPOSE').reset_index()

    # fig5 update
    fig5 = px.line(df_fig5_cnt, x='SETUP_MONTH', y=df_fig5_cnt.columns.tolist())

    # Update layout
    fig5.update_layout(
        title="Loan Purpose Count Originated by Month",
        xaxis_title="Loan Origination Month",
        yaxis_title="Loan Count",
        legend_title="Purpose"
    )

    fig5.update_traces(hovertemplate='<b>Month</b>: %{x}<br>'
                                     + '<i>Sum</i>: Debug<br>'
                                     + '<i>Count</i>: %{y:,.0f}</b>'
                       )

    # Create df subset
    df_fig5 = dff.groupby(['SETUP_MONTH', 'PURPOSE'])['ORIGINAL_LOAN_AMOUNT'] \
        .agg(['sum', 'count', 'mean']).reset_index().rename(columns={'SETUP_MONTH': 'Origination Month',
                                                                     'PURPOSE': 'Purpose',
                                                                     'sum': 'Sum',
                                                                     'count': 'Count',
                                                                     'mean': 'Mean'}
                                                            )

    # Plot loan purposes
    fig5 = px.line(df_fig5, x='Origination Month', y='Count', color='Purpose',
                   custom_data=[df_fig5['Purpose'],
                                df_fig5['Sum'],
                                df_fig5['Mean']]
                   )

    # Update layout
    fig5.update_layout(
        title="Loan Purpose Count Originated by Month",
        xaxis_title="Loan Origination Month",
        yaxis_title="Loan Count",
        legend_title="Purpose"
    )

    fig5.update_traces(hovertemplate='<b>Loan Purpose</b>: %{customdata[0]}<br>' +
                                     '<i>Origination Month</i>: %{x}<br>' +
                                     '<i>Sum</i>: $%{customdata[1]:,.2f}<br>' +
                                     '<i>Count</i>: %{y}<br>' +
                                     '<i>Average</i>: $%{customdata[2]:,.2f}</b>'
                       )

    return (fig5)


# ----------------------------------------------------------------------------------------------------------------
# map1 callback
@app.callback(
    Output("map1", "figure"),
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
def display_choropleth(start_date, end_date,
                       loan_types_chosen, tier_type_chosen,
                       purpose_type_chosen, pledged_status_chosen,
                       fico_score_chosen, utilities_chosen,
                       dti_range_chosen, successors_chosen):
    # successor filter
    successors_chosen = [i for i in successor_options[successors_chosen]]

    # dataframe filters
    dff = df[((df["SETUP_MONTH"] >= start_date) & (df['SETUP_MONTH'] <= end_date)) &
             (df['LOAN_TYPE'].isin(loan_types_chosen)) &
             (df['UNDERWRITING'].isin(tier_type_chosen)) &
             (df['PURPOSE'].isin(purpose_type_chosen)) &
             (df['PLEDGED'].isin(pledged_status_chosen)) &
             ((df["CREDIT_SCORE_CURRENT_HIGH"] >= fico_score_chosen[0]) & (
                         df['CREDIT_SCORE_CURRENT_HIGH'] <= fico_score_chosen[1])) &
             (df['UTILITY'].isin(utilities_chosen)) &
             ((df["DEBT_TO_INCOME"] >= dti_range_chosen[0]) & (df['DEBT_TO_INCOME'] <= dti_range_chosen[1])) &
             (df['SUCCESSOR_NUMBER'].isin(successors_chosen))
             ]  # the graph/dataframe will be filterd by chosen values

    # create dataframe
    # Merge fipsdf and map_df based on both (County and state) attributes
    map_df = pd.merge(dff, df_fips, on=['PROPERTY_COUNTY', 'PROPERTY_STATE'], how="left")

    # Group by County/CountyFIPS and sum/count original loan amounts
    map_color_orig_Loan_sumcnt = pd.DataFrame.from_dict(
        map_df.groupby(['PROPERTY_COUNTY', 'CountyFIPS'])['ORIGINAL_LOAN_AMOUNT'].agg(['sum', 'count']).reset_index())

    map_fig = px.choropleth_mapbox(map_color_orig_Loan_sumcnt, geojson=counties, locations='CountyFIPS', color='sum',
                                   color_continuous_scale=[[0, 'rgb(250, 250, 110)'],
                                                           [0.05, 'rgb(134, 215, 128)'],
                                                           [0.90, 'rgb(35, 170, 143)'],
                                                           [0.95, 'rgb(0, 120, 130)'],
                                                           [1, 'rgb(42, 72, 88)']
                                                           ],
                                   range_color=(0, map_color_orig_Loan_sumcnt['sum'].max()),
                                   mapbox_style="carto-positron",
                                   zoom=6, center={"lat": 42.7128, "lon": -75.5},
                                   labels={'sum': '$'},
                                   custom_data=[map_color_orig_Loan_sumcnt['PROPERTY_COUNTY'],  # hover data
                                                map_color_orig_Loan_sumcnt['sum'],
                                                map_color_orig_Loan_sumcnt['count']
                                                ]
                                   )

    # map_fig.update_geos(fitbounds="locations", visible=False)
    map_fig.update_layout(title='Loan Origination Density by Dollar ($) Amount',
                          title_x=0.5,
                          margin={"r": 0, "t": 0, "l": 0, "b": 0}
                          )

    # Create custom hover template for hover event
    hovertemp = '<i>County:</i> %{customdata[0]}<br>'
    hovertemp += '<i>Loan Sum: $</i> %{customdata[1]:,.2f}<br>'
    hovertemp += '<i>Loan Count:</i> %{customdata[2]:,.0f}<br>'

    # Set hover template
    map_fig.update_traces(hovertemplate=hovertemp)

    return map_fig


# run app
if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)  # Turn off reloader if inside Jupyter