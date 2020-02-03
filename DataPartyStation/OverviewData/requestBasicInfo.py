### Read healthcare cost data from vektis https://www.vektis.nl/intelligence/open-data ###
### Please read the data description before using the data ###
<<<<<<< HEAD
import re, yaml, ntpath
=======
import re
import yaml
>>>>>>> 570086569db26e0a46968d3436e9eba76fa6fef8
import func
import pyreadstat
import numpy as np
import pandas as pd
from collections import Counter
import redacted_logging as rlog
logger = rlog.get_logger(__name__)

try:
<<<<<<< HEAD
    with open(r'/inputVolume/request.yaml') as file:
=======
    with open(r'request.yaml') as file:
>>>>>>> 570086569db26e0a46968d3436e9eba76fa6fef8
        inputYAML = yaml.load(file, Loader=yaml.FullLoader)
        logger.info("Reading request.yaml file...")
except:
    logger.error("Your inputs in request.yaml are not correct! ")

### Read data path and delimiter from configuration file ###
file_path = inputYAML['data_file']
file_sep = inputYAML['delimiter']

### Read data (csv or sav) ###
<<<<<<< HEAD
file_name = ntpath.basename(file_path).split('.')[0]
=======
file_name = re.split('\.',file_path)[-2]
>>>>>>> 570086569db26e0a46968d3436e9eba76fa6fef8

try:
    if '.csv' in file_path:
        df =  pd.read_csv(file_path, sep=file_sep)
    elif '.sav' in file_path:
        df, meta = pyreadstat.read_sav(file_path)
except FileNotFoundError:
        logger.error("The data file does not exist!")
except: 
    logger.error("Errors occur when reading the data file!")

else:
    ### Select features you are interested in ###
    try:
        selected_features = inputYAML['selected_features']
        excluded_features = inputYAML['excluded_features']
        if selected_features == "ALL":
            if excluded_features == False: 
                col = df.columns
            else:
                col = df.drop(excluded_features, axis=1).columns
        else:
            col = selected_features

    except:
        logger.error("Some of your selected_features and excluded_features are not in the dataset")
    
    else:
        ### Check missing values in the dataset ###
        if inputYAML['check_missing'] == True:
            func.check_missing(df, col, file_name)

        ### Get the basic description about the dataset ###
        if inputYAML['data_description'] == True:
            func.data_describe(df, col, file_name)

        ### Function for correlation matrix ###
        if inputYAML['correlation_matrix'] == True:
            func.corr_Matrix(df[col], file_name)

        ### Separate features to numerical and categorical ###
        numFea = []
        catFea = []
        for c in col:
            if len(Counter(df[c].dropna())) > 20:
                numFea.append(c)
            else:
                catFea.append(c)

        ### Function for distribution plot ###
<<<<<<< HEAD

=======
>>>>>>> 570086569db26e0a46968d3436e9eba76fa6fef8
        if inputYAML['distribution_plot'] == True:
            if inputYAML['distribution_feature'] == 'ALL':
                for f in numFea:
                    try:
                        func.dist_Plot(df[numFea], f, file_name)
                    except:
                        if f not in catFea:
                            logger.error(f, " -- Data type does not support numerical distribution plot")

                for f in catFea:
                    try:
                        func.cate_Dist(df[catFea], f, file_name)
                    except:
                        if f not in numFea:
                            logger.error(f, " -- Data type does not support categorical distribution plot")

            else:
                for f in inputYAML['distribution_feature']:
                    if f in numFea:
                        try:
                            func.dist_Plot(df[numFea], f, file_name)
                        except:
                            logger.error(f, " -- Data type does not support numerical distribution plot")

                    elif f in catFea:
                        try:
                            func.cate_Dist(df[catFea], f, file_name)
                        except:
                            logger.error(f, " -- Data type does not support categorical distribution plot")

        ### Function for Cat-Num plot ###
        if inputYAML["Cat_Num_plot"] == True and inputYAML["Cat_Num_feature"] != False :
            print(inputYAML['Cat_Num_feature'])
            for f in inputYAML['Cat_Num_feature']:
                func.plot_catNum(df,f,file_name, catFea)


        ### Function for Box plot ###
        if inputYAML["Box_plot"] == True and inputYAML["Box_plot_feature"] != False :
            for f in inputYAML['Box_plot_feature']:
                func.box_Plot(df,f,file_name, catFea)


        ### Function for Num-Num plot ###
        if inputYAML["Num_Num_Plot"] == True and inputYAML["Num_Num_feature"] != False :
            for f in inputYAML['Num_Num_feature']:
                func.plot_numNum(df,f,file_name, catFea)