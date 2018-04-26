#!/usr/bin/python
# -*- coding: utf-8 -*-

# Import dependencies
import pytesseract
import argparse
import cv2
import os
from src import *

PAGE_ROI = (80, 0, 3350, 5220)

def process_image(args, annuary_data):
  print('Processing file ' + args.input + '...')

  if not os.path.exists(args.input):
    print('Error on reading or file input dont exist. ( ∩ ︵ ∩ )')
    return

  # Read image source and crop it
  image_src = cv2.imread(args.input)
  image_src = crop_roi(image_src, PAGE_ROI)
  if args.debug:
    show_scaled_image('source', image_src, 0.4)

  # Get binary image
  binary_image = binarize_image(image_src)
  if args.debug:
    show_scaled_image('binary', binary_image, 0.4)
  
  # Get columns
  cols = find_columns_on_annuary(binary_image, args)

  # Process rows from each column
  print('Processing rows...')

  reading_errors = []
  for col in cols:
    img_col = crop_roi(binary_image, col)

    # Get rows and process rows
    rows = find_rows_on_annuary(img_col, args)
    reading_errors += process_rows(img_col, rows, annuary_data, args)

  print('Finished with ' + str(len(reading_errors)) + ' errors.')

  # Fix errors if exist
  if len(reading_errors) > 0:
    fix_reading_errors(reading_errors, annuary_data)
  else:
    print('Perfect (✿ ♥ ‿ ♥ )!')

def process_rows(img_col, rows, annuary_data, args):

  reading_errors = []

  for i, row in enumerate(rows):
    
    # Get ROI (region of interest) and execute OCR
    roi = crop_roi(img_col, row)

    readed = pytesseract.image_to_string(roi)
    register_str = readed.encode('utf-8')

    # Parser and catch errors
    try:
      register = parse_register_str(register_str)
      added = annuary_data.add_register(register)

      if added:
        print('Added register: ' + str(register))
    except Exception as exception:
      reading_errors.append((img_col, row, exception))
    
  return reading_errors

def fix_reading_errors(reading_errors, annuary_data):
  print('\nPlease, help me to fix the following errors (● ω ●):')

  # Send to fix all errors
  for reading_error in reading_errors:
    user_fix_error(reading_error, annuary_data)

def user_fix_error(reading_error, annuary_data):
  img_col, row, exception = reading_error
  print('\n' + str(exception))

  # Get ROI image and display
  roi = crop_roi(img_col, row)
  cv2.imshow('Bad readed row', roi)
  cv2.waitKey(1)

  # Wait user input and destroy the window
  user_input = raw_input('Enter the fixed register: ')
  cv2.destroyAllWindows()

  # Try to parse user input and catch errors to try again 
  try:
    register = parse_register_str(user_input)
    added = annuary_data.add_register(register)

    if added:
      print('Added register: ' + str(register))
  except Exception as exception:
    print('Upsis, it seems that you enter an invalid register. Try again.')
    user_fix_error(reading_error, annuary_data)

# Main script
def main():

  # Config parser
  parser = argparse.ArgumentParser(description='Digitalization of Annuary-part from Francois-Xavier Guerra database.')
  parser.add_argument('-i', '--input', help='Input image file')
  parser.add_argument('-o', '--output', help='Output CSV file', default='csv/annuary.csv')
  parser.add_argument('-d', '--debug', help='Enable debug option', action='store_true')
  parser.add_argument('-s', '--status', help='Show status from output', action='store_true')

  args = parser.parse_args()

  annuary_data = AnnuaryData(args.output)

  if args.status:
    annuary_data.print_status()
    return

  if not args.input:
    print('error: argument -i/--input is required')
    return
  
  process_image(args, annuary_data)
  annuary_data.save(args.output)

if __name__ == '__main__':

  pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'
  main()
