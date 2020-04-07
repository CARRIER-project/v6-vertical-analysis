#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script is to read the data file, extract the linking features as indicated in the encrypt_input.yaml,
hash+salt on the linking features. Then a new file with pseudonymized linking features and actual data is saved 
in the Docker container. The new file will be used for encrypt.py. 

"""

import time, sys, yaml
start_time = time.time()
import pyreadstat
import pandas as pd
import check_format
import PQencryption as cr
import redacted_logging as rlog



def load_yaml_file(file_name, logger):
    """loads a yaml file, logs to logger if errors occur

    Args:
        file_name (str): File name of the YAML file to be loaded.
        logger (logging.Logger): Logger class handling log messages.

    Raises:
        FileNotFoundError: If the yaml file can not be found.

    Returns:
        dict: yaml file content as a dictionary.
    """
    try:
        with open(file_name) as file:
            inputYAML = yaml.load(file, Loader=yaml.FullLoader)
            logger.debug("Reading encrypt_input.yaml file...")
    except yaml.parser.ParserError:
        logger.error(f"File {file} is not valid YAML.")
        raise
    except FileNotFoundError:
        logger.error(f"Trying to read file '{file}', but it does not exist.")
        raise

    return inputYAML


def get_data_from_file(file_path, file_sep, logger):
    """Read data from a '.csv' file, or load it from a '.sav' file.

    Args:
        file_path (str): Path of the data file.
        file_sep (str): Separator for the '.csv' file.
        logger (logging.Logger): Logger class handling log messages.

    Raises:
        FileNotFoundError: If the data file can not be found.

    Returns:
        pandas.core.frame.DataFrame: Data in a data frame.
    """
    try:
        if '.csv' in file_path:
            data_frame = pd.read_csv(file_path, sep=file_sep)
        elif '.sav' in file_path:
            data_frame, _ = pyreadstat.read_sav(file_path)
    except FileNotFoundError:
        logger.error("The data file does not exist!")
        raise

    return data_frame


def making_salt (salt_text):
    """ Read the salt from yaml file and adapt it for hashing function.

    Args:
        salt_text (str): salt string.

    Returns:
        salt for hashing function (128 bytes)
    """
    # Salt must be 128 bytes in hex.
    ### 18-08-2019 ###
    salt_missing = 128 - len(salt_text)
    if salt_missing > 0:
        salt_text = salt_text + ("a" * salt_missing)
    if salt_missing < 0:
        salt_text = salt_text[:salt_missing]
    salt = salt_text #.encode('UTF-8')

    return salt


def main():

    """main function

    The main function will extract linking features, combine multiple values into one string, and salt hash the string. 
    Then, hashed linking features combining with actual data will be written into a data file stored in the Docker container.
    """
    logger = rlog.get_logger(__name__)
    input_yaml_file_name = r'/inputVolume/encrypt_input.yaml'
    inputYAML = load_yaml_file(input_yaml_file_name, logger)

    # Read all values from yaml file #
    try: 
        file_path = inputYAML['data_file']
        file_sep = inputYAML['delimiter']
        salt_text = inputYAML['salt_text']
        party_name = inputYAML['party_name']
        linking_features = inputYAML['linking_features'] 
        check_format = inputYAML['check_format']
    except KeyError:
        logger.error("YAML file not valid. Please consult the example " +
                     "'encrypt_input.yaml' file and edit in your settings.")

    # Read data file #
    data_frame = get_data_from_file(file_path, file_sep, logger)
    
    # Drop original linking features from orignal data (=linking features + acutal data) #
    try: 
        act_data = data_frame.drop(linking_features, axis=1)
    except KeyError:
        logger.warning(f"One or more linking features you provided are'{linking_features}' not" +
                        "found in the data.")


    ### Check formats of linking features###
    if check_format:
        checkFormat.checking(data_frame, linking_features)
    else:
        logger.warning("You did not check format of linking features which might cause mis-matchings!")

    # convert inputed salt string to salt for hashing function #
    salt = making_salt (salt_text)

    ### salt hash linking features###
    hashed_linking_features = []
    if data_frame[linking_features].isnull().sum().sum() == 0:
        for i in range(0, len(data_frame)):
            combine_linking_features = str()
            ### combine multiple linking features to one string ###
            for j in range(0, len(linking_features)):
                id_feature =  data_frame.iloc[i][linking_features[j]]
                combine_linking_features = combine_linking_features + str(id_feature)

            try:   
                ### Remove space from strings ###
                combine_linking_features =  combine_linking_features.replace(' ', '')
                ### salthash the combined linking features ###
                hashed = cr.salthash(salt, combine_linking_features) #.encode('UTF-8')
                hashed_linking_features.append(hashed)
            except:
                logger.error("Failed to pseudonymize and encrypt the data file.")
                raise

    else:
        logger.error("Work cannot be done because missing values are in personal identifiers!")
        logger.info(data_frame.isnull().sum())
        sys.exit("Execution interrupted!")
    
    ### Combing hased linking features with acutally data ###
    hashed_linking_features_df = pd.DataFrame(hashed_linking_features, columns=['encString'])
    hashedData_df = pd.concat([hashed_linking_features_df, act_data], axis=1, join='inner')
    logger.info("Pseudonymized data has %s rows" %str(len(hashedData_df)))

    ### Write the new data file out ###
    hashedData_df.to_csv("/data/encrypted_%s.csv" %(party_name), index=None, sep=',', encoding='utf-8') #2.4 Output file name

    logger.info("My program took {runtime:.4f}s to run".format(runtime=time.time() - start_time)) 

if __name__ == "__main__":
    main()