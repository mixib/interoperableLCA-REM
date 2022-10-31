# -*- coding: utf-8 -*-
"""
From IO_20190923, created on Tue Sep 17 10:32:54 2019
Modified into a function that imports databases from a Excel file to a brightway project.
@author: xicotencatlbm
The selection of input variables is manual (project, file, database name[96]).
Also the selection of the ei technosphere version [60 or 65]. To overwrite[75].
"""
#Importing some modules
from pathlib import Path
import brightway2 as bw
from bw2io.export import write_lci_excel

#%% Function
def import_from_ExcelFile(project, background, data, save, newXL):
    #%%Loading an environment for the import check
    bw.projects.set_current(project)
    print('The databases in the selected project, before importing your new data are:')
    print (bw.databases)

    #%%#%%Import the excel file

    datapath = Path.cwd()/'data/bw-harmonised'/data
    imp = bw.ExcelImporter(datapath)

    #%% Match flows with existing and current databases after general strategies.

    imp.apply_strategies()

    # Current database
    imp.match_database(fields=('code', 'location', 'unit'))

    # Match biosphere flows.
    imp.match_database('biosphere3', fields=('name', 'code', 'unit'),
                       kind='biosphere')

    #Match technosphere flows with background.
    imp.match_database(background, fields=('name', 'reference product', 'location', 'unit'),
                       kind='technosphere')

    imp.statistics()

    #%%
    imp.write_excel()

    if save == True:
        #%% Save new database
        imp.write_database()
    if save == False:
        print('If you want to save the imported database, use save = True')
    #%%Erase imp
    # if 'imp' in globals():
    #     del imp

    #%% Check save
    print('The databases in the selected project, after importing your new data are:')
    print (bw.databases)

    return imp

    #%% Generate new Excel file.
    if newXL == True:
        write_lci_excel(project)
