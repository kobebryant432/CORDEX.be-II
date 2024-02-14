#Read in the crossing time file as a pandas dataframe

import pandas as pd
from itables import to_html_datatable
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
df_selected_GCMs = df_selected_GCMs[df_selected_GCMs['resolution'] == '4km'][['driving_GCM','experiment']].drop_duplicates()

#Format the experiment column to be lowercase and without special characters so that it can be merged with the crossing time dataframe
df_selected_GCMs.rename(columns={'experiment':'experiment_formatted'}, inplace=True)
df_selected_GCMs['experiment'] = df_selected_GCMs['experiment_formatted'].str.lower().replace('[^a-zA-Z0-9]', '', regex=True)

## MERGE THE DATAFRAMES ##
# Merge (inner) the two dataframes on the GCM and experiment 

df_merged = df.merge(df_selected_GCMs[['driving_GCM','experiment','experiment_formatted']], how='inner', left_on=['GCM','experiment'], right_on=['driving_GCM','experiment']).drop(columns=['driving_GCM'])

#Clean up for plotting
df_merged['Global Warming Level'] = df_merged['threshold'].apply(lambda x: f'+{x}°C GWL')
df_merged['GCM SSP'] = df_merged['GCM'] + ' ' + df_merged['experiment_formatted']
df_merged['crossing_time_start'] = df_merged['crossing_time'] - 10
df_merged['crossing_time_end'] = df_merged['crossing_time'] + 9
df_merged = df_merged.dropna(subset=['crossing_time'])
df_merged['crossing_time'] = df_merged['crossing_time'].astype(int)
df_merged = df_merged.sort_values(by=['GCM','experiment_formatted'])

## PLOT THE DATA ##

fig, ax = plt.subplots(figsize=(10,10))

for name, group in df_merged.groupby('Global Warming Level'):
    #If the threshold is 2 color the points blue, if it is 3 color them red
    if name == '+2°C GWL':
        color = 'blue'
    else:
        color = 'red'
    plt.errorbar(x=group['crossing_time'], y=group['GCM SSP'], xerr=[group['crossing_time'] - group['crossing_time_start'], group['crossing_time_end'] - group['crossing_time']], fmt='o', label=name, color=color, elinewidth=2)
    #Add text to the points with the year
    for i, row in group.iterrows():
        #Move the text more upwards 
        ax.text(x=row['crossing_time'], y=row['GCM SSP'], s=row['crossing_time'], ha='center', va='bottom', fontsize=8)

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
