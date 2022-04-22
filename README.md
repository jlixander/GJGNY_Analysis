# Green Jobs Green New York Residential Loan Performance

## Overview
This project consists of exploring the performance of the Green Jobs Green New York (GJGNY) Residential Loan Portfolio. We will use multiple visualization tools to evaluate which loan attributes can give us insight into performance and quantitative metrics. Additionally, we will design an interactive Plotly Dashboard that can be used to extract graphs and tables as desired. The dashboard will have multiple attribute filters that will apply across the whole board as selected. Lastly, the dashboard will be coded in a scalable manner where it'll adjust as the loan portfolio continues to increase. In essence, this dashboard will be able to be connected to a relational database with the ability to auto-update on the first day of each month.

## Why GJGNY?
The GJGNY program has enabled more than 34,000 New Yorkers the ability to finance energy efficiency services and/or cleaner energy alternatives for their homes. This includes, but is not limited to: Solar Panels, Air Sealing services, Air Source Heatpumps, and Ground Source Heatpumps.

### Questions We Hope to Answer:
* Which services are being financed the most? Do Energy Efficiency Loans still dominate the portfolio? 
* Do interest rate levels impact the demand of GJGNY loans?
* How do loan types compare? Does the ease of payment make On-Bill Recovery (OBR) loans a more popular choice?
* Which underwriting category is most common? Tier 1 or Tier 2?
* What charge-off correlations can we find between attributes?
* Does the age of a loan affect charge off rate? Does Debt-To-Income ratios and FICO Scores have an impact?
* Is the payment amount based on loan term linear? Who is paying the most on a monthly basis?
* Who are the top performing contractors in terms of loan quantity? Is it possible some contractors oversell service?
* Can we pinpoint which NY counties take the most and least advantage of the GJGNY program?


## About the Data
* The dataset is from OpenNY's online website.
* The dataset starts from November 2010 and continues through the end of 12/31/2021.
* The data is composed of the following:
    * 34,106 loans
    * Each row corresponds to one loan.

### Matrix Columns
* Please use the following link for a detailed description of each field: https://data.ny.gov/Energy-Environment/Green-Jobs-Green-New-York-GJGNY-Residential-Loan-P/9evn-drxk

### Data Preprocessing
* Column headers were formatted to replace spaces with underscores
* We extracted three dates into variables.
1) The most recent date found in the dataset 
2) A date delta of three years prior to the most recent date 
3) The oldest date in the dataset
* Fixed some contractor names to have the same format to avoid duplicate binning
* Created dataframe subsets by pivoting certain attributes. I.e.: Loan Purpose
* Calculated percent chargeoff of loans
* Split the GEOREFERENCE column into two columns, Latitude and Longitude.

## Results
* As recent as August 2020 Solar PV loans have seen a spike in interest constituting about 58.4% of all funds disbursed for loans.
![Distribution of loan funds since Aug 2020](https://raw.githubusercontent.com/jlixander/GJGNY_Analysis/main/Graphs_and_dataframes/newplot.png)
![Loan Purpose Trends (Program To Date)](https://raw.githubusercontent.com/jlixander/GJGNY_Analysis/main/Graphs_and_dataframes/newplot%20(1).png)

* It was found that GJGNY loans are much more in demand if the interest rate is below 3.75%.
![GJGNY Total Loan Amount Issued by Year)](https://raw.githubusercontent.com/jlixander/GJGNY_Analysis/main/Graphs_and_dataframes/GJGNY%20Total%20Loan%20Amount%20Issued%20by%20Year.png)

* On-Bill Recovery (OBR) loans only constitute about 37.2% of the portfolio. By looking at the past three years we also found that they have become less popular over time. Smart Energy loans have been the most popular since program inception.
![Distribution of loan type (Program To Date)](https://raw.githubusercontent.com/jlixander/GJGNY_Analysis/main/Graphs_and_dataframes/newplot%20(3).png)
![Distribution of loan type since December 2018](https://raw.githubusercontent.com/jlixander/GJGNY_Analysis/main/Graphs_and_dataframes/newplot%20(2).png)

* According to the data, the average interest rate for both, Tier 1 and Tier 2, is 3.73% and 3.67%, respectively. However, applicants seem to qualify mostly for Tier 1 loans which constitute 82.2% of the loan portfolio.
![Distribution of loan tier (Program To Date)](https://raw.githubusercontent.com/jlixander/GJGNY_Analysis/main/Graphs_and_dataframes/newplot%20(4).png)

* Ironically, when comparing delinquency rate between Payment Amount and Debt To Income level, it was found that borrowers are less likely to become delinquent if their loan payment is above $100. At a DTI of 0.20% and under we start to see a decline of delinquency in borrowers. It was also found that borrowers are less likely become delinquent after their 40th payment and if their monthly payment is above $100. Lastly, there is a decline in delinquency for borrowers with a Credit Score above 700.
![Loans Delinquent (Payment Amt Vs DTI)](https://raw.githubusercontent.com/jlixander/GJGNY_Analysis/main/Graphs_and_dataframes/GJGNY%20Res%20Loans%20120%2B%20Days%20Delinquent%20(Payment%20Amt%20vs%20DTI).png)
![Loans Delinquent (Payment Amt Vs Delinquency Start)](https://raw.githubusercontent.com/jlixander/GJGNY_Analysis/main/Graphs_and_dataframes/GJGNY%20Res%20Loans%20Delinquency%20Start.png)
![Loans Delinquent (Credit Score Vs DTI)](https://raw.githubusercontent.com/jlixander/GJGNY_Analysis/main/Graphs_and_dataframes/GJGNY%20Res%20Loans%20120%2B%20Days%20Delinquent.png)

* GJGNY loans are offered in three different terms. 60, 120, and 180 months. As expected, 60 month loan terms have the highest average monthly payment. However, the 180 month term loans have a higher average monthly payment than 120 month term loans. By exploring the dataset further, we found that contractors that focus on Solar PV loans average a higher montly payment than those who focus on Energy Efficiency. To confirm this we may create a boxplot of loan purposes with all three loan terms side by side.
![Average Payment Amount by Loan Term)](https://raw.githubusercontent.com/jlixander/GJGNY_Analysis/main/Graphs_and_dataframes/GJGNY%20Res%20Loans%20-%20Average%20Payment%20Amt%20by%20Loan%20Term.png)
![Average Monthly Payment Amount by Top Contractors)](https://raw.githubusercontent.com/jlixander/GJGNY_Analysis/main/Graphs_and_dataframes/GJGNY%20Res%20Loans%20-%20Average%20Payment%20Amt%20by%20Contractor.png)


* The top performing contractors by loan quantity are as follows:
![Average Monthly Payment Amount by Top Contractors)](https://raw.githubusercontent.com/jlixander/GJGNY_Analysis/main/Graphs_and_dataframes/GJGNY%20Res%20Loans%20Highest%20Performing%20Contractors.png)
By looking at the loan delinquency rate we could determine if a borrower may be unhappy with the provided services. We found that J SYNERGY GREEN INC, BUFFALO ENERGY INC, HOME COMFORT HEATING AND COOLING-ROCHESTER, GREEN AUDIT USA, INC, ENERGY SAVERS INC, and POWERSMITH each have the highest loan deliquency rate at more that 7.21% off all customers.
![Loan Delinquency Rate by Contractor)](https://raw.githubusercontent.com/jlixander/GJGNY_Analysis/main/Graphs_and_dataframes/Loan%20Default%20Rate%20Grouped%20by%20Contractor.png)

* After mapping all loans acroos New York State, it was found that the biggest loan concentration is found across the Long Island Peninsula. Other concentrations include major cities such as Albany, NY and Buffalo, NY.
![GJGNY Residential Loan Portfolio Map)](https://raw.githubusercontent.com/jlixander/GJGNY_Analysis/main/Graphs_and_dataframes/Map.png)


## Potential Next Steps for the Performance Report and Plotly Dashboard
* Create a written PDF report template to be used with the graphs/tables generated by the python script. Could potentially be used for fiscal reports.
* Style the Plotly Dashboard page with CSS or bootstrap cards
* Program the Plotly Dash map section to serve as a filter across the whole dashboard by using the "Lasso Select" feature.
* Connect the Plotly Dashboard to a database that houses updated data.

## Languages, Technologies, Tools, and Algorithms
* Python/Jupyter Notebook/PyCharm/Visual Studio Code
* matplotlib/NumPy
* Plotly Dash/Bootstrap/Gunicorn/Heroku/GitHub

## Resources
* Live Plotly Dashboard - https://plotly-dash-gjgny-showcase.herokuapp.com/
* Github - https://github.com/jlixander/GJGNY_Analysis
* Data Source - https://data.ny.gov/Energy-Environment/Green-Jobs-Green-New-York-GJGNY-Residential-Loan-P/9evn-drxk/data
