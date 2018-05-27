# -*- coding: utf-8 -*-

class DiaryData:

  def __init__(self, csvpath=None):
    self.data = {}
    self.csvpath = csvpath

  def add_content(self, register, content):
    num_id = register['num_id']
    if num_id in self.data:
      return False
    
    self.data[num_id] = content
    return True
  
  def save(self):
    if not self.csvpath:
      return
    
    print('Saving diary data to file ' + self.csvpath + '...')

    # Create directories if dont exist
    basedir = os.path.dirname(csvpath)
    if not os.path.exists(basedir):
      os.makedirs(basedir)

    with open(self.csvpath, 'wb') as csvfile:
      diary_writer = csv.DictWriter(csvfile, fieldnames=CSV_DIARY_FIELDNAMES,
                                             delimiter=',',
                                             quotechar="'",
                                             quoting=csv.QUOTE_NONNUMERIC)
      
      diary_writer.writeheader()

      sorted_ids = sorted(self.data)