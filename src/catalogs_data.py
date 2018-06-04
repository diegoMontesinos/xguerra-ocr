# -*- coding: utf-8 -*-

import csv

class CatalogsData:

  CATALOGS_DESCRIPTION = {
    2:  { 'file': '02_months', 'header': [ 'month_id', 'month' ] },
    3:  { 'file': '03_places', 'header': [ 'place_id', 'place' ] },
    5:  { 'file': '05_occupations', 'header': [ 'occupation_id', 'occupation' ] },
    6:  { 'file': '06_return_active', 'header': [ 'return_active_id', 'return_active' ] },
    7:  { 'file': '07_local_factions', 'header': [ 'local_faction_id', 'place_id', 'local_faction' ] },
    8:  { 'file': '08_public_actions', 'header': [ 'public_action_id', 'public_action' ] },
    9:  { 'file': '09_cities', 'header': [ 'city_id','place_id','city' ] },
    10: { 'file': '10_cultural_levels', 'header': [ 'cultural_level_id','cultural_level' ] },
    11: { 'file': '11_school_types', 'header': [ 'school_type_id','school_type' ] },
    12: { 'file': '12_political_trends', 'header': [ 'political_trend12_id','political_trend12' ] },
    13: { 'file': '13_fam_political_trends', 'header': [ 'fam_political_trend_id','fam_political_trend' ] },
    14: { 'file': '14_richness', 'header': [ 'richness_id','richness' ] },
    16: { 'file': '16_schools', 'header': [ 'school_id','place_id','school' ] },
    17: { 'file': '17_academic_statuses', 'header': [ 'academic_status_id','academic_status' ] },
    18: { 'file': '18_geographical_orientation', 'header': [ 'geographical_orientation_id','geographical_orientation' ] },
    19: { 'file': '19_death_causes', 'header': [ 'death_cause_id','death_cause' ] },
    20: { 'file': '20_locality_types', 'header': [ 'locality_type_id','locality_type' ] },
    21: { 'file': '21_religions', 'header': [ 'religion_id','religion' ] },
    22: { 'file': '22_ethnics', 'header': [ 'ethnics_id','ethnics' ] },
    23: { 'file': '23_retirement_causes', 'header': [ 'retirement_cause_id','retirement_cause' ] },
    24: { 'file': '24_trends_belonging', 'header': [ 'trends_belonging_id','trends_belonging' ] },
    25: { 'file': '25_ministries', 'header': [ 'ministry_id','ministry' ] },
    26: { 'file': '26_parliamentarians', 'header': [ 'parliamentarian_id','parliamentarian' ] },
    29: { 'file': '29_political_trends', 'header': [ 'political_trend_29id','political_trend_29' ] },
    30: { 'file': '30_charge_characteristics', 'header': [ 'charge_characteristics_id','charge_characteristics' ] },
    31: { 'file': '31_personal_links', 'header': [ 'personal_link_id','personal_link' ] },
    33: { 'file': '33_political_positions', 'header': [ 'political_position_id','political_position' ] },
    34: { 'file': '34_social_movements', 'header': [ 'social_movement_id','social_movement' ] },
    35: { 'file': '35_collective_events', 'header': [ 'collective_event_id','collective_event' ] },
    36: { 'file': '36_content_measures', 'header': [ 'content_measure_id','content_measure' ] },
    37: { 'file': '37_measure_types', 'header': [ 'measure_type_id','measure_type' ] },
    38: { 'file': '38_military_rank_precisions', 'header': [ 'military_rank_precision_id','military_rank_precision' ] },
    39: { 'file': '39_careers', 'header': [ 'career_id','career' ] },
    40: { 'file': '40_recognised_child', 'header': [ 'recognised_child_id','recognised_child' ] },
    41: { 'file': '41_military_divisons', 'header': [ 'military_division_id','military_division_id' ] }
  }

  def __init__(self):
    self.catalogs = {}

    print('\nCATALOGS DATA\n')
    for catalog_id in CatalogsData.CATALOGS_DESCRIPTION:
      self.load_catalog(catalog_id, CatalogsData.CATALOGS_DESCRIPTION[catalog_id])
    print('--------------')
  
  def load_catalog(self, catalog_id, catalog_description):
    csvpath = 'csv/' + catalog_description['file'] + '.csv'

    print('Loading catalog from file ' + csvpath + '...')

    catalog = {
      'header'    : catalog_description['header'],
      'registers' : []
    }

    with open(csvpath, 'rb') as csvfile:
      csvreader = csv.DictReader(csvfile, delimiter=',', quotechar="'", quoting=csv.QUOTE_NONNUMERIC)

      for register in csvreader:
        catalog['registers'].append(register)
    
    self.catalogs[catalog_id] = catalog
  
  def get(self, catalog_id):
    if not catalog_id in self.catalogs:
      return None

    return self.catalogs[catalog_id]