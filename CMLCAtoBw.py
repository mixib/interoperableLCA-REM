# -*- coding: utf-8 -*-
"""
Created on Mon Sep 23 14:04:53 2019
Major editions on Tue Feb  4 12:47:28 2020

@author: xicotencatlbm

"""

#%%Import modules

from pathlib import Path
import pandas as pd
import numpy as np

import idFunctions as fx

#%%
def convertFromCMLCAeiV2_2(project, target, replace2ndNi, disconnect):

    databaseName = project + target
    bw2File = databaseName + '.xlsx'
    sourceFile = 'processDataCMLCA.xlsx'

    #%% Fetch the file with the unit processes

    file = Path.cwd()/'data'/sourceFile

    pd_import = pd.read_excel(file,
                              sheet_name = 'processData').dropna(
                                  subset=['Label_or_metadata'])
    pd_import = pd_import[pd_import['Label_or_metadata'] !='Label']

    #%% Overwrite automatic matching of secondary Ni if replace2ndNi is True.

    if replace2ndNi == True:
        secondaryNi = ('nickel, secondary, from electronic and electric scrap '
                       'recycling, at refinery[SE]')
        primaryNi = 'nickel, 99.5%, at plant[GLO]'
        pd_import.replace(secondaryNi, primaryNi, inplace = True)
        print ('The economic flow "', secondaryNi, '" was replaced by "',
               primaryNi, '".')

    #%% Fetch allocation data

    allocDF = pd.read_excel(file, sheet_name = 'allocFactors',
                            index_col=[0,1], usecols='B,C,D,G,H')

    #%% From fx, apply the function that identifies the type of flow (G/W/E)
    pd_import['type'] = pd_import['Label_or_metadata'].apply(fx.typer)

    #%%
    ########################### waste convention #################################
    #%% Filter for strings corresponding to waste treatment flows.
    if target == '2_2':
        pd_import['amount'] = pd_import['Value']
    else:
    # Change sign to signal waste according to bw-ecoinvent v3.x conventions.
        pd_import.loc[
        (pd_import['type']=='technosphere')&(
            pd_import['Name'].str.startswith('disposal,')),
        'amount' ] = (-pd_import['Value'])

    pd_import.loc[ # Record amount as it is.
                  (~pd_import['Name'].str.startswith('disposal,', na=False)),
                  'amount' ] = pd_import['Value']

    # df.loc[df['dollars_spent'] > 0, 'purchase'] = 1

    ##############################################################################

    ########################Read markers##########################################
    #%% Iterate each row and assign a process identificator
    for row in pd_import.index:
        processID = pd_import.at[row,'ID']
        if processID != 0:
            newID = 'P' + str(processID)
        pd_import.at[row,'newID'] = newID

    pd_import.reset_index(drop = True, inplace = True)

    #%% Iterate each row and identify the economic outputs

    for row in pd_import.index:
        IOmarker = pd_import.at[row, 'IO_ID']
        try:
            IOantmarker = pd_import.at[row - 1, 'IO_ID']
        except:
            IOantmarker = 0
        if IOantmarker == 1:
            if IOmarker != 2:
                pd_import.at[row,'type'] = 'production'
                pd_import.at[row,'IO_ID'] = 1

    pd_import.set_index('newID', inplace= True)

    # ^^^The content above doesn't need modifications at this stage^^^^^^^^^^^^^^
    ##############################################################################
    ################strip activity name, biosphere code and reference product#####
    #%% Initialise flowdata.

    # Create a newcolumn in pd_import with the 'name', 'location' and
    # 'reference product' ready for brightway.

    pd_import['name'] = np.vectorize(fx.findName)(pd_import['Name'],
                                                  pd_import['Unit'],
                                                  pd_import['type'],
                                                  target,
                                                  disconnect)
    pd_import['location'] = np.vectorize(fx.findLocation)(pd_import['Name'],
                                                          pd_import['Unit'],
                                                          pd_import['type'],
                                                          target)
    pd_import['reference product'] = np.vectorize(fx.findRP)(pd_import['Name'], # result modified at idFunctions. Maybe later: also add the reference product of the technospshere or use the whole column as "(activity) name" and
                                                             pd_import['Unit'],
                                                             pd_import['type'],
                                                             target)
    pd_import['code'] = np.vectorize(fx.findUUID)(pd_import['Name'],
                                                  pd_import['type'])

    # Extract flow data
    flowdata = pd_import[['name', 'amount', 'Unit', 'type', 'code', 'location', # Replaced from 'Value' to 'amount' for waste conventions.
                          'reference product','Name']].rename( # Name contains primary technoMatcher key
                              columns ={'Unit':'unit'}).dropna(
                                  subset = ['name'])
    # Convert amount to float.
    flowdata['amount'] = flowdata['amount'].astype('float64')

    ##############################################################################
    # newbit
    # Identify functionality of processes and create a dictionary for
    # monofunctional processes with production codes.

    # Count the functions associated to each process.
    functionality = pd_import[pd_import['type'] == 'production'].groupby(
        'newID').count()

    # Identify the monofunctional and multifunctional processes.
    multifunctionals = functionality[functionality['type']> 1].index.tolist()
    monofunctionals = functionality[functionality['type']== 1].index.tolist()

    productCodesMonofunctional = pd_import.loc[
        (pd_import['type'] == 'production'), 'Name'
        ].loc[monofunctionals
              ].reset_index().set_index('Name').to_dict()['newID']

    # With Unit
    # productCodesMonofunctional = pd_import.loc[
    #     (pd_import['type'] == 'production'), ('Name', 'Unit')
    #     ].loc[monofunctionals
    #           ].reset_index().set_index(['Name','Unit']).to_dict()['newID']


    productCodesPartitioned = {}

    for process, partition in allocDF.index:
        key = allocDF.loc[(process, partition), 'name']
        activityCode = process + '.' + str(partition +1)
        productCodesPartitioned.update({key : activityCode})

    #################### Find CUT_OFFS, originally used the prefix 'not34'########
    #%% Identify cut-off names

    # technosphere = list(flowdata.loc[(flowdata['type'] =='technosphere'),
    #                                  ('name', 'reference product','unit')
    #                                  ].drop_duplicates(
    #                                      ).itertuples(index=False, name = None))

    technosphere = list(flowdata.loc[(flowdata['type'] =='technosphere'),
                                      ('Name','unit')
                                      ].drop_duplicates(
                                          ).itertuples(index=False, name = None))

    flowdata.drop(columns='Name', inplace=True) # Drop imported name column.

    # cut_offsList = fx.findCut_offs(technosphere,
    #                            [productCodesMonofunctional,
    #                             productCodesPartitioned])

    cut_offsDf= pd.DataFrame(fx.findCut_offs(technosphere,
                                [productCodesMonofunctional,
                                productCodesPartitioned]))
    cut_offsList = cut_offsDf[0]

    # Return a dataframe with the product name and unit of the cut-offs.
    CUT_OFFS = flowdata.loc[(flowdata['name']).isin(cut_offsList),
                             ['name','unit']].drop_duplicates().reset_index(
                                 drop = True).rename(
                                     columns = {'name' : 'reference product'})# name might change to reference product at an earlier stage

    CUT_OFFS['Activity'] = 'Production of ' + CUT_OFFS['reference product']
    CUT_OFFS['code'] = 'cut-off_' + CUT_OFFS['reference product']
    CUT_OFFS['categories'] = 'cut-off'
    CUT_OFFS['production amount'] = 1

    productCodesCut_offs = CUT_OFFS[['reference product', 'code']].set_index(
        'reference product').to_dict()['code']

    productCodesForeground = {}
    productCodesForeground.update(productCodesMonofunctional)
    productCodesForeground.update(productCodesPartitioned)
    productCodesForeground.update(productCodesCut_offs)

    cut_offs = CUT_OFFS.T

    #############################shifted code command############################
    #%% Add code field for the technosphere and production exchanges to flowdata
    flowdata['code'] = np.vectorize(fx.findCode)(flowdata['code'], flowdata['name'], #might change to reference product
                                                  flowdata['type'],
                                                  productCodesForeground)

    #%% Create a dataframe from the metadata and the exchange flows by
    # slicing columns from pd_import.

    # Extract the metadata
    pd_import['metadata'] = pd_import['Label_or_metadata'].apply(fx.metaExtract)
    pd_import['label'] = pd_import['Label_or_metadata'].apply(fx.labelExtract)

    # Declare the metadata
    metadata = pd_import[['label', 'metadata']].dropna(subset = ['label'])


    #%% Export the database to Excel

    # Create a Pandas Excel writer using XlsxWriter as the engine.
    # [See https://xlsxwriter.readthedocs.io/example_pandas_positioning.html]

    writer = pd.ExcelWriter((Path.cwd()/'data/bw-harmonised'/bw2File), engine='xlsxwriter')

    layout_mono = ['Activity', 'code', 'Description',
                   'Author', 'Date', 'Exchanges']
    layout_unAlloc = ['code','Activity', 'Description', 'Author', #change/corrected for waste
                      'Date','Exchanges']
    layout_multi = ['Activity', 'categories', 'code',
                    'Description', 'Author', 'Date', #'production amount', 'unit', #new bit
                    'allocation factor', 'Exchanges']
    layout_cutOffs = ['Activity', 'categories','code','reference product',
                      'production amount', 'unit']

    # Sheet with monofunctional processes.
    pd.DataFrame([['Database', databaseName]],
                 columns = ['label', 'metadata']).to_excel(
                     writer, sheet_name='monofunctional',
                     header=False, index=False)

    starter = 2

    for process in monofunctionals:
        metadataSection = metadata.loc[process].append(
            pd.DataFrame([['code',str(process)],['Exchanges','']],
                         columns=['label','metadata'])).set_index(
                             'label').reindex(layout_mono)

        flowSection = flowdata.loc[process]

        metadataSection.to_excel(writer, sheet_name='monofunctional',
                                 header=False, startrow=starter)
        flowSection.to_excel(writer, sheet_name='monofunctional', index=False,
                             startrow= starter + len(metadataSection.index))

        space = len(metadataSection.index) + len(flowSection.index) + 2
        starter = starter + space

    # Sheet with cut-offs

    starter = 0

    for process in list(cut_offs):
        cut_offs[process].reindex(layout_cutOffs).to_excel(writer, sheet_name='cut_offs', header=False,
                                   startrow=starter)

        space = len(cut_offs.index) + 1
        starter = starter + space

    # Sheet with partitioned processes based on parsed allocation factors.
    starter = 0

    for process, partition in allocDF.index:

        referenceProduct = allocDF.loc[(process, partition), 'name'] #should be reference product
        allocFactor = allocDF.loc[(process, partition), 'preset_alloc']

        activityCode = productCodesPartitioned.get(referenceProduct)
        metadataSection = metadata[metadata['label'] != 'Activity'].loc[
            process].append(pd.DataFrame([[
                'code', activityCode],['Exchanges','']],
                columns=['label','metadata'])).set_index('label').reindex(
                    layout_multi)

        activity = (metadata[metadata['label']=='Activity'].loc[process,
                                                                'metadata']
                    + '_' + str(partition + 1))
        metadataSection.at['Activity', 'metadata'] = activity

        tempName = referenceProduct
        productionAmount = flowdata.loc[(flowdata['type']== 'production') & (
            flowdata['name']== tempName), 'amount'].loc[process]
        activityUnit = flowdata.loc[(flowdata['type']== 'production') & (
            flowdata['name']== tempName), 'unit'].loc[process]

        metadataSection.at['allocation factor', 'metadata'] = allocFactor
        metadataSection.at['categories', 'metadata'] = 'partitioned'

        preFlowSection = flowdata[flowdata['type'] !='production'].loc[process]
        preFlowSection['amount'] = allocFactor*preFlowSection[['amount']]

        columnsFS = ['name', 'amount', 'unit', 'type', 'code', 'location',
                     'reference product']
        preflowSection = preFlowSection[columnsFS]

        refProduct = allocDF.loc[(process, partition), 'name']
        productionLine = pd.DataFrame([
            [refProduct, productionAmount, activityUnit, 'production',
             activityCode, '', '']], columns = columnsFS)
        flowSection = preflowSection.append(productionLine)


        metadataSection.to_excel(writer, sheet_name='partitioned', header=False,
                                 startrow=starter)
        flowSection.to_excel(writer, sheet_name='partitioned', index=False,
                             startrow= starter + len(metadataSection.index))

        space = len(metadataSection.index) + len(flowSection.index) + 2
        starter = starter + space

    pd.DataFrame([['skip']], columns = ['placeholder']).to_excel(
        writer, sheet_name='multifunctional', header=False, index=False)

    starter = 2

    for process in multifunctionals:
        metadataSection = metadata.loc[
            process].append(pd.DataFrame([['code', str(process)],
                                          ['Exchanges','']], columns=[
                                              'label','metadata'])).set_index(
                                                  'label').reindex(layout_unAlloc)
        flowSection = flowdata.loc[process]

        metadataSection.to_excel(writer, sheet_name='multifunctional',
                                 header=False, startrow=starter)
        flowSection.to_excel(writer, sheet_name='multifunctional', index=False,
                             startrow= starter + len(metadataSection.index))

        space = len(metadataSection.index) + len(flowSection.index) + 2
        starter = starter + space


    writer.save()
