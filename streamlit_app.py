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

def frame_name_clean(df):
    
    df = df.rename(columns = {'CountNumber': 'CountNum'})
       
    update_party_names = pd.read_csv('https://raw.githubusercontent.com/jckkrr/Polling-Place-Preference-Tracker---2022-Australian-Election/refs/heads/main/update_party_names.csv').to_dict()
    update_party_names = dict(zip(update_party_names['OldNm'].values(), update_party_names['NewNm'].values()))
        
    if 'PartyNm' in df.columns:
        for party_name in update_party_names.keys():
            df.PartyNm = np.where(df.PartyNm == party_name, update_party_names[party_name], df.PartyNm)
    df['PartyNm'] = np.where(df['PartyNm'] == 'Independent', ' ' + df['GivenNm'] + ' ' + df['Surname'] + ' (IND)', df['PartyNm'])
        
    update_party_abbreviations = pd.read_csv('https://raw.githubusercontent.com/jckkrr/Polling-Place-Preference-Tracker---2022-Australian-Election/refs/heads/main/update_party_abbreviations.csv').to_dict()
    update_party_abbreviations = dict(zip(update_party_abbreviations['OldAb'].values(), update_party_abbreviations['NewAb'].values()))
    if 'PartyAb' in df.columns:
        for party_ab in update_party_abbreviations.keys():
            df.PartyAb = np.where(df.PartyAb == party_ab, update_party_abbreviations[party_ab], df.PartyAb)
    df['PartyAb'] = np.where(df['PartyAb'] == 'IND', 'IND' + '_' + df['Surname'].str.replace(' ','').str[0:4], df['PartyAb'])

    return df


def twoparty_prefdist_horizontalbar_base(chosen_state, chosen_electorate, chosen_pollingplace, tiered_base):

    ### Assemble the data
    
    df_MAIN_electorate = df_MAIN.copy().loc[(df_MAIN['StateAb'] == chosen_state) & (df_MAIN['DivisionNm'] == chosen_electorate)]
    df_MAIN_electorate['PartyAb'] = np.where(df_MAIN_electorate['PartyAb'] == 'IND', 'IND' + '_' + df_MAIN_electorate['Surname'].str[0:4], df_MAIN_electorate['PartyAb'])
    df_MAIN_electorate_countmax = df_MAIN_electorate['CountNum'].max()
    last_two_parties = df_MAIN_electorate.loc[(df_MAIN_electorate['CountNum'] == df_MAIN_electorate_countmax) & (df_MAIN_electorate['CalculationType'] == 'Preference Count') & (df_MAIN_electorate['CalculationValue'] > 0)].sort_values(by = 'CalculationValue', ascending = False)['PartyAb'].values.tolist()
    last_two_parties = list(reversed(last_two_parties))  ### So the winner goes on top
        
    ##
    
    if chosen_pollingplace == 'ALL':
        df_electorate = df_MAIN_electorate
        df_electorate['PPNm'] = 'ALL'     
        
    else:    
        electorate_file_slug = f'{chosen_state}-{chosen_electorate.upper()[0:4]}'
        electorate_file = f'http://constituent.online/parli/aec_data/australia/australia/2022/HouseDopByPPDownload-27966-VIC/HouseDopByPPDownload-27966-{electorate_file_slug}.csv'
        df_electorate = pd.read_csv(electorate_file, skiprows = 0, header = 1)  
    
    df_electorate = frame_name_clean(df_electorate)
        
    party_colors = dict(zip(pd.read_csv('https://raw.githubusercontent.com/jckkrr/Polling-Place-Preference-Tracker---2022-Australian-Election/refs/heads/main/party_colors.csv')['p'], pd.read_csv('https://raw.githubusercontent.com/jckkrr/Polling-Place-Preference-Tracker---2022-Australian-Election/refs/heads/main/party_colors.csv')['c']))
    for party in df_electorate['PartyAb'].unique():
        if party not in party_colors.keys():
            party_colors[party] = 'silver'
                
    legend_text = ''
    for party in party_colors.keys():
        if party in df_electorate.PartyAb.unique():
            legend_text += f'<span style="color: {party_colors[party]}">&#x25AE;</span> {party}  '
    
    
    #### Construct the plot dataframe
    
    fig = go.Figure() 

    df_plot = pd.DataFrame(columns = ['CountNum', 'PartyAb' ,'VotesAdded', 'VotesTakenFrom'])
    df_x = df_electorate.loc[(df_electorate.PPNm == chosen_pollingplace) & (df_electorate.PartyAb.isin(last_two_parties)) & (df_electorate.CalculationType.isin(['Preference Count', 'Transfer Count']))]
        
    for partyab in last_two_parties:

        for count in range(0, df_electorate.CountNum.max() + 1):
            countvotetype = 'Preference Count' if count == 0 else 'Transfer Count'
            votesadded = df_x.loc[(df_electorate.PartyAb == partyab) & (df_x.CountNum == count) & (df_x.CalculationType == countvotetype), 'CalculationValue'].values[0].astype(int)    
            votestakenfrom = partyab if count == 0 else df_electorate.loc[(df_electorate.PPNm == chosen_pollingplace) & (df_electorate.CountNum == count) & (df_electorate.CalculationType == 'Transfer Percent') & (df_electorate.CalculationValue == -100.00), 'PartyAb'].values[0]
            df_plot.loc[df_plot.shape[0]] = count, partyab, votesadded, votestakenfrom

    count_maxes = {}
    start_positions = {}
    for count in range(0, df_electorate.CountNum.max() + 1):
        m = df_plot.loc[df_plot.CountNum == count, 'VotesAdded'].max()
        count_maxes[count] = m
        if count == 0:
            start_positions[count] = 0
        if count > 0:
            start_positions[count] = count_maxes[count-1] + start_positions[count-1]


    ## Get ready to plot

    for partyab in last_two_parties:
        df_plot_party = df_plot.copy().loc[df_plot['PartyAb'] == partyab]
        df_plot_party['StartPosition'] = start_positions.values()
        df_plot_party['VotesTally'] = df_plot_party['VotesAdded'].cumsum()
        df_plot_party['color'] = df_plot_party['VotesTakenFrom'].apply(lambda x: party_colors[x])

        fig.add_trace(
            go.Bar(
                name = partyab,
                orientation='h',
                y = df_plot_party['PartyAb'],
                x = df_plot_party['VotesAdded'], 
                base = None if tiered_base is False else df_plot_party['StartPosition'],
                marker = dict(color = df_plot_party['color']),
                width = 1.2
            )
        )

    fig.update_layout(title = f'<b>{chosen_electorate} | {chosen_pollingplace.title()}</b> | Preference distribution, 2022 Australia election  <br><span style="font-size: 75%">{legend_text}</span>')
    customChartDefaultStyling.styling(fig)
    fig.update_layout(showlegend=False)
    fig.update_layout(width = 1000, height = 250)
    fig.update_layout(bargap=0.6)
    
    st.plotly_chart(fig, use_container_width=True)
    
    
    ########################################
    ########################################
    ########################################
    #### Chase chart #######################
    ########################################
    ########################################
    
    df_prefdist = pd.DataFrame()
            
    df_analysis = df_electorate.copy().loc[(df_electorate.StateAb == chosen_state) & (df_electorate.DivisionNm == chosen_electorate) & (df_electorate.PPNm == chosen_pollingplace)] 
    df_analysis['PartyAb'] = np.where(df_analysis['PartyAb'] == 'IND', 'IND' + '_' + df_analysis['Surname'].str[0:4], df_analysis['PartyAb'])
            
    parties = df_analysis['PartyAb'].unique()
    
    counts = df_analysis['CountNum'].unique()

    for count in counts:

        df_count = df_analysis.loc[(df_analysis['CountNum'] == count) & (df_analysis.CalculationType == 'Preference Count')]
        df_count = df_count.sort_values(by = 'CalculationValue', ascending = False)
                
        for party in parties:        
            cv = df_count.loc[df_count['PartyAb'] == party, 'CalculationValue'].values[0]            
            df_prefdist.loc[party, count] = cv

    df_prefdist = df_prefdist.astype(int)
    
    cols = list(df_prefdist.columns)
    cols.reverse()
    df_prefdist = df_prefdist.sort_values(by = cols, ascending = False)
   

    df_fill_colour = df_prefdist.copy()
    df_fill_colour = df_fill_colour / df_fill_colour.max()
    
    for col in df_fill_colour.columns:
        df_fill_colour[col] = df_fill_colour[col].apply(lambda x: f'rgba({x*255},25, 222, 0.2)')
        
    fig2 = go.Figure() 

    
    for party in parties:
                
        values = [x if x != 0 else None for x in df_prefdist.loc[party]]
        
        color = 'silver'
        if party in party_colors.keys():
            color = party_colors[party]
        
        fig2.add_trace(
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
                
        
    #fig2.update_layout(title = f'The chase for {chosen_electorate} ({chosen_pollingplace})')
    fig2.update_layout(title = ' ')
    customChartDefaultStyling.styling(fig2)
    fig2.update_layout(width = 1000, height = 300)
    fig2.update_xaxes(title = '<b>Counts</b>', tickangle = 0)
    fig2.update_yaxes(title = '<b>Votes</b>')
    fig2.update_layout(showlegend= False)

    st.plotly_chart(fig2, use_container_width=True)


### _________________________________________ RUN

st.markdown("**Open Investigation Tools** | [constituent.online](%s)" % 'http://www.constituent.online')
    
st.title('Polling Place Preference Tracker - 2022 Australian Election')
st.write('Because all politics is local.')


### 

chosen_pollingplace = 'ALL'

df_MAIN = pd.read_csv('https://raw.githubusercontent.com/jckkrr/Polling-Place-Preference-Tracker---2022-Australian-Election/refs/heads/main/data/2022%20Australian%20Election%20AEC%20Data%20-%20HouseDopByDivisionDownload-27966.csv', skiprows = 0, header = 1)
df_MAIN = frame_name_clean(df_MAIN)

col1, col2, col3, col4 = st.columns([1,2,3,1])
with col1: 
    states = df_MAIN['StateAb'].unique() 
    chosen_state = st.selectbox('State:', (states))
    df_state = df_MAIN.loc[df_MAIN.StateAb == chosen_state]
with col2: 
    state_electorates = df_state['DivisionNm'].unique()
    chosen_electorate = st.selectbox('Electorate:', (state_electorates))
with col3:
    electorate_pollingplaces = ['ALL']
    
    if chosen_state == 'VIC':  ### !!!!!!
        electorate_files = {chosen_electorate: f'VIC-{chosen_electorate.upper()[0:4]}'}        
    else: 
        electorate_files = {}
    
    if chosen_electorate in electorate_files.keys():

        electorate_preferences_file = f'http://constituent.online/parli/aec_data/australia/australia/2022/HouseDopByPPDownload-27966-VIC/HouseDopByPPDownload-27966-{electorate_files[chosen_electorate]}.csv'
        df_electorate = pd.read_csv(electorate_preferences_file, skiprows = 0, header = 1)
        
        electorate_pollingplaces = list(df_electorate['PPNm'].unique())
        electorate_pollingplaces.insert(0, 'ALL')
        
        chosen_pollingplace = st.selectbox('Polling Place:', (electorate_pollingplaces))
        
with col4:
    tiered_base = st.selectbox('Tiered?', ([True, False]))
        

        
twoparty_prefdist_horizontalbar_base(chosen_state, chosen_electorate, chosen_pollingplace, tiered_base)