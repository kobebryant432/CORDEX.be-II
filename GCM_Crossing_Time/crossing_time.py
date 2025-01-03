#Read in the crossing time file as a pandas dataframe

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

## LOAD THE CROSSING TIME DATA ##

df = pd.read_csv('GCM_Crossing_Time/input/GWL_CMIP6_20year_runningMean_1995_2014_1.5_2_3_4_exceedanceTimes.csv')

#Split the Model column into three columns (GCM, Experiment, and member), drop the original column and set the new columns as the index

df[['GCM','experiment','member']] = df['Model'].str.split('_',expand=True)
df = df.set_index(['GCM','experiment','member'])[['2','3']]

#Pivot the data so that each row is a GCM, each column is an experiment, a value in years and which threshold was crossed name the new index as threshold
df = pd.melt(df.reset_index(), id_vars=['GCM','experiment','member'], value_vars=['2','3'], var_name='threshold', value_name='crossing_time')

## LOAD THE SIMULATION STATUS DATA ##
#Select only the GCMs and SSPs that are planned to be downscaled at 4km resolution

df_selected_GCMs = pd.read_csv('Simulation_Status/input/sim_status.csv')
df_selected_GCMs = df_selected_GCMs[df_selected_GCMs['resolution'] == '4km'][['driving_GCM','experiment', 'RCM']].drop_duplicates()

#Format the experiment column to be lowercase and without special characters so that it can be merged with the crossing time dataframe
df_selected_GCMs.rename(columns={'experiment':'experiment_formatted'}, inplace=True)
df_selected_GCMs['experiment'] = df_selected_GCMs['experiment_formatted'].str.lower().replace('[^a-zA-Z0-9]', '', regex=True)

## MERGE THE DATAFRAMES ##
# Merge (inner) the two dataframes on the GCM and experiment 

df_merged = df.merge(df_selected_GCMs[['driving_GCM','experiment','experiment_formatted','RCM']], how='inner', left_on=['GCM','experiment'], right_on=['driving_GCM','experiment']).drop(columns=['driving_GCM'])

#Clean up for plotting
df_merged['Global Warming Level'] = df_merged['threshold'].apply(lambda x: f'+{x}°C GWL')
df_merged['GCM SSP'] = df_merged['GCM'] + ' ' + df_merged['experiment_formatted']
df_merged['crossing_time_start'] = df_merged['crossing_time'] - 10
df_merged['crossing_time_end'] = df_merged['crossing_time'] + 9
df_merged = df_merged.dropna(subset=['crossing_time'])
df_merged['crossing_time'] = df_merged['crossing_time'].astype(int)
df_merged = df_merged.sort_values(by=['GCM','experiment_formatted'])

## PLOT THE DATA ##

add_rcm = True

def RCM_acronyms(model_name):
    if model_name == 'ALARO1-SFX':
        return 'AL1'
    elif model_name == 'MARv3.14':
        return 'MAR'
    elif model_name == 'COSMO-CLMv6':
        return 'CSMO'

fig, ax = plt.subplots(figsize=(10,10))

for name, group in df_merged.groupby('Global Warming Level'):
    #If the threshold is 2 color the points blue, if it is 3 color them red
    if name == '+2°C GWL':
        color = 'blue'
    else:
        color = 'red'
    plt.errorbar(x=group['crossing_time'], y=group['GCM SSP'], xerr=[group['crossing_time'] - group['crossing_time_start'], group['crossing_time_end'] - group['crossing_time']], fmt='o', label=name, color=color, elinewidth=2, alpha=0.5)
    #Aggregate the groups by GCM and experiment by concatenating the RCMs into a single string containing an ACRONYM for each RCM
    group = group.groupby(['crossing_time','GCM SSP'])['RCM'].apply(lambda x: ', '.join([RCM_acronyms(RCM) for RCM in x])).reset_index()
    
    #Add text to the points with the year
    if add_rcm:
        for i, row in group.iterrows():
            #Add a symbol on top of the error bars for each RCM that is planned to be downscaled
            ax.text(x=row['crossing_time'], y=row['GCM SSP'], s=row['RCM'], ha='center', va='top', fontsize=9, color='black')

    #Aggregate the groups by GCM and experiment
    GCM_SSPs = group[['crossing_time','GCM SSP']].drop_duplicates()
    for i, row in GCM_SSPs.iterrows():
        #Make the text appear a bit higher than the error bars
        print(row['crossing_time'], row['GCM SSP'])
        ax.text(x=row['crossing_time'], y=row['GCM SSP'], s=row['crossing_time'], ha='center', va='bottom', fontsize=9, color='black')

#Manually add the RCM Acronyms to the legend as they are not directly plotted
if add_rcm:
    plt.errorbar([], [], fmt='o', label='AL1 - ALARO1-SFX', color='white')
    plt.errorbar([], [], fmt='o', label='MAR - MARv3.14', color='white')
    plt.errorbar([], [], fmt='o', label='CSMO - COSMO-CLMv6', color='white')



ax.set_xlabel('Period of each GWL')
ax.set_ylabel('GCM SSP')

#Add more space for the y-axis labels
plt.subplots_adjust(left=0.2, right=0.8)

#Add a legend
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), title='Global Warming Level')
ax.grid(True)

#Group the y-labels by GCM
plt.title("The crossing time of the +2°C and +3°C GWL for each GCM and SSP")
plt.savefig('GCM_Crossing_Time/output/crossing_time.png', bbox_inches='tight')
