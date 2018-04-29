# -*- coding: utf-8 -*-

import csv
import os

CSV_ANNUARY_FIELDNAMES = [ 'num_id', 'text_id', 'name', 'type', 'info' ]

PERSON_START_ID = 0
COMMUNITY_START_ID = 8999

class AnnuaryData:

  def __init__(self, csvpath=None):
    self.data = {}

    should_read = (csvpath != None) and os.path.exists(csvpath)
    if should_read:
      self.load_from_file(csvpath)
  
  def load_from_file(self, csvpath):
    print('Loading data from file ' + csvpath + '...\n')
    
    with open(csvpath, 'rb') as csvfile:
      annuary_reader = csv.DictReader(csvfile, delimiter=',',
                                               quotechar="'",
                                               quoting=csv.QUOTE_NONNUMERIC)

      for register in annuary_reader:
        register['num_id'] = int(register['num_id'])
        self.add_register(register)
  
      print('Loaded ' + str(len(self.data)) + ' registers!')
  
  def print_status(self):
    print('ANNUARY DIGITALIZATION STATUS:\n')
    print('Saved ' + str(len(self.data)) + ' registers.')
    print('Person: ' + str(self.count_by_type('person')) + ' registers.')
    print('Community: ' + str(self.count_by_type('community')) + ' registers.\n')

    print('ID Missings:')
    self.print_missings(self.registers_by_type('person'), PERSON_START_ID)
    self.print_missings(self.registers_by_type('community'), COMMUNITY_START_ID)
  
  def count_by_type(self, register_type):
    count = 0

    for register_id in self.data:
      register = self.data[register_id]
      if register['type'] == register_type:
        count += 1
    
    return count
  
  def registers_by_type(self, register_type):
    registers = []

    sorted_ids = sorted(self.data)
    for register_id in sorted_ids:
      register = self.data[register_id]
      if register['type'] == register_type:
        registers.append(register)
    
    return registers
  
  def print_missings(self, registers, init_id):
    last_id = init_id

    for register in registers:
      range_diff = range(last_id, register['num_id'])
      if len(range_diff) > 1:
        print range_diff[1:]

      last_id = register['num_id']
  
  def add_register(self, register):
    if register['num_id'] in self.data:
      return False
    
    self.data[register['num_id']] = register
    return True
  
  def save(self, csvpath=None):
    if not csvpath:
      return
    
    print('Saving data to file ' + csvpath + '...')

    # Create directories if dont exist
    basedir = os.path.dirname(csvpath)
    if not os.path.exists(basedir):
      os.makedirs(basedir)
    
    with open(csvpath, 'wb') as csvfile:
      annuary_writer = csv.DictWriter(csvfile, fieldnames=CSV_ANNUARY_FIELDNAMES,
                                               delimiter=',',
                                               quotechar="'",
                                               quoting=csv.QUOTE_NONNUMERIC)

      annuary_writer.writeheader()

      sorted_ids = sorted(self.data)
      for register_id in sorted_ids:
        register = self.data[register_id]
        annuary_writer.writerow(register)
    
    print('File saved!')