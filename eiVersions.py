# -*- coding: utf-8 -*-
"""
Versions dictionary indexed by the name of intermediate exchanges in 
ecoinvent v2.2, in CMLCA format.
 
Created on Wed Aug 26 10:59:11 2020

@author: xicotencatlbm
"""

#%%
from pathlib import Path
import pandas as pd
import numpy as np

cf3_0 = 'correspondence_file_intermediate-exchangesv2.2_to_v3.0_20130904.xlsx'

ef3_1 = 'activity_overview_for_users_3.1_cut-off.xlsx'

cf3_2 = 'ecoinvent_correspondence_file_eiv3_1_to_eiv3_2_updated20151214_2.xlsx'
cf3_3 = 'ecoinvent_correspondence_file_eiv3.2_to_eiv3.3_final.xlsx'
cf3_4 = 'correspondence_file_eiv3.3_to_eiv3.4_20170921_final.xlsx'
cf3_5 = 'correspondence_file_eiv3.4_to_eiv3.5_20181008.xlsx'
cf3_6 = 'correspondence_file_eiv3.5_to_eiv3.6_2.xlsx'

columns = ['activityID', 'product name', 'activityName', 'geography', 'unit']

#%% Custom dictionary to overwrite the secondary Ni ei correspondence.
customNi = {('nickel, secondary, from electronic and electric scrap recycling'
             ', at refinery[SE]', 'kg'):
            ('nickel, 99.5%, at plant[GLO]','kg')}
    
#%% Correspondence dictionary ei v2.2 CMLCA - v3.1 bw.

file = Path.cwd()/'data/correspondenceFiles'/cf3_0
df = pd.read_excel(file).replace('(missing)', value=np.nan).dropna(
    subset=['PRODUCT NAME v2.2']).rename(
        columns= {'ACTIVITY NAME v3':'activityName',
                  'PRODUCT NAME v3':'product name',
                  'Unit':'unit',
                  'Location':'geography'})
df['CMLCAstringV2.2'] = df['PRODUCT NAME v2.2'] + '[' + df['geography'] + ']'


file = Path.cwd()/'data/correspondenceFiles'/ef3_1
df3_1 = pd.read_excel(file, sheet_name='activity overview').rename(
    columns={'activity id': 'activityID'})

# Create a correspondence dicionary indexed by the name and location in eiv2.2
# in CMLCA format, ignoring the intermediate exchanges with changes of unit or
# location.

cd3_1 = df.loc[ 
                df['Geographical area changed to:'].isna() 
              & df['Unit changed to:'].isna()
              ].merge(df3_1)[columns + ['CMLCAstringV2.2']].set_index(
              ['CMLCAstringV2.2','unit']).T.to_dict()

#%% Correspondence dictionary ei v3.1 - v3.2.
file = Path.cwd()/'data/correspondenceFiles'/cf3_2
df = pd.read_excel(file, sheet_name='cut-off', header =[1,2])

# A dataframe with 10784 direct correspondences.
mask1 = df[(10784,'direct match')]==1
direct = df.loc[mask1].set_index(
    [('eiv3.1','activityID'), ('eiv3.1', 'product name')]).xs(
        'eiv3.2', level=0, axis=1)[columns]
        
direct['Matching type'] = 'direct'
    

# A dataframe with 426 indirect correspondences recommended by ecoinvent.        
mask2 = df[(827, 'no direct mach available')]==1
mask3 = df[(767, 'replaced by how many activities')]==1
indirect = df.loc[mask2 & mask3].set_index(
    [('eiv3.1','activityID'), ('eiv3.1', 'product name')]).xs(
        'eiv3.2', level=0, axis=1)[columns]
        
indirect['Matching type'] = 'indirect'

cd3_2 = pd.concat([direct, indirect]).T.to_dict()

#%% Correspondence dictionary ei v3.2 - v3.3.
file = Path.cwd()/'data/correspondenceFiles'/cf3_3
df = pd.read_excel(file, sheet_name='cut-off', header =[1,2])

mask1 = df[(12490,'direct match')]==1
direct = df.loc[mask1].set_index(
    [('eiv3.2','activityID'), ('eiv3.2', 'product name')]).xs(
        'eiv3.3', level=0, axis=1)[columns]

direct['Matching type'] = 'direct'

mask2 = df[(780, 'no direct mach available')]==1
mask3 = df[(732, 'replaced by how many activities')]==1

indirect = df.loc[mask2 & mask3].set_index(
    [('eiv3.2','activityID'), ('eiv3.2', 'product name')]).xs(
        'eiv3.3', level=0, axis=1)[columns]

indirect['Matching type'] = 'indirect'
        
cd3_3 = pd.concat([direct, indirect]).T.to_dict()

#%% Correspondence dictionary ei v3.3 - v3.4.
file = Path.cwd()/'data/correspondenceFiles'/cf3_4
df = pd.read_excel(file, sheet_name='cut-off', header =[1,2])

mask1 = df[(13739,'direct match')]==1
direct = df.loc[mask1].set_index(
    [('eiv3.3','activityID'), ('eiv3.3', 'product name')]).xs(
        'eiv3.4', level=0, axis=1)[columns]

mask2 = df[(224, 'no direct mach available')]==1
mask3 = df[(197, 'replaced by how many activities')]==1
        
direct['Matching type'] = 'direct'

indirect = df.loc[mask2 & mask3].set_index(
    [('eiv3.3','activityID'), ('eiv3.3', 'product name')]).xs(
        'eiv3.4', level=0, axis=1)[columns]

indirect['Matching type'] = 'indirect'

cd3_4 = pd.concat([direct, indirect]).T.to_dict()

#%% Correspondence dictionary ei v3.4 - v3.5.
file = Path.cwd()/'data/correspondenceFiles'/cf3_5
df = pd.read_excel(file, sheet_name='cut-off', header =[1,2])

mask1 = df[(14333,'direct match')]==1
direct = df.loc[mask1].set_index(
    [('eiv3.4','activityID'), ('eiv3.4', 'product name')]).xs(
        'eiv3.5', level=0, axis=1)[columns]

direct['Matching type'] = 'direct'

mask2 = df[(890, 'no direct mach available')]==1
mask3 = df[(883, 'replaced by how many activities')]==1

indirect = df.loc[mask2 & mask3].set_index(
    [('eiv3.4','activityID'), ('eiv3.4', 'product name')]).xs(
        'eiv3.5', level=0, axis=1)[columns]

indirect['Matching type'] = 'indirect'

cd3_5 = pd.concat([direct, indirect]).T.to_dict()

#%% Correspondence dictionary ei v3.5 - v3.6.
# Checkcount = 15646

file = Path.cwd()/'data/correspondenceFiles'/cf3_6
df = pd.read_excel(file, sheet_name='cut-off', header =[0,1])

mask1 = df[('eiv3.6','the mapped datasets represent the same dataset')]== 1
mask2 = df[('eiv3.6','comment')].isna()

direct = df.loc[mask1 & mask2].set_index(
    [('eiv3.5','activityID'), ('eiv3.5', 'product name')]).xs(
        'eiv3.6', level=0, axis=1)[columns]

direct['Matching type'] = 'direct'

indirect = df.loc[mask1 & ~mask2].set_index(
    [('eiv3.5','activityID'), ('eiv3.5', 'product name')]).xs(
        'eiv3.6', level=0, axis=1)[columns]

indirect['Matching type'] = 'indirect'


cd3_6 = pd.concat([direct, indirect]).T.to_dict()
        
