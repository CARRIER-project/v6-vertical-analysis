#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script is to match the mulitple datasets from all data parties.
This will happen after verification-decryption-verification and before
the actually analysis. 
"""

import time
start_time = time.time()

import yaml, sys
import pandas as pd
import numpy as np
import redacted_logging as rlog
logger = rlog.get_logger(__name__)


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


def matching_process(dataset_list): 
    """match multiple datasets from all data parties

    Args:
        dataset_list (list): a list of dataframes of all data parties.

    Returns:
        combined_df (Pandas.DataFrame): matched dataset
        exact_match (list): the index list of exact matched records
    """

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
            logger.info('Matching result - Exact {exNum}'.format(exNum=len(exact_match)))
            logger.info('Matching result - Multi {mulNum}'.format(mulNum=len(multi_match)))
            logger.info('Matching result - None {noNum}'.format(noNum=len(no_match)))
            logger.debug("Multi-matching array: {array} ".format(array=str(multi_match_number)))

            # Link and combine actual data with hashed personal identifiers #
            combined_df = pd.concat([combined_df.loc[exact_match], dataset_list[order[item]].loc[exact_match]], axis=1, join='inner')
    return combined_df, exact_match



def main():
    """main function

    The main function will load all decrypted datasets, find the exact matched records, 
    combined matched records to a new data file. 
    If the number of exact matched records is less than 100, execution will be interrupted
    to protect individual's privacy.
    """

    logger = rlog.get_logger(__name__)
    input_yaml_file_name = r'/inputVolume/security_input.yaml'
    inputYAML = load_yaml_file(input_yaml_file_name, logger)

    parties = inputYAML['parties']

    # Read all encrypted datasets into a list #
    try:
        dataset_list = []
        for index in range(0, len(parties)): 
            data_frame_eachParty = pd.read_csv('/data/encrypted_%s.csv' %(parties[index])).set_index('encString')
            dataset_list.append(data_frame_eachParty)

            logger.info('{dataparty} has {datasize} rows'.format(dataparty=parties[index], datasize=len(dataset_list[index]))) 
    except FileNotFoundError:
        logger.error("Failed to read decrypted data files. This might be because your keys are incorrect. ")

    # Matching process
    combined_df, exact_match = matching_process(dataset_list)

    # Execution will be continued when exact matching number is larget than 100 and 
    if len(exact_match) > 0:
        # Restrict analysis if exact match is less than 100 #
        if len(exact_match) < 100:
            logger.warning("The number of exact-matched instances is less than 100!!")
            sys.exit("Due to priavcy concerns, execution is interrupted here. Please provide datasets which have more common instances!")
        else:
            cmb_col = list(combined_df.columns)
            with open('/output/CombinedFeatures.txt', 'w') as f:
                for item in cmb_col:
                    f.write("%s\n" % item)

            # Save file #
            combined_df.to_csv('/data/act_data.csv')
            logger.debug('Features in combined dataset are saved locally')
            logger.info("Matching and linking took {runtime:.4f}s to run.".format(runtime=(time.time() - start_time)))
        
    else:
        logger.error('No records have been exactly matched so that no combined dataset is generated!!')

if __name__ == "__main__":
    main()