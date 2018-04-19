#!/usr/bin/python
# -*- coding: utf-8 -*-

# Import dependencies
import pytesseract
import argparse
import cv2
from src import *

def add_valid_register(register):
  print('Added register: ' + str(register))

def fix_reading_errors(binary_image, reading_errors):
  print('\nPlease, help me to fix the following errors (● ω ●):')

  # Send to fix all errors
  for reading_error in reading_errors:
    user_fix_error(binary_image, reading_error)

def user_fix_error(binary_image, reading_error):
  row, exception = reading_error
  print('\n' + str(exception))

  # Get ROI image and display
  x, y, w, h = row
  roi = binary_image[y:y+h, x:x+w]

  cv2.imshow('Bad readed row', roi)
  cv2.waitKey(1)

  # Wait user input and destroy the window
  user_input = raw_input('Enter the fixed register: ')
  cv2.destroyAllWindows()

  # Try to parse user input and catch errors to try again 
  try:
    register = parse_register_str(user_input)
    add_valid_register(register)
  except Exception as exception:
    print('Upsis, it seems that you enter an invalid register. Try again.')
    user_fix_error(binary_image, reading_error)

def process_rows(binary_image, rows, args):
  print('Processing rows...')

  reading_errors = []

  # Iterate all rows
  for i, row in enumerate(rows):
    x, y, w, h = row
    
    # Get ROI (region of interest) and execute OCR
    roi = binary_image[y:y+h, x:x+w]

    readed = pytesseract.image_to_string(roi)
    register_str = readed.encode('utf-8')

    # Parser and catch errors
    try:
      register = parse_register_str(register_str)
      add_valid_register(register)
    except Exception as exception:
      reading_errors.append((row, exception))
  
  print('Finished with ' + str(len(reading_errors)) + ' errors.')

  # Fix errors if exist
  if len(reading_errors) > 0:
    print('( ∩ ︵ ∩ )')
    fix_reading_errors(binary_image, reading_errors)
  else:
    print('Perfect (✿ ♥ ‿ ♥ )!')

def process_image(args):
  print('Processing file ' + args.input + '...')

  # Read image source
  image_src = cv2.imread(args.input)
  if args.debug:
    show_scaled_image('source', image_src, 0.35)

  # Get binary image
  binary_image = binarize_image(image_src)
  if args.debug:
    show_scaled_image('binary', binary_image, 0.35)

  # Get rows
  rows = find_rows(binary_image, args)
  print('\nFind ' + str(len(rows)) + ' rows!')

  if args.debug:
    boxes_img = draw_boxes(binary_image, rows, (0, 255, 0))
    show_scaled_image('rows', boxes_img, 0.35)
  
  # Process rows
  process_rows(binary_image, rows, args)

# Main script
def main():

  # Config parser
  parser = argparse.ArgumentParser(description='Digitalization of Annuary-part from Francois-Xavier Guerra database.')
  parser.add_argument('-i', '--input', help='Input image file', required=True)
  parser.add_argument('-o', '--output', help='Output CSV file', default='output.csv')
  parser.add_argument('-d', '--debug', help='Debug parameter', action='store_true')

  args = parser.parse_args()
  process_image(args)

if __name__ == '__main__':
  pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'
  main()
