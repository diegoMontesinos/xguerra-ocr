# -*- coding: utf-8 -*-

import csv
import os

CSV_ANNUARY_FIELDNAMES = [ 'num_id', 'text_id', 'name', 'type', 'info' ]

PERSON_START_ID = 0
COMMUNITY_START_ID = 8999

class AnnuaryData:

  def __init__(self, csvpath=None):
    self.data = {}
    self.csvpath = csvpath

    should_read = (self.csvpath != None) and os.path.exists(self.csvpath)
    if should_read:
      self.load_from_file()
  
  def load_from_file(self):
    print('\nANNUARY DATA\n')
    print('Loading data from file: ' + self.csvpath + '...')
    
    with open(self.csvpath, 'rb') as csvfile:
      annuary_reader = csv.DictReader(csvfile, delimiter=',', quotechar="'", quoting=csv.QUOTE_NONNUMERIC)

      for register in annuary_reader:
        register['num_id'] = int(register['num_id'])
        self.add_register(register)
  
      print('Loaded ' + str(len(self.data)) + ' registers!')
    
    print('--------------')
  
  def print_status(self):
    print('\nANNUARY DIGITALIZATION STATUS\n')
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
  
  def search_by_num_id(self, num_id):
    if not (num_id in self.data):
      return None

    return self.data[num_id]
  
  def search_by_id(self, text_id, num_id):
    register = self.data[num_id]

    if (not register) or (register['text_id'] == text_id):
      return None
    
    return register
  
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
  
  def update_register(self, register):
    num_id = register['num_id']
    if not num_id in self.data:
      return False
    
    self.data[num_id] = register
    return True
  
  def save(self):
    if not self.csvpath:
      return
    
    print('\nSaving annuary data to file ' + self.csvpath + '...')

    # Create directories if dont exist
    basedir = os.path.dirname(self.csvpath)
    if not os.path.exists(basedir):
      os.makedirs(basedir)
    
    with open(self.csvpath, 'wb') as csvfile:
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