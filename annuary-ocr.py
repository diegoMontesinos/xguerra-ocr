#!/usr/bin/python
# -*- coding: utf-8 -*-

import pytesseract
import argparse
import cv2
import numpy as np
import re

# Constants
IMAGE_SCALE = 0.35

ONLY_UPPERCASE_LETTERS = re.compile(u'^[A-Z]*$')
ONLY_NUMBERS           = re.compile(u'^[0-9]*$')
ONLY_UPPERCASE_DOTS    = re.compile(u'^[A-Z. \(\)]*$')

def show_scaled_image(title, img, scale, wait=True):

  height, width = img.shape[:2]
  resized = cv2.resize(img, (int(width * scale), int(height * scale)))

  cv2.imshow(title, resized)

  if wait:
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def binarize_image(image_src):

  gray = cv2.cvtColor(image_src, cv2.COLOR_BGR2GRAY)
  ret, binary = cv2.threshold(gray, 70, 255, cv2.THRESH_BINARY_INV)

  return binary

def find_rows(binary_image, args):

  # Dilate image
  kernel_dilation = np.ones((1, 15), np.uint8)
  image_dilation = cv2.dilate(binary_image, kernel_dilation, iterations=1)

  if args.debug:
    show_scaled_image('rows dilation', image_dilation, IMAGE_SCALE)
  
  # Close image
  kernel_closing = np.ones((2, 95), np.uint8)
  image_closing = cv2.morphologyEx(image_dilation, cv2.MORPH_CLOSE, kernel_closing)

  if args.debug:
    show_scaled_image('rows closing', image_closing, IMAGE_SCALE)
  
  # Find contours
  im2, contours, hierarchy = cv2.findContours(image_closing, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

  if args.debug:
    contours_img = draw_contours(binary_image, contours)
    show_scaled_image('contours rows', contours_img, IMAGE_SCALE)
  
  # Create rows
  rows = []
  for contour in contours:
    row = cv2.boundingRect(contour)

    if (is_valid_row(row)):
      rows.append(row)
  
  print('Finded ' + str(len(rows)) + ' rows.')

  return rows

def is_valid_row(row):
  w = row[2]
  h = row[3]

  area = w * h
  return (area > 20000) and (h < 60)

def draw_contours(binary_image, contours):
  channel = cv2.split(binary_image)[0]

  contours_img = cv2.merge((channel, channel, channel))
  cv2.drawContours(contours_img, contours, -1, (0, 255, 0), 2)

  return contours_img

def draw_boxes(binary_image, boxes, stroke):
  channel = cv2.split(binary_image)[0]

  boxes_img = cv2.merge((channel, channel, channel))
  for box in boxes:
    x, y, w, h = box
    cv2.rectangle(boxes_img, (x, y), (x + w, y + h), stroke, 1)
  
  return boxes_img

def process_rows(binary_image, rows, args):
  print('Process rows and dump into ' + args.output)

  bad_count = 0

  for i, row in enumerate(rows):
    x, y, w, h = row
    
    roi = binary_image[y:y+h, x:x+w]

    if args.debug:
      cv2.imwrite('output/row' + str(i) + '.png', roi)

    readed = pytesseract.image_to_string(roi)
    register_str = readed.encode('utf-8')

    try:
      register = parse_register_str(register_str)
      #print register
    except Exception as e:
      #user_input = input()
      print e
      
      bad_count += 1
  
  print('Errors in: ' + str(bad_count) + ' registers of: ' + str(len(rows)))

def parse_register_str(register_str):
  tokens = register_str.split(' ')

  if '\n' in register_str:
    raise Exception('Register contains breakline, should be a line')
    print('Here!!!!')

  if len(tokens) < 3:
    raise Exception('Insuficient tokens at register: ' + register_str)
  
  register_id = get_register_id(tokens)

  index_id = len(tokens[0]) + len(tokens[1]) + 1
  name = register_str[index_id:].strip()
  name = name.replace(',', '.')

  if ONLY_UPPERCASE_DOTS.match(name) == None:
    raise Exception('Invalid name: ' + name)

  return { 'id' : register_id, 'name' : name }

def get_register_id(tokens):

  # Get and validate id
  letters_id = tokens[0]
  numbers_id = tokens[1]

  if (ONLY_UPPERCASE_LETTERS.match(letters_id) == None) or (len(letters_id) < 2):
    raise Exception('Bad letters id: ' + letters_id)
  
  if ONLY_NUMBERS.match(numbers_id) == None:
    raise Exception('Bad numbers id: ' + numbers_id)
  
  return (letters_id, int(numbers_id))

def process_image(args):
  print('Processing file ' + args.input + '...')

  # Read image source
  print('Readed image source.')
  image_src = cv2.imread(args.input)
  if args.debug:
    show_scaled_image('source', image_src, IMAGE_SCALE)

  # Get binary image
  binary_image = binarize_image(image_src)
  if args.debug:
    show_scaled_image('binary', binary_image, IMAGE_SCALE)
  
  # Get rows
  rows = find_rows(binary_image, args)
  if args.debug:
    boxes_img = draw_boxes(binary_image, rows, (0, 255, 0))
    show_scaled_image('rows', boxes_img, IMAGE_SCALE)
  
  # Process rows
  process_rows(binary_image, rows, args)

# Main script
def main():

  # Config parser
  parser = argparse.ArgumentParser(description='Digitalization of Annuary-part from Francois-Xavier Guerra database.')
  parser.add_argument('-i', '--input', help='Input image file', required=True)
  parser.add_argument('-o', '--output', help='Output text file', default='output.txt')
  parser.add_argument('-d', '--debug', help='Debug parameter', action='store_true')

  args = parser.parse_args()
  process_image(args)

if __name__ == '__main__':
  pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'
  main()
