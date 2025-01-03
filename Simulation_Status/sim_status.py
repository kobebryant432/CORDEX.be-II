#Read in the simulation status file as a pandas dataframe
import pandas as pd
from itables import to_html_datatable

df = pd.read_csv('Simulation_Status/input/sim_status.csv')

#Split the table int two tables one per resolution
df['experiment_formatted'] = df.apply(lambda x: '<span style="color: green">%s</span>' % x['experiment'] if x['status'] == 'complete' else '<span style="color: orange">%s</span>' % x['experiment'] if x['status'] == 'running' else '<span style="color: blue">%s</span>' % x['experiment'], axis=1)
#Underline the experiment name if eu_cordex is True
df['experiment_formatted'] = df.apply(lambda x: '<u>%s</u>' % x['experiment_formatted'] if x['eu_cordex'] == True else '%s' % x['experiment_formatted'], axis=1)

df_1 = df[df['resolution'] == '12km']
df_2 = df[df['resolution'] == '4km']

def concat_experiments(x):
    return "%s" % ', '.join(x.unique())

for res,df in zip(["12km","4km"],[df_1, df_2]):
    df_mat = df.sort_values(by=['experiment']).pivot_table(index=['driving_GCM'], columns='RCM', values='experiment_formatted', aggfunc=concat_experiments)
    df_mat = df_mat.reindex(sorted(df_mat.columns), axis=1).fillna('')

    #Create a

    with open(f'Simulation_Status/output/sim_status_{res}.html', 'w') as f:
        f.write(to_html_datatable(df_mat, dom="t", classes="display"))

#Create an html list of the status colors

with open('Simulation_Status/output/sim_status_legend.html', 'w') as f:
    f.write('<ul>')
    f.write('<li><span style="color: green">complete</span></li>')
    f.write('<li><span style="color: orange">running</span></li>')
    f.write('<li><span style="color: blue">planned</span></li>')
    f.write('</ul>')