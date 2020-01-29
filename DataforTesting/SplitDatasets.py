### Slipt Data into multiple data parties ### 

import pandas as pd
import numpy as np
import yaml
import redacted_logging as rlog
logger = rlog.get_logger(__name__)

try:
    with open(r'input.yaml') as file:
        inputYAML = yaml.load(file, Loader=yaml.FullLoader)
    logger.info("Reading input.yaml file...")
    
except: 
    logger.error("The information in your input.yaml is not correct!")

else:
    num_of_party = inputYAML['num_of_party']
    if num_of_party < 2:
        logger.error("num_of_party has to be greater than 2")
        sys.exit("Execution interrupted!")
    elif type(num_of_party) != int:
        logger.error("num_of_party has to be an integer")
        sys.exit("Execution interrupted!")

    input_delimiter = inputYAML['delimiter']

    try:
        df = pd.read_csv(inputYAML['data_file'], sep=input_delimiter)
    except FileNotFoundError:
        logger.error("Please provide the right path to the data file.")
    
    else:
        try:
            PI = df[inputYAML['linking_feature']]
            variables = df.drop(inputYAML['linking_feature'], axis=1).columns
        except:
            logger.error("linking_feature is not in the dataset!")
        else:

            sets = int(len(variables)/num_of_party)
            for i in range(0, num_of_party):
                if i == num_of_party-1:
                    df_sub = df[variables[int(i*sets):]]
                else:
                    df_sub = df[variables[int(i*sets): int((i+1)*sets)]]
                save_df = pd.concat([PI, df_sub], axis=1, join='inner')
                save_df.to_csv('output/data_party_%d.csv' %(i+1), index=None)
            logger.info("Dataset is successfully splited and stored in output folder.")