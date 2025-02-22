############## Constistuent.Online #################
####### Code-free analysis for curious folk. ######

### An application for ...

## streamlit run "C:\Users\Jack\Documents\Python_projects\streamlit_apps\parli_pollingplace_dashboard\streamlit_app.py"

### --------------------------------------- IMPORTS 

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import customChartDefaultStyling

pd.set_option('display.max_columns', None)

### 
headers = {
    "content-type": "application/json"
}

css = 'body, html, p, h1, .st-emotion-cache-1104ytp h1, [class*="css"] {font-family: "Inter", sans-serif;}'
st.markdown( f'<style>{css}</style>' , unsafe_allow_html= True)

### ---------------------------------------- FUNCTIONS 

def prefdist(chosen_df, chosen_state, chosen_electorate, chosen_pollingplace):

    df_prefdist = pd.DataFrame()
            
    df_analysis = chosen_df.copy().loc[(chosen_df.StateAb == chosen_state) & (chosen_df.DivisionNm == chosen_electorate)] 
    df_analysis['PartyAb'] = np.where(df_analysis['PartyAb'] == 'IND', 'IND' + '_' + df_analysis['Surname'].str[0:4], df_analysis['PartyAb'])    
   
    parties = df_analysis['PartyAb'].unique()
    count_col = 'CountNum' if 'CountNum' in df_analysis.columns else 'CountNumber'
    counts = df_analysis[count_col].unique()

    for count in counts:

        df_count = df_analysis.loc[(df_analysis[count_col] == count) & (df_analysis.CalculationType == 'Preference Count')]
        df_count = df_count.sort_values(by = 'CalculationValue', ascending = False)        
        
        for party in parties:        
            cv = df_count.loc[df_count['PartyAb'] == party, 'CalculationValue'].values[0]            
            df_prefdist.loc[party, count] = cv

    df_prefdist = df_prefdist.astype(int)
    
    cols = list(df_prefdist.columns)
    cols.reverse()
    df_prefdist = df_prefdist.sort_values(by = cols, ascending = False)
   
    return df_prefdist


def plotter(chosen_df, chosen_state, chosen_electorate, chosen_pollingplace):
    
    df_prefdist = prefdist(chosen_df, chosen_state, chosen_electorate, chosen_pollingplace)
    
    df_analysis = chosen_df.copy().loc[(chosen_df.StateAb == chosen_state) & (chosen_df.DivisionNm == chosen_electorate)] 
    df_analysis['PartyAb'] = np.where(df_analysis['PartyAb'] == 'IND', 'IND' + '_' + df_analysis['Surname'].str[0:4], df_analysis['PartyAb'])
        
    parties = df_analysis['PartyAb'].unique()
    count_col = 'CountNum' if 'CountNum' in df_analysis.columns else 'CountNumber'
    counts = df_analysis[count_col].unique()

    party_colors = {
        
        'ALP': 'maroon',
        'LP': 'blue',
        'LNP': 'blue',
        'NAT': 'darkgreen',
        'CLP': 'darkgreen',
        'GVIC': 'green', 
        'GRN': 'green'

    }
    
    fig = go.Figure() 
        
    for party in parties:
                
        values = [x if x != 0 else None for x in df_prefdist.loc[party]]
        
        color = 'silver'
        if party in party_colors.keys():
            color = party_colors[party]
        
        fig.add_trace(
            go.Scatter(
                
                mode = 'markers+lines',
                name = party,
                x = df_prefdist.columns, 
                y = values,
                
                marker = dict(
                    size = 5,
                ),
                
                line = dict(
                    width = 2, 
                    color = color
                )
            )
        )
                
        
    fig.update_layout(title = f'<b>{chosen_electorate} ({chosen_state}) - {chosen_pollingplace}</b><br><sup>party tally through the preference distributions</sup>')
    customChartDefaultStyling.styling(fig)
    fig.update_layout(width = 1200, height = 600)
    fig.update_xaxes(title = '<b>Counts</b>', tickangle = 0)
    fig.update_yaxes(title = '<b>Votes</b>')
    fig.update_layout(legend=dict(orientation='h', font = dict(size = 10, color = "#181818")))
    fig.update_layout(legend={'y':-0.1,'x':0,'xanchor': 'left','yanchor': 'top'})

    st.plotly_chart(fig, use_container_width=True)
                

### _________________________________________ RUN

st.markdown("**Open Investigation Tools** | [constituent.online](%s)" % 'http://www.constituent.online')
    
st.title('Polling Place Preference Tracker - 2022 Australian Election')
st.write('Because all politics is local.')


### 

chosen_pollingplace = '*** ALL ***'

df_MAIN = pd.read_csv('https://raw.githubusercontent.com/jckkrr/Polling-Place-Preference-Tracker---2022-Australian-Election/refs/heads/main/data/2022%20Australian%20Election%20AEC%20Data%20-%20HouseDopByDivisionDownload-27966.csv', skiprows = 0, header = 1)

col1, col2, col3 = st.columns([1,2,3])
with col1: 
    states = df_MAIN['StateAb'].unique() 
    chosen_state = st.selectbox('State:', (states))
    df_state = df_MAIN.loc[df_MAIN.StateAb == chosen_state]
with col2: 
    state_electorates = df_state['DivisionNm'].unique()
    chosen_electorate = st.selectbox('Electorate:', (state_electorates))
    chosen_df = df_state
with col3:
    electorate_pollingplaces = ['*** ALL ***']
    
    electorate_files = {
        'Cooper': 'VIC-COOP',
        'Wannon': 'VIC-WANN',
        'Wills': 'VIC-WILL', 
    }
    
    if chosen_electorate in electorate_files.keys():

        df_electorate = pd.read_csv(f'https://raw.githubusercontent.com/jckkrr/Polling-Place-Preference-Tracker---2022-Australian-Election/refs/heads/main/HouseDopByPPDownload-27966-{electorate_files[chosen_electorate]}.csv', skiprows = 0, header = 1)
    
        electorate_pollingplaces = list(df_electorate['PPNm'].unique())
        electorate_pollingplaces.insert(0, '*** ALL ***')
        
        chosen_pollingplace = st.selectbox('Polling Place:', (electorate_pollingplaces))
        
        if chosen_pollingplace != '*** ALL ***':
            chosen_df = df_electorate.loc[df_electorate['PPNm'] == chosen_pollingplace]
            
            
            
df_prefdist = prefdist(chosen_df, chosen_state, chosen_electorate, chosen_pollingplace)

plotter(chosen_df, chosen_state, chosen_electorate, chosen_pollingplace)

st.table(df_prefdist.style.format("{:,.0f}"))

cell_hover = {  # for row hover use <tr> instead of <td>
    'selector': 'td:hover',
    'props': [('background-color', 'aqua')]
}
index_names = {
    'selector': '.index_name',
    'props': 'font-style: italic; color: darkgrey; font-weight:normal;  text-align:center'
}
headers = {
    'selector': 'th:not(.index_name)',
    'props': 'background-color: #fefefe; color: #181818; font-size: 10pt; text-align:right; font-weight: bold;'
}
s = df_prefdist.style.set_properties(**{'font-size': '10pt'}).format("{:,.0f}").bar(subset=df_prefdist.columns, color='lightgreen')
s.set_table_styles([cell_hover, index_names, headers])
st.table(s.set_table_styles([cell_hover, index_names, headers]))




#def color_survived(val):
#    color = f'rgba({val/255},25,222,0.3)' if val else '#181818'
#    return f'background-color: {color}'
#st.table(df_prefdist.style.format("{:,.0f}").applymap(color_survived, subset=[x for x in df_prefdist.columns]))

