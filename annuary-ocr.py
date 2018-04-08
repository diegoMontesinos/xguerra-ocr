#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cv2
import numpy as np
import pytesseract
import io

def binarize_image(image_src):

  gray = cv2.cvtColor(image_src, cv2.COLOR_BGR2GRAY)
  ret, binary = cv2.threshold(gray, 70, 255, cv2.THRESH_BINARY_INV)

  return binary

def find_columns(binary_image):

  kernel_closing = np.ones((13, 13), np.uint8)
  image_closing = cv2.morphologyEx(binary_image, cv2.MORPH_CLOSE, kernel_closing)

  kernel_dilation = np.ones((30, 7), np.uint8)
  image_dilation = cv2.dilate(image_closing, kernel_dilation, iterations=1)

  im2, contours, hierarchy = cv2.findContours(image_dilation.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

  columns = []
  for contour in contours:

    area = cv2.contourArea(contour)
    x, y, w, h = cv2.boundingRect(contour)

    if (area > 4000) and is_valid_column(x, y, w, h):
      columns.append((x, y, w, h))

  return columns

def find_rows(binary_image):

  kernel_dilation = np.ones((1, 10), np.uint8)
  image_dilation = cv2.dilate(binary_image, kernel_dilation, iterations=1)

  #cv2.imwrite('output/dilation-rows.png', image_dilation)

  kernel_closing = np.ones((1, 66), np.uint8)
  image_closing = cv2.morphologyEx(image_dilation, cv2.MORPH_CLOSE, kernel_closing)

  #cv2.imwrite('output/closing.png', image_closing)

  im2, contours, hierarchy = cv2.findContours(image_closing.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

  rows = []
  for contour in contours:

    area = cv2.contourArea(contour)
    x, y, w, h = cv2.boundingRect(contour)

    if (area > 1000) and (h < 30):
      rows.append((x, y, w, h))

  return rows

def is_valid_column(x, y, w, h):
  ratio = w / h

  return (ratio < 1.0) and (w > 30)

def draw_boxes(boxes, stroke, image):

  for box in boxes:
    x, y, w, h = box
    cv2.rectangle(image, (x, y), (x + w, y + h), stroke, 1)

def get_registers(image_url):

  # Load and crop image
  image_src = cv2.imread(image_url)
  image_src = image_src[0:3200, 0:2550]

  cv2.imwrite('source.png', image_src)

  binary_image = binarize_image(image_src)

  cv2.imwrite('binary.png', binary_image)
  
  height, width = binary_image.shape[:2]
  M = cv2.getRotationMatrix2D((width/2,height/2), 1.1, 1)
  binary_image = cv2.warpAffine(binary_image, M, (width,height))

  cv2.imwrite('binary-rotated.png', binary_image)

  # Get columns and rows
  columns = find_columns(binary_image)
  rows = find_rows(binary_image)

  draw_boxes(columns, (0, 0, 255), image_src)
  cv2.imwrite('output/columns.png', image_src)

  draw_boxes(rows, (255, 0, 0), image_src)
  cv2.imwrite('output/rows.png', image_src)

  f = open('output.txt', 'wb')
  for i, row in enumerate(rows):
    x, y, w, h = row
    
    roi = binary_image[y:y+h, x:x+w]

    #cv2.imwrite('output/row' + str(i) + '.png', roi)

    text = pytesseract.image_to_string(roi)
    f.write(text.encode('utf-8'))
    f.write('\n'.encode('utf-8'))

    print('readed ' + str(i))
  
  f.close()

# Main script
def main():
  pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'

  registers = get_registers('images/annuary/BaseGuerra0009.jpg')

if __name__ == '__main__':
  main()
