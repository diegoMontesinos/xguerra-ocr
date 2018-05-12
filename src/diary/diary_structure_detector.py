# -*- coding: utf-8 -*-

import numpy as np
import cv2
from ..utils import *

COL_WIDTH = 1040
MIN_COL_HEIGHT = 1000
MIN_SEPARATION_OFFSET = 4
MIN_SEPARATION_AREA = 100
CONTENT_OFFSET = 253

def find_columns_on_diary(binary_image, debug):

  # Remove noise
  kernel_open = np.ones((3, 3),np.uint8)
  image_open = cv2.morphologyEx(binary_image, cv2.MORPH_OPEN, kernel_open)

  # Close image
  kernel_close = np.ones((40, 85), np.uint8)
  image_close = cv2.morphologyEx(image_open, cv2.MORPH_CLOSE, kernel_close)

  if debug:
    show_scaled_image('cols dilation', image_close, 0.4)

  # Find contours
  im2, contours, hierarchy = cv2.findContours(image_close, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

  if debug:
    contours_img = draw_contours(binary_image, contours)
    show_scaled_image('contours cols', contours_img, 0.4)
  
  # Get bounding boxes as detected columns
  detected_cols = []
  for contour in contours:
    col = cv2.boundingRect(contour)

    if is_valid_diary_col(col):
      detected_cols.append(col)
  
  # Sort by x and y
  detected_cols.sort(key=lambda col: col[0])
  detected_cols.sort(key=lambda col: col[1])

  # Get first and second in x-order and create cols
  first = detected_cols[0]
  second = detected_cols[1]

  height, width = binary_image.shape[:2]

  cols = get_columns_from(first, width)
  cols += get_columns_from(second, width)

  if debug:
    boxes_img = draw_boxes(binary_image, cols, (0, 255, 0))
    show_scaled_image('cols', boxes_img, 0.4)

  return cols

def is_valid_diary_col(col):
  w = col[2]
  h = col[3]

  return (h > MIN_COL_HEIGHT) and (w > (COL_WIDTH * 2))

def get_columns_from(col, width):
  x, y, w, h = col

  cols = [
    (x, y, COL_WIDTH, h),
    (x + COL_WIDTH, y, COL_WIDTH, h),
    (x + (2 * COL_WIDTH), y, width - (x + (2 * COL_WIDTH)), h)
  ]
  
  return cols

def find_blocks_on_diary_col(img_col, debug):

  # Remove noise
  kernel_open = np.ones((3, 3), np.uint8)
  image_open = cv2.morphologyEx(img_col, cv2.MORPH_OPEN, kernel_open)

  # Close image
  kernel_close = np.ones((2, 200), np.uint8)
  image_dilation = cv2.morphologyEx(image_open, cv2.MORPH_CLOSE, kernel_close)

  if debug:
    show_scaled_image('blocks dilation', image_dilation, 0.4)
  
  # Find contours
  im2, contours, hierarchy = cv2.findContours(image_dilation, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

  if debug:
    contours_img = draw_contours(img_col, contours)
    show_scaled_image('contours blocks', contours_img, 0.4)

  # Get rows separation as leftmost bounding boxes
  separation_rows = []
  for contour in contours:
    area = cv2.contourArea(contour)
    if area < 2000:
      continue

    row = cv2.boundingRect(contour)

    if is_separation_diary_row(row):
      separation_rows.append(row)
    
  # Sort by y
  separation_rows.sort(key=lambda row: row[1])
  
  height, width = img_col.shape[:2]

  # Build blocks
  headers = []
  contents = []
  blocks = []

  n = len(separation_rows)
  for i in range(0, n):
    
    x, y, w, h = separation_rows[i]

    next_y = height if (i == (n - 1)) else separation_rows[i + 1][1]

    # Create header
    header = (x, y, width, h)
    headers.append(header)

    # Create content
    content_height = next_y - (y + h) - 4
    if content_height > 25:
      content = (CONTENT_OFFSET, y + h, width - CONTENT_OFFSET, content_height)
      contents.append(content)
    else:
      content = None
    
    # Diary block: header + content
    blocks.append([ header, content ])
  
  if debug:
    boxes_img = draw_boxes(img_col, contents, (0, 0, 255))
    boxes_img = draw_boxes(boxes_img, headers, (0, 255, 0))
    show_scaled_image('blocks', boxes_img, 0.4)

  return blocks

def is_separation_diary_row(row):
  x = row[0]
  area = row[2] * row[3]

  return (x < MIN_SEPARATION_OFFSET) and (area > MIN_SEPARATION_AREA)