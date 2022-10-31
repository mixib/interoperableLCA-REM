# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 10:37:30 2020

Helper functions to identify certain things from the process data.

@author: xicotencatlbm
"""
from technoMatcher import technoMatch, cd3_1, mcd_ge

from bioMatcher import biomatcher as bioMatcher

#%% Function to identify the type of flow

def typer(label):
    if label.startswith('[G'):
        return 'technosphere'
    elif label.startswith('[W'):
        return 'technosphere'
    elif label.startswith('[E'):
        return 'biosphere'

#%% Functions to identify the name of any flow and the code if it is a
# biosphere flow.

def findName (ei22Key, unit, flowType, target_db, disconnect):
    try:
        if flowType == 'biosphere':
            if disconnect==True:
                if flowType == 'biosphere':
                    matchType = bioMatcher.get(ei22Key).get('Matching type')
                    if matchType == 'semiautomatic' or matchType == 'Manual by BMX':
                        print("Omitting "+ ei22Key)
                    else:
                        cmlcaString = bioMatcher.get(ei22Key).get('CMLCAstring')
                        return cmlcaString.split('[')[0]
            else:
                cmlcaString = bioMatcher.get(ei22Key).get('CMLCAstring')
                return cmlcaString.split('[')[0]

        elif flowType == 'technosphere' or flowType == 'production':
            return technoMatch(ei22Key, unit, target_db).get('activityName')
    except AttributeError:
        return ei22Key

def findCode (current, ei22Key, flowType, productDict):
    '''Return the flow code of a string marked as technosphere or production,
    if it exists'''
    if flowType != 'biosphere':
        newID = productDict.get(ei22Key)
        if newID is not None:
            return str(productDict.get(ei22Key))
        else:
            return None
    else:
        return current

def findUUID (ei22Key, flowType):
    '''Return the UUID of a string marked as biosphere type if it exists. If
    it doesn't exist, print that no code was found'''
    if flowType == 'biosphere':
        try:
            return bioMatcher.get(ei22Key).get('UUID')
        except AttributeError:
            print('No code for the environmental flow "' + ei22Key +'" was found.')

#%% Function to identify the location of a technosphere flow.

def findLocation (ei22Key, unit, flowType, target_db):
        if flowType == 'technosphere':
            try:
                return technoMatch(ei22Key, unit, target_db).get('geography')
            except AttributeError:
                return None

#%% Function to identify the reference product of a process.

def findRP (ei22Key, unit, flowType, target_db):
    if flowType == 'technosphere':
        try:
            return technoMatch(ei22Key, unit, target_db).get('product name')
        except AttributeError:
            return None
    elif flowType == 'production':
        return ei22Key

#%% Helper function to strip the name of the process
def metaExtract (metadata):
    if metadata.startswith('Process'):
        return metadata.split(']')[1].strip()
    if metadata.startswith(('Description','Author','Date')):
        return metadata.split('=')[1].strip()

def labelExtract (label):
    if label.startswith(('Description','Author','Date')):
        return label.split('=')[0].strip()
    elif label.startswith('Process'):
        return 'Activity'

#%% Function to identify cutt-offs

def findCut_offs(flowList, dictionaryList):
    '''Search listed flows in the technoMatcher dictionary and in the listed
    dictionaries. Return a list of flows that are in neither dictionary'''
    cut_offs = []

    for importedName, unit in flowList:
        found = False
        if importedName in dictionaryList[0]:
            print('Flow "', importedName, '"(', unit,
                  ') was found in the foreground dictionary; process index: ',
                  dictionaryList[0][importedName] )
            continue
        elif importedName in dictionaryList[1]:
            print('Flow "', importedName, '"(', unit,
                  ') was found in the foreground dictionary; process index: ',
                  dictionaryList[1][importedName] )
            continue
        elif(importedName, unit) in mcd_ge:
            print('Flow "', importedName, '"(', unit,
                  '" was found in the background dictionary and '
                  'migrated to the target ecoinvent version using the general '
                  'manual correspondences.')
            continue
        elif (importedName, unit) in cd3_1:
            found = True
            print('Flow "', importedName, '"(', unit,
                          '" was found in the background dictionary and '
                          'migrated to the target ecoinvent version using the '
                          'ecoinvent correspondences')
            continue

        # if not found:
        if found == False:
            cut_offs.append((importedName, unit))
    return cut_offs
