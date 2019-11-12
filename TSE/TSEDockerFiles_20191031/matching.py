import time
start_time = time.time()

import json
import pandas as pd
import numpy as np

#read input file
with open('security_input.json') as data_file:    
    inputJson = json.load(data_file)
parties = inputJson['parties']

# Read all encrypted datasets into a list #
smallest = 0
dataset_list = []
for p in parties: 
    df_eachParty = pd.read_csv('/data/encrypted_%s.csv' %(p)).set_index('encString')
    dataset_list.append(df_eachParty)

# Order the size of datasets from small to large #
sizes = []
for dataset in dataset_list:
    sizes.append(len(dataset))
order = np.argsort(sizes)

# Find match records #

for item in range(0, len(order)): 
    multi_match = []
    multi_match_number = []
    exact_match = []
    no_match = []

    if item == 0:
        combined_df = dataset_list[order[item]]
    else:
        for i in combined_df.index:
            try:
                pair = dataset_list[order[item]].loc[i]
                if type(pair) == pd.DataFrame:
                    multi_match.append(i)
                    multi_match_number.append(len(pair))
                elif type(pair) == pd.Series:
                    exact_match.append(i)
            except:
                no_match.append(i)

        # Report matches #
        print('************************************************')
        print('*** Match result between %s and %s ***' %(parties[item-1], parties[item]))
        print('************************************************')
        with open('/output/printOut.txt', 'w') as f:
                f.write("Exact match: %s \n Multiple matchs: %s \n No matches: %s" %(str(len(exact_match)), str(len(multi_match)),str(len(no_match))))

        print('Exact match: %s \n Multiple matchs: %s \n No matches: %s' \
                %(str(len(exact_match)), str(len(multi_match)),str(len(no_match))))

        with open('/output/printOut.txt', 'a') as f:
            f.write("Multi match number array: %s "%(str(multi_match_number)))
        print("Multi match number array: %s "%(str(multi_match_number)))

        # Link and combine actual data with person identifiers #
        combined_df = pd.concat([combined_df.loc[exact_match], dataset_list[order[item]].loc[exact_match]], axis=1, join='inner')


print('************************************************')
print('Features in combined dataset')
cmb_col = list(combined_df.columns)
with open('/output/CombinedFeatures.txt', 'w') as f:
    for item in cmb_col:
        f.write("%s\n" % item)
        print("%s" % item)
print('************************************************')

# Save file #
combined_df.to_csv('/data/act_data.csv')
print("Matching and linking took", time.time() - start_time, "to run")