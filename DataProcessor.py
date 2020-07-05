'''
Adapted from @nicseo code 11/20/14

Last Modified: 10/10/19

@author: cindiewu
'''

######################################################################################################
######################################################################################################
######################## PRE-PROCESSING INPUT FILE FOR VISUALIZATION ANALYSIS ########################
######################################################################################################
###################################################################################################### 


##Set up directories
#os.chdir("/home/matrix/")

import pandas as pd

def test():
    #set up
    import os
    os.chdir("/home/matrix/")
    resolution = 5.0
    holdingBayWorkbook = "OutputData/holdingBayOccupancy.csv" 
    #run
    formatDataFileForVisualization(resolution, holdingBayWorkbook)   
    
def formatDataFileForVisualization(myres, mywkbk):
    '''
    Given a reference to the csv file containing Holding Bay Occupancy data, 
    creates a structured csv file that can be loaded directly into Tableau (or other data viz software)
    Input: csv file name (ex. "HoldingBayOccupancyFirst24Hours.csv")
    Returns: csv file saved to OutputDataFileStr
    '''
    
    #Define file names
    inputDataFileStr = mywkbk #"HoldingBayOccupancyFirst24Hours.csv"
    outputDataFileStr = "OutputData/HBDataMelt.csv"

    #Read in the data
    HoldingBay_raw = pd.read_csv(inputDataFileStr)
    
    #Keep only the first 24 hours, that is columns 1 through 24*60/resolution + 1 (to include 'Day' column) +1 (to include 24:00) where resolution is size of time bucket (minutes)
    HoldingBay = HoldingBay_raw[HoldingBay_raw.columns[0:int((60*24)//myres+1+1)]] #round down to the nearest whole number
    
    #Melt the holding bay data into the format suitable for analysis in Tableau, change column names
    HB = pd.melt(HoldingBay, id_vars=['Day'], var_name='Time', value_name='Number.Bays.Occupied')
          
    #Change the labels in the time column to look nicer
    HB['Time']=HB['Time'].str.replace(':','.')

    #Output to csv file
    HB.to_csv(outputDataFileStr, index=False)
    