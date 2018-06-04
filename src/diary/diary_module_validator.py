# -*- coding: utf-8 -*-

import re
from ..catalogs_data import CatalogsData
from ..utils import matches

class DiaryModuleValidator:

  SPACE_CHAR = '_'

  YEAR_PATTERN = re.compile(u'^[0-9]*$')

  def __init__(self):
    catalogs_data = CatalogsData()
    pass

  def validate_modules(self, modules):

    result = []

    for module in modules:
      result.append(self.validate_module(module))
    
    print result
    print '--'

    return  None
  
  def validate_module(self, module):

    # Start to validate each zone in the module
    is_valid = True
    
    index = len(module_id)
    for zone in module_type:
      size_zone = zone[1]
      zone_str = module[index:(index + size_zone)]

      is_valid = is_valid and self.validate_zone(zone, zone_str)

      index = index + size_zone
    
    return is_valid
  
  def validate_zone(self, zone, zone_str):
    catalog_id, size_zone = zone

    # Catalog 0 is empty spaces
    if catalog_id == 0:
      return (DiaryModuleValidator.SPACE_CHAR * size_zone) == zone_str
    
    # Catalog 1 is a year
    elif catalog_id == 1:
      return self.validate_year(zone_str)

    return True
  
  def validate_year(self, year_str):
    year_str = year_str.replace('O', '0')
    print 'yy:'
    print year_str

    if matches(DiaryModuleValidator.YEAR_PATTERN, year_str):
      year = int(year_str)
      if year < 40:
        print (1900 + year)
      else:
        print (1800 + year)

    return False