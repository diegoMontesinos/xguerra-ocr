# -*- coding: utf-8 -*-

import csv

class AnnuaryData:

  def __init__(self, csvpath=None):
    self.data = {}

    if (csvpath != None) and (csvpath != ''):
      self.loadDataFromFile(csvpath)
    
  def loadDataFromFile(self, csvpath):
    pass
  
  def add_register(self, register):
    if register['id'] in self.data:
      return
    
    self.data[register['id']] = register
    print('Added register: ' + str(register))
  
  def save(self):
    pass