# -*- coding: utf-8 -*-

import csv
import os

class AnnuaryData:

  def __init__(self, csvpath=None):
    self.data = {}

    if (csvpath != None) and os.path.exists(csvpath):
      self.load_from_file(csvpath)
    
  def load_from_file(self, csvpath):
    print('Loading data from file ' + csvpath + '...\n')
    
    with open(csvpath, 'rb') as csvfile:
      annuary_reader = csv.reader(csvfile, delimiter=',')
      for row in annuary_reader:
        register = {
          'id': (int(row[0]), row[1]),
          'name': row[2],
          'type': row[3]
        }
        self.add_register(register)
  
  def add_register(self, register):
    if register['id'][0] in self.data:
      return
    
    self.data[register['id'][0]] = register
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