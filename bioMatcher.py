# -*- coding: utf-8 -*-
"""
biomatcher
Automating the matching of biosphere flows between ecoinvent v2.2 and v3.x were x<7.
(Auxiliary to the generation of bw input from CMLCA and to the comparison of
life cycle inventories)

Created on Tue Mar  3 14:37:05 2020

@author: xicotencatlbm
"""
#%% Import modules

import os # Line 22
import pandas as pd # Line 22
import numpy as np

#%% Import ecoinvent's matching file and create a 2.2 - 3.x dictionary
# with automatic matches

# From the ei file with all the biosphere correspondances:
PATH = os.getcwd()
FILE = r'data\correspondenceFiles\correspondence_file_elementary-exchanges_v2.2-v3.0_20130904.xls'

df = pd.read_excel(os.path.join(PATH, FILE)).dropna(
    subset=['Elementary Flow Name v3'])

# From the CMLCA implementation of ei22:
# FILE = 'CMLCA22_bare.txt'

# Or from the project implementation of ei22 and additional processing.
FILE = r'data\correspondenceFiles\CMLCA22_REM.txt'
cmlca22 = pd.read_csv(FILE, sep = '\t')

# Strip units from tag.
cmlca22['Unit'] = cmlca22['Unit'].str.split(pat = '] ', expand = True)[1]

#%% Functions used in this script.

def CMLCA22s (df):
    '''Deduct the CMLCA ei22 string for environmental flows in ei22.'''
    return (df['Elementary Name v2.2']
            + '['
            + df['Category v2.2']
            + '_'
            + df['SubCategory v2.2']
            + ']')

def stringer (string22):
    '''Get the harmonized string corresponding to a CMLCA ei22 string.'''
    try:
        return biomatcher.get(string22).get('CMLCAstring')
    except AttributeError:
        pass

def main_uuid(CMLCAstring, Unit):
    '''Get the UUID characterized by an harmonized string and a unit. '''
    return uuidDict.get((CMLCAstring, Unit))

def slice_to_iterate():
    '''Identify which CMLCA ei22 flows haven't been matched to ei3.x'''
    return cmlca22[~cmlca22['CMLCAstring'].isin(CMLCAstring34)][['Full name',
                                                              'Unit']]
def generalize(target):
    '''Remove a level of detail and substitute rail with road (to match with
    the flow containing rail/road).
    '''
    keywords = ['forest, intensive', 'industrial area']
    for term in keywords:
        if term in target:
            prefix = target.split(term)[0]
            sufix = target.split('[')[1]
            return prefix+term+'['+sufix
        elif 'rail' in target:
            return target.replace('rail', 'road')

#%% Functions imported by other scripts.

# To debug: should also consider unit, otherwise there might be duplicates.
def uuid (string22):
    '''Get the UUID corresponding to a CMLCA ei22 string.'''
    try:
        return biomatcher.get(string22).get('UUID')
    except AttributeError:
        pass

#%% List with the subkeys of the biomatcher dictionary.

dictKeys = ['Full name', 'CMLCAstring', 'Matching type', 'Unit', 'UUID']

#%% First iteration of the dictionary; uses the ei correspondence data and
# tags the matching type of the existing correspondences as automatic.

# Deduct CMLCAstring for flows with unspecified subcompartment.
df.loc[(df['Subcompartment v3'] == 'unspecified'),'CMLCAstring'] = (
    df['Elementary Flow Name v3']
    + '[(\''
    + df['Compartment v3']
    + '\',)]')

# Deduct CMLCAstring for flows with specified compartment.
df.loc[(df['Subcompartment v3'] != 'unspecified'),'CMLCAstring'] = (
    df['Elementary Flow Name v3']
    + '[(\''
    + df['Compartment v3']
    + '\', \''
    + df['Subcompartment v3']
    +'\')]')

# Create a dictionary matching the CMLCAstring to the corresponding UUID.

# 3847 unique uuid's. Ther are 11 duplicates of CMLCAstring differing by unit.
uuidDict= df[['CMLCAstring', 'Unit', 'UUID Elementary Flow v3']].dropna(
    ).set_index(['CMLCAstring','Unit']).to_dict()['UUID Elementary Flow v3']

# Deduct CMLCA22 string
df['CMLCA22'] = CMLCA22s(df)

# Drop all the lines with empty CMLCA22.
df.dropna(subset=['CMLCA22'], inplace= True)

df['Matching type'] = 'automatic'

# First iteration
biomatcher = df[['CMLCA22', 'CMLCAstring', 'Matching type',
                 'UUID Elementary Flow v3', 'Unit']].rename(
                     columns={'UUID Elementary Flow v3':'UUID'}).set_index(
                         'CMLCA22').T.to_dict('dict')

cmlca22['CMLCAstring'] = np.vectorize(stringer)(cmlca22['Full name'])

#%% Iteration check

# There are 3615 environmental flows listed by ecoinvent in the version 3.X.
CMLCAstring34 = df['CMLCAstring'].tolist()

df_sa = slice_to_iterate()

#%% Second iteration

# Algorithm specific to the project file, which contains more environmental
# flows than the bare ei22 CMLCA implementation.

df_sa.loc[(df_sa['Full name'].str.contains(
    '[air]', regex=False)),'Search'] = df_sa['Full name'].str.replace(
        'air', 'air_unspecified')

df_sa['CMLCAstring'] = np.vectorize(stringer)(df_sa['Search'])
df_sa.dropna(subset=['CMLCAstring'], inplace=True)
df_sa['Matching type'] = 'semiautomatic'

df_sa['UUID'] = np.vectorize(main_uuid)(df_sa['CMLCAstring'], df_sa['Unit'])

# Dictionary specific to the project file.
sa = df_sa[dictKeys].set_index('Full name').T.to_dict('dict')

# Update dictionary.
biomatcher.update(sa)

# Iterate
cmlca22['CMLCAstring'] = np.vectorize(stringer)(cmlca22['Full name'])

# Iteration check

# Input slice for the third iteration, containing 587 unmatched elements.
df_aw = slice_to_iterate()

#%% Third iteration

water = [('water_fossil-', '(\'water\', \'ground-\')'),
         ('water_lake', '(\'water\', \'surface water\')'),
         ('water_river','(\'water\', \'surface water\')'),
         ('water_river, long-term', '(\'water\', \'surface water\')')]

for old, new in water:
    df_aw.loc[(df_aw['Full name'].str.contains(old, regex=False)),
              'CMLCAstring'] = df_aw['Full name'].str.replace(old, new)

df_aw.dropna(subset=['CMLCAstring'], inplace=True)

# Check if all the deduced CMLCAstrings for the ei3.4 version exist.
aw_check = df_aw.loc[df_aw['CMLCAstring'].isin(CMLCAstring34)]

df_aw['Matching type'] = 'water compartments by C. Mutel'

df_aw['UUID'] = np.vectorize(main_uuid)(df_aw['CMLCAstring'], df_aw['Unit'])

aw = df_aw[dictKeys].set_index('Full name').T.to_dict('dict')

biomatcher.update(aw)

# Iterate
cmlca22['CMLCAstring'] = np.vectorize(stringer)(cmlca22['Full name'])

# Input slice for the fourth iteration, containing 30 unmatched elements.
df_mutel = slice_to_iterate()

#%%Fourth iteration

df_mutel['Matching type'] = 'Manual by Mutel'

# Remove a level of detail and substitute rail with road (to match with the
# flow containing rail/road).

df_mutel['Search'] = np.vectorize(generalize)(df_mutel['Full name'])
df_mutel['CMLCAstring'] = np.vectorize(stringer)(df_mutel['Search'])

df_mutel['UUID'] = np.vectorize(main_uuid)(df_mutel['CMLCAstring'],
                                           df_mutel['Unit'])

mutel = df_mutel[dictKeys].dropna().set_index('Full name').T.to_dict('dict')

biomatcher.update(mutel)

# Iterate
cmlca22['CMLCAstring'] = np.vectorize(stringer)(cmlca22['Full name'])

# Input slice for the fifth iteration, containing 9 unmatched elements.

df_manual = slice_to_iterate()

#%% Fifth iteration

df_manual['Matching type'] = 'Manual by BMX'

manual = [('Carbon dioxide\[air\]',
           'Carbon dioxide, fossil[air_unspecified]'),
          ('Carbon monoxide\[air\]',
           'Carbon monoxide, fossil[air_unspecified]'),
         ('2,3,7,8-tetrachlorodibenzo-p-dioxin\[air\]',
           ('Dioxins, measured as 2,3,7,8-tetrachlorodibenzo-p-dioxin'
            '[air_unspecified]')),
          ('Particulates\[air\]',
           'Particulates, > 2.5 um, and < 10um[air_unspecified]'),
          ('Water\[resources\]',
           'Water, unspecified natural origin[resource_in water]')
         ]

for old, new in manual:
    df_manual.loc[(df_manual['Full name'].str.contains(old, regex=True)),
              'Search'] = df_manual['Full name'].str.replace(old, new)
    # df_manual['Search'] = df_manual['Full name'].str.replace(old, new)

df_manual['CMLCAstring'] = np.vectorize(stringer)(df_manual['Search'])

df_manual['UUID'] = np.vectorize(main_uuid)(df_manual['CMLCAstring'],
                                            df_manual['Unit'])

manual= df_manual[dictKeys].dropna().set_index('Full name').T.to_dict('dict')

biomatcher.update(manual)

# Iterate
cmlca22['CMLCAstring'] = np.vectorize(stringer)(cmlca22['Full name'])

#%% Last check, leaving 4 unmatched elements.
df_unlinked= slice_to_iterate()
