# -*- coding: utf-8 -*-

import csv
import os

class AnnuaryData:

  def __init__(self, csvpath=None):
    self.data = {}
    self.csvpath = csvpath

    if (csvpath != None) and os.path.exists(csvpath):
      self.load_from_file(csvpath)
    
  def load_from_file(self, csvpath):
    print('Loading data from file ' + csvpath + '...')
    pass
  
  def add_register(self, register):
    if register['id'][1] in self.data:
      return
    
    self.data[register['id'][1]] = register
    print('Added register: ' + str(register))
  
  def save(self, csvpath=None):
    if csvpath == None:
      return
    
    print('Saving data to file ' + csvpath + '...')

    # Create directories if dont exist
    basedir = os.path.dirname(csvpath)
    if not os.path.exists(basedir):
      os.makedirs(basedir)
    
    with open(csvpath, 'wb') as csvfile:
      annuary_writer = csv.writer(csvfile, delimiter=',')

      sorted_data = sorted(self.data)

      for register_id in sorted_data:
        register = self.data[register_id]
        annuary_writer.writerow([
          register['id'][0],
          register['id'][1],
          register['name'],
          register['type']
        ])