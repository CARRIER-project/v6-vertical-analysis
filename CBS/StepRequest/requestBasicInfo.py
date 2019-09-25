### Read healthcare cost data from vektis https://www.vektis.nl/intelligence/open-data ###
### Please read the data description before using the data ###

import json
import func
import numpy as np
import pandas as pd

with open('request.json', 'r') as f:
    input = json.load(f)

file = input['data_file']
year = file[6:-4]
df = pd.read_csv(file) #### delimiter! ####

### Select features you are interested in ###
### Feature descriptions are provided by https://www.vektis.nl/intelligence/open-data ###
# KOSTEN_MEDISCH_SPECIALISTISCHE_ZORG
col_input = input['selected_features']
year_input = input['year']
col = ['GESLACHT', 'AANTAL_BSN']
for c in col_input:
    col.append(c+'_'+year_input)


### As some features are available in some years, we need to check before select certain features ###
data_col = list(df.columns)
present = []
for c in col:
    if c in data_col:
        present.append(col.index(c))
        
df_vektis = df[np.array(col)[present]]


### Give new columns names which are understandable for yourself ###
# medical_specialist
name_col = ['SEX','BSNs']
for i in input['name_features']:
    name_col.append(i)
new_col = np.array(name_col)[present]
df_vektis.columns = new_col

### Change the types (int,float,str --> float) of values in the AGE column ###
age = []
for i in df['LEEFTIJDSKLASSE']:
    if type(i) == str:
        try:
            age.append(float(i))
        except:
            age.append(float(i[:-1]))
    elif type(i) == float:
        age.append(i)
    elif type(i) == int:
        age.append(i)

### Add new age column ###
df_vektis['AGE'] = age

### For getting some basic info ###
if input['check_missing'] == 'true':
    func.check_missing(df, col, year)
if input['data_description'] == 'true':
    func.data_describe(df, col, year)

### For three plots ###
loop = input['age_range']
for i in loop:
    df_avg = func.groupAgeRange(df_vektis, i, 0)

    if input['correlation_matrix'] == True:
        func.corr_Matrix(df_avg, i, year)

    if input['pie_chart'] == True:
        func.pie_Chart(df_avg, i, year)

    if input['distribution_plot'] == True:
        func.dist_Plot(df_avg,'SUM', i, year)

### Only for the Stack plot ###
if input['stacked_area'] == True:
    loop = list(range(0,90,1))
    df_stack = pd.DataFrame()
    for i in loop:
        df_avg = func.groupAgeRange(df_vektis, i, df_stack)
        df_stack[i] = df_avg.mean(axis=0, skipna=True)
        df_stack_trans = df_stack.transpose()
        df_stack_trans = func.merge(df_stack_trans)
        func.stacked_Plot(df_stack_trans, year)
    print('Stacked Area plot is done')

