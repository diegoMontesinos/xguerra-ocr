# -*- coding: utf-8 -*-

import numpy as np
import cv2
from ..utils import *

COL_WIDTH = 1040
MIN_COL_HEIGHT = 1000
MIN_SEPARATION_OFFSET = 4
MIN_SEPARATION_AREA = 100
CONTENT_OFFSET = 253
MIN_CONTENT_ROW_HEIGHT = 15
MIN_CONTENT_ROW_AREA = 2300
MIN_CHAR_AREA = 4
MAX_CHAR_WIDTH = 29
AVG_CHAR_WIDTH = 21
AVG_SPACE_WIDTH = 23

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
  contours = cv2.findContours(image_close, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[1]

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
  contours = cv2.findContours(image_dilation, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[1]
  contours = [cnt for cnt in contours if cv2.contourArea(cnt) >= 2000]

  if debug:
    contours_img = draw_contours(img_col, contours)
    show_scaled_image('contours blocks', contours_img, 0.4)

  # Get rows separation as leftmost bounding boxes
  separation_rows = map(cv2.boundingRect, contours)
  separation_rows = [row for row in separation_rows if is_separation_diary_row(row)]
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
    content_y = y + h
    content_height = next_y - content_y - 2
    
    if content_height > 25:
      content = (CONTENT_OFFSET, content_y, width - CONTENT_OFFSET, content_height)
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

def find_diary_content_modules(content_img, debug):
  modules = []

  rows = find_diary_content_rows(content_img, debug)
  for row in rows:
    content_row_img = crop_roi(content_img, row)
    row_modules = get_modules_on_content_row(content_row_img, row, debug)
    modules.append(row_modules)
  
  return modules

def find_diary_content_rows(content_img, debug):

  # Remove noise
  kernel_open = np.ones((2, 3), np.uint8)
  image_open = cv2.morphologyEx(content_img, cv2.MORPH_OPEN, kernel_open)

  # Close image
  width = content_img.shape[1]
  kernel_close = np.ones((5, width), np.uint8)
  image_close = cv2.morphologyEx(image_open, cv2.MORPH_CLOSE, kernel_close)

  # Find contours and filter
  contours = cv2.findContours(image_close, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[1]
  contours = [cnt for cnt in contours if is_valid_content_row(cnt)]

  rows = []
  for cnt in contours:
    x, y, w, h = cv2.boundingRect(cnt)
    rows.append((max(x - 2, 0), max(y - 2, 0), width - x, h + 2))

  rows.sort(key=lambda row:row[1])

  return rows

def is_valid_content_row(cnt):
  x, y, w, h = cv2.boundingRect(cnt)
  return (x < 50) and (h >= MIN_CONTENT_ROW_HEIGHT) and ((w * h) > MIN_CONTENT_ROW_AREA)

def get_modules_on_content_row(content_row_img, offset, debug):

  # Find chars contours
  kernel_close = np.ones((5, 4), np.uint8)
  image_close = cv2.morphologyEx(content_row_img, cv2.MORPH_CLOSE, kernel_close)

  contours = cv2.findContours(image_close, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[1]
  contours = [cnt for cnt in contours if cv2.contourArea(cnt) > MIN_CHAR_AREA]

  # Get bounding boxes, filter and sort
  rects = map(get_bounding_rect_char(content_row_img.shape[0]), contours)
  rects = [rect for rect in rects if not is_rect_inside_another(rect, rects)]
  rects.sort(key=lambda rect:rect[0])
  rects = merge_overlays_and_brokens(rects)

  return get_modules_from_rects(content_row_img, offset, rects)

def get_bounding_rect_char(height):
  def bounding_rect_char(cnt):
    x, y, w, h = cv2.boundingRect(cnt)
    return (max(x - 3, 0), 0, w + 2, height - 1)

  return bounding_rect_char

def is_rect_inside_another(rect, rects):
  x_a, y_a, w_a, h_a = rect

  for another_rect in rects:
    x_b, y_b, w_b, h_b = another_rect
    range_x = range(x_b, x_b + w_b)

    if (x_a in range_x) and ((x_a + w_a) in range_x):
      return True

  return False

def merge_overlays_and_brokens(rects):

  merged_rects = []

  current = None
  for rect in rects:
    if not current:
      current = rect
      continue
    
    if are_rects_overlaped(current, rect):
      current = merge_rects(current, rect)
      continue
    
    curr_w = current[2]
    x_space = rect[0] - (current[0] + curr_w)
    if (curr_w < 14) and (x_space <= 6):
      current = merge_rects(current, rect)
      continue

    merged_rects.append(current)
    current = rect
  
  merged_rects.append(current)
  
  return merged_rects

def are_rects_overlaped(rect_a, rect_b):
  range_x = range(rect_a[0], rect_a[0] + rect_a[2])

  return (rect_b[0] in range_x) or ((rect_b[0] + rect_b[2]) in range_x)

def merge_rects(rect_a, rect_b):
  x_a, y_a, w_a, h_a = rect_a
  stop_b = rect_b[0] + rect_b[2]

  return (x_a, y_a, stop_b - x_a, h_a)

def get_modules_from_rects(content_row_img, offset, rects):

  modules = []

  # Process char rects
  last_x = None
  for rect in rects:
    x, y, w, h = rect

    # Put num of spaces between last rect into modules
    x_space = 0 if not last_x else (x - last_x)
    last_x = (x + w)
    num_spaces = 0 if x_space <= AVG_SPACE_WIDTH else int(x_space / AVG_SPACE_WIDTH)

    if num_spaces > 0:
      modules.append((num_spaces, None))

    # Put num of chars in rect into modules
    num_chars = 1
    if w > MAX_CHAR_WIDTH:
      num_chars = int(w / AVG_CHAR_WIDTH)
    
    modules.append((num_chars, (x + offset[0], y + offset[1], w, h)))

  return modules
