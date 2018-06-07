# -*- coding: utf-8 -*-

import csv
import os

CSV_DIARY_FIELDNAMES = [ 'annuary_id', 'module' ]

class DiaryData:

  def __init__(self, csvpath=None):
    self.data = {}

    self.csvpath = csvpath

    should_read = (self.csvpath != None) and os.path.exists(self.csvpath)
    if should_read:
      self.load_from_file()

  def load_from_file(self):
    print('\nDIARY DATA\n')
    print('Loading data from file: ' + self.csvpath + '...')
    
    with open(self.csvpath, 'rb') as csvfile:
      diary_reader = csv.DictReader(csvfile, delimiter=',', quotechar="'", quoting=csv.QUOTE_NONNUMERIC)

      for register in diary_reader:
        self.add_module(register['annuary_id'], register['module'])
  
      print('Loaded ' + str(len(self.data)) + ' registers!')
    
    print('--------------')

  def add_module(self, annuary_id, module):

    module_str = module

    if not isinstance(module, str):
      module_str = '|'.join(module)

    # Check if the module has been added
    if (annuary_id in self.data) and (module_str in self.data[annuary_id]):
      return False
    
    # If is the first module its create the register
    if not annuary_id in self.data:
      self.data[annuary_id] = []
    
    self.data[annuary_id].append(module_str)
    return True
  
  def search_by_annuary_id(self, annuary_id):
    if not (annuary_id in self.data):
      return None

    return self.data[annuary_id]
  
  def save(self):
    if not self.csvpath:
      return
    
    print('\nSaving diary data to file ' + self.csvpath + '...')

    # Create directories if dont exist
    basedir = os.path.dirname(self.csvpath)
    if not os.path.exists(basedir):
      os.makedirs(basedir)
    
    with open(self.csvpath, 'wb') as csvfile:
      diary_writer = csv.DictWriter(csvfile, fieldnames=CSV_DIARY_FIELDNAMES,
                                             delimiter=',',
                                             quotechar="'",
                                             quoting=csv.QUOTE_NONNUMERIC)

      diary_writer.writeheader()

      sorted_ids = sorted(self.data)
      for annuary_id in sorted_ids:
        modules = self.data[annuary_id]
        
        for module_str in modules:
          csvrow = { 'annuary_id': int(annuary_id), 'module': module_str }
          diary_writer.writerow(csvrow)
    
    print('File saved!')