import time, json
start_time = time.time()
import pandas as pd

def checking(df, PI):
    standardName = ['GBAGeboorteJaar', 'GBAGeboorteMaand', 'GBAGeboorteDag',
                    'GBAGeslacht', 'GBAPostcode', 'GBAHuisnummer', 'GBAToev']
    for var in standardName:
        if var in PI:
            if df[var].isnull().sum() > 0:
                print("%s has missing values. Linking features cannot have missing values" %var)
                
            if var == "GBAGeboorteJaar":
                df[var] = df[var].astype(str)
                for i in range(0, len(df)):
                    value = df.iloc[i][var]
                    if type(value) != str:
                        print("%s type has to be string" %var)
                        if len(value) != 4:
                            print("%s length has to be 4" %var)
                print("%s checking is done" %var)
                            
                
            if var == "GBAGeboorteMaand":
                df[var] = df[var].astype(str)
                for i in range(0, len(df)):
                    value = df.iloc[i][var]
                    if type(value) != str:
                        print("%s type has to be string" %var)
                        if len(value) != 4:
                            print("%s length has to be 2" %var)
                print("%s checking is done" %var)
                            
                
            if var == "GBAGeboorteDag":
                df[var] = df[var].astype(str)
                for i in range(0, len(df)):
                    value = df.iloc[i][var]
                    if type(value) != str:
                        print("%s type has to be string" %var)
                        if len(value) != 4:
                            print("%s length has to be 2" %var)
                print("%s checking is done" %var)
            
                            
            if var == "GBAGeslacht":
                df[var] = df[var].astype(str)
                for i in range(0, len(df)):
                    value = df.iloc[i][var]
                    if type(value) != str:
                        print("%s type has to be string" %var)
                        if value != 1 or value != 2:
                            print("%s has to be 1 or 2" %var)
                print("%s checking is done" %var)
            
                            
            if var == "GBAPostcode":
                df[var] = df[var].astype(str)
                for i in range(0, len(df)):
                    value = df.iloc[i][var]
                    if type(value) != str:
                        print("%s type has to be string" %var)
                        if len(value) != 4:
                            print("%s length has to be 6" %var)
                print("%s checking is done" %var)
            
                            
            if var == "GBAHuisnummer":
                df[var] = df[var].astype(str)
                for i in range(0, len(df)):
                    value = df.iloc[i][var]
                    if type(value) != str:
                        print("%s type has to be string" %var)
                        if len(value) < 5:
                            print("%s length has to be less 5" %var)
                print("%s checking is done" %var)
            
                            
            if var == "GBAToev":
                df[var] = df[var].astype(str)
                for i in range(0, len(df)):
                    value = df.iloc[i][var]
                    if type(value) != str:
                        print("%s type has to be string" %var)
                        if len(value) < 7:
                            print("%s length has to be less 7" %var)
                print("%s checking is done" %var)
            
                
        else:
            print('Sorry, %s is not in the dataset.' %var)