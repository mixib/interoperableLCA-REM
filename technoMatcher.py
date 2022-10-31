# -*- coding: utf-8 -*-
"""
technoMatcher
Based on reformat_20191014, technoMatcher22 34 and 36, and bioMatcher
Created on Sun May  3 09:14:29 2020

@author: xicotencatlbm
"""

#%%Import modules
from eiVersions import cd3_1, cd3_2, cd3_3, cd3_4, cd3_5, cd3_6
from pathlib import Path
import pandas as pd

#%% Fetch the customised dictionary with manual correspondences.

sourceFile = 'processDataCMLCA.xlsx'
 
file = Path.cwd()/'data'/sourceFile

# Create general dictionary with manual correspondences from process data file.
mcd_ge = pd.read_excel(file, sheet_name='manualDict_general', 
                        header=1,
                        index_col=[0,1]).T.to_dict()

# cd3_1.update(mcd_ge)

# note that the mcd_ge doesn't output geography. Then, how does it get matched?
# maybe geography isn't useful at all. Anyway, the output excel does provide that information, so maybe don't input it but read it at the output?
# There are no codes in the output, though.

#%% Build the customised dictionary with special correspondences

#I'm here
sp = pd.read_excel(file, sheet_name='customDict',
                    header = 1,
                    index_col=[0,1,2]).T.to_dict()
    
#temp df
cf3_3 = 'ecoinvent_correspondence_file_eiv3.2_to_eiv3.3_final.xlsx'
file = Path.cwd()/'data/correspondenceFiles'/cf3_3

from eiVersions import df3_1

df3_1 = df3_1[['activityID', 'activityName', 'geography', 'product name']
              ].set_index(['activityID', 'product name']).T.to_dict()


df3_3 = pd.read_excel(file, sheet_name='cut-off', header = 2,
                   usecols = 'O,P,Q,X',
                   ).rename(columns={'activityID.1': 'activityID',
                                     'product name.1': 'product name',
                                     'activityName.1': 'activityName',
                                     'geography.1': 'geography'}
                                     ).set_index(['activityID', 'product name']).T.to_dict()
                                     
cf3_4 = 'correspondence_file_eiv3.3_to_eiv3.4_20170921_final.xlsx'
file = Path.cwd()/'data/correspondenceFiles'/cf3_4

df3_4 = pd.read_excel(file, sheet_name='cut-off', header = 2,
                   usecols = 'O,P,Q,X',
                   ).rename(columns={'activityID.1': 'activityID',
                                     'product name.1': 'product name',
                                     'activityName.1': 'activityName',
                                     'geography.1': 'geography'}
                                     ).set_index(['activityID', 'product name']).T.to_dict()

cf3_5 = 'correspondence_file_eiv3.4_to_eiv3.5_20181008.xlsx'
file = Path.cwd()/'data/correspondenceFiles'/cf3_5
df3_5 = pd.read_excel(file, sheet_name='cut-off', header = 2,
                   usecols = 'O,P,Q,X',
                   ).rename(columns={'activityID.1': 'activityID',
                                     'product name.1': 'product name',
                                     'activityName.1': 'activityName',
                                     'geography.1': 'geography'}
                                     ).set_index(['activityID', 'product name']).T.to_dict()

# cd3_1 = {}
# cd3_3 = {}

#%% Dictionary of correspondences according to database version.
version = {'2_2': 'The matching values will be deducted from the key.',
           '3_1': cd3_1,
            '3_2': cd3_2,
            '3_3': cd3_3,
            '3_4': cd3_4,
            '3_5': cd3_5,
            '3_6': cd3_6
            }

for from_database, code, subid in sp:
    if from_database == '3_2':
        df = df3_3
    if from_database == '2_2':
        df = df3_1
    if from_database == '3_3':
        df = df3_4
        
    if from_database == '3_4':
        df = df3_5
        
    entry = sp[from_database, code, subid]
    activityID = sp[from_database, code, subid]['activityID']
    productName = sp[from_database, code, subid]['product name']
    to_database = sp[from_database, code, subid]['database']

    activityName = df[activityID, productName]['activityName']
    geography = df[activityID, productName]['geography']
    
    complement = {'activityName': activityName,
                  'geography': geography}
    entry.update(complement) 
    
    version[to_database].update({(code,subid): entry})
        
    
#%% Dictionary of correspondences according to database version.
# version = {'2_2': 'The matching values will be deducted from the key.',
#            '3_1': cd3_1,
#            '3_2': cd3_2,
#            '3_3': cd3_3,
#            '3_4': cd3_4,
#            '3_5': cd3_5,
#            '3_6': cd3_6}

# #%%
def technoMatch(CMLCAstring, unit, target):
    if target not in list(version):
        print('The target ecoinvent version is invalid.')
        return None

    subkeys= ['activityID', 'product name']
    key = (CMLCAstring, unit)
    
    if target == '2_2':
        current = '2_2'
        try:
            product, geography = tuple(CMLCAstring.strip(']').rsplit('[',1))
    
            match = {'activityName': product,
                      'geography': geography,
                      'product name': product,
                      'unit': unit}
        except ValueError:
            match = None
    else:
        current = '3_1'
    
    while current != target:
        try:
            key = tuple(map(version[current][key].get, subkeys))
        except KeyError:
            pass
        i = list(version).index(current) + 1
        current = list(version)[i]
    
    if target != '2_2':
        match = version[target].get(key)
        
    return match

#%%

test = [('corrugated board, mixed fibre, single wall, at plant[RER]','kg'),
        ('transport, lorry >16t, fleet average[RER]','tkm'),
        ('corrugated board, recycling fibre, double wall, at plant[RER]','kg'),
        ('chlorine, liquid, production mix, at plant[RER]','kg'),
        ('transport, lorry 16-32t, EURO3[RER]','tkm')]

shortList = []
for v in test:
    try:
        a = technoMatch(v[0], v[1], '3_4')['activityID'], technoMatch(v[0], v[1], '3_4')['product name']
        shortList.append(a)
    except:
        pass


