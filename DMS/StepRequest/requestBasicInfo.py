### Read healthcare cost data from vektis https://www.vektis.nl/intelligence/open-data ###
### Please read the data description before using the data ###

import json
import func
import pyreadstat
import numpy as np
import pandas as pd
from collections import Counter

with open('request.json', 'r') as f:
    input = json.load(f)

file_path = input['data_file']
file = file_path[:-4]
print(file_path)
if '.csv' in file_path:
    df =  pd.read_csv(file_path, delimiter=';')
elif '.sav' in file_path:
    df, meta = pyreadstat.read_sav(file_path)

### Select features you are interested in ###
if input['selected_features'] == "ALL":
    col = df.columns
else:
    col = input['selected_features']

### For getting some basic info ###
if input['check_missing'] == True:
    func.check_missing(df, col, file)
if input['data_description'] == True:
    func.data_describe(df, col, file)

### Function for correlation matrix ###
if input['correlation_matrix'] == True:
    func.corr_Matrix(df[col], file)

### Separate features to numerical and categorical ###
numFea = []
catFea = []
for c in col:
    if len(Counter(df[c].dropna())) > 10:
        numFea.append(c)
    else:
        catFea.append(c)

### Function for distribution plot ###
if input['distribution_plot'] == True:
    if input['distribution_feature'] == 'ALL':
        for f in numFea:
            try:
                func.dist_Plot(df[numFea], f, file)
            except:
                if f not in catFea:
                    print(f, " -- Data type does not support numerical distribution plot")

        for f in catFea:
            try:
                func.cate_Dist(df[catFea], f, file)
            except:
                if f not in numFea:
                    print(f, " -- Data type does not support categorical distribution plot")

    else:
        for f in input['distribution_feature']:
            if f in numFea:
                try:
                    func.dist_Plot(df[numFea], f, file)
                except:
                    print(f, " -- Data type does not support numerical distribution plot")

            elif f in catFea:
                try:
                    func.cate_Dist(df[catFea], f, file)
                except:
                    print(f, " -- Data type does not support categorical distribution plot")

### Function for Cat-Num plot ###
if input["Cat_Num_plot"] == True and len(input["Cat_Num_feature"]) > 0:
    for f in input['Cat_Num_feature']:
        func.plot_catNum(df,f,file)

### Function for Box plot ###
if input["Box_plot"] == True and len(input["Box_plot_feature"]) > 0:
    for f in input['Box_plot_feature']:
        func.box_Plot(df,f,file)


### Function for Num-Num plot ###
if input["Num_Num_Plot"] == True and len(input["Num_Num_feature"]) > 0:
    for f in input['Num_Num_feature']:
        func.plot_numNum(df,f,file)