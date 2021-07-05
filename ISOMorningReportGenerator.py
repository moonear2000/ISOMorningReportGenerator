import requests
import datetime as DT
import csv
import numpy as np
import pandas as pd
import os

# append date onto the end
requestURL = "https://www.iso-ne.com/transform/csv/morningreport?start="


def getDates(): 
    
    # this is a function that generates a list with the dates of the last 7 days

    dateToday = DT.date.today()
    timeList = []
    for i in range(7):
        
        timeList.append(str(dateToday).replace("-", ""))
        dateToday = dateToday - DT.timedelta(days=1)
        
    return timeList


def downloadFiles():
    
    
    # This function uses the api URL of the ISO Morning report archives to request the report of each of the 7 days required
    #They are placed in a dictionary based on their dates
    
    dateList = getDates()
    csvDict = {}

    for i in dateList:
        x = requests.get(requestURL+i)
        x_decoded = x.content.decode('utf-8')
        x_reader = csv.reader(x_decoded.splitlines(), delimiter=',')
        ls = []
        for row in x_reader:
            ls.append(row)
        csvDict[i] = ls

    return csvDict


def formatColumn(d):

    # This is a function that formats the downloaded csv's into a usefull format.
    
    # First, the useless values are removed from the csvs - we only need sections 3-7.
    # Then, we extract the numbers from sections 3-6.
    # Then we extract the numbers from section 7(more difficult due to downloaded format)
    # Then we create a section index which is embeded in the row labels.
    # Then we can create a dataframe with all the required data.
    # Then we add a column of row labels and a column of section labels to the dataframe.
    # Export the dataframe onto the desktop as a csv. 

    sectionIndicatorIndex = []  # This will store the section numbers
    numericalDict = {}  # This will store all the numbers from the csv's
    rows = []  # This will store the row labels:
    df = pd.DataFrame()

    # remove sections before section 3 (before index 10)
    for i in d.keys():
        d[i] = d[i][10:]

    # remove sections after section 7 (after index -20)
    for i in d.keys():
        d[i] = d[i][:-20]
        d[i].pop(1)

    counter = 3
    dList = list(d.values())[0]

    # Generate the section index list (First column is the 'Section Column')
    for i in dList:
        if 'Section' not in i[1]:
            sectionIndicatorIndex.append('')
        else:
            sectionIndicatorIndex.append(counter)
            counter += 1

    # Extract the numbers of section 3-6
    for i in d.keys():
        ls = []

        for row in d[i]:

            # Extract data from section 3-6. This is easy because no reformatting is required
            if 'Section 7' not in row[1]:
                if row[-1][-1].isdecimal():
                    ls.append(row[-1])
                else:
                    ls.append('')
            else:
                break

        numericalDict[i] = ls

    # Extract the data from section 7. More difficult because reformatting is required
    for i in d.keys():
        
        importLimit = []
        exportLimit = []
        schedualed = []

        x = False

        for row in d[i]:

            if 'Section 7' in row[1]:
                x = True

            elif x == True:
                
                if row[-1][-1].isdecimal():
                    importLimit.append(row[2])
                    exportLimit.append(row[3])
                    schedualed.append(row[3])
                    
                    
        concatenatedList = [np.nan, np.nan] + importLimit + [np.nan] + exportLimit + [np.nan] + schedualed
        numericalDict[i] = numericalDict[i] + concatenatedList

    # create a column of row labels
    counter = 3
    m = False

    for row in list(d.values())[0]:
        
        if 'Section' in row[1] and m == False:
            
            if counter == 7:
                x = row[1].replace('Section {}. '.format(counter), '')
                rows.append(x)
                m = True
                break
            
            x = row[1].replace('Section {}. '.format(counter), '')
            rows.append(x)
            counter += 1
        
        else:
            rows.append(row[1])
            
    ph = ['HighGate', 'NB', 'NYISO AC', 'NYISO CSC', 'NYISO NNC', 'Phase 2']
    rows = rows + ['Import Limit MW'] + ph + ['Export Limit MW'] + ph + ['Scheduled Contract MW'] + ph
    
    for i in range(len(rows)-len(sectionIndicatorIndex)):
        sectionIndicatorIndex += [np.nan]
    
    sectionIndicatorIndex = [np.nan] + sectionIndicatorIndex
    rows = [np.nan] + rows
    
    #Build dataframe
    df['Sections'] = sectionIndicatorIndex
    df['Rows'] = rows
    
    for i in numericalDict.keys():
        
        #Create date headers that are easy to read
        header = i[6:] + '/' + i[4:6]
        numericalDict[i] = [np.nan] + numericalDict[i]
        df[header] = numericalDict[i]
    
    return df
    

#Download Files
d = downloadFiles()

#Format the columns into the required dataframe
df = formatColumn(d)

#Save csv onto the Desktop
df.to_csv(os.path.join(os.path.join(r'C:',os.environ['HOMEPATH'],'Desktop\ISO Morning Report.csv')), index = False)










