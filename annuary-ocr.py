import cv2
import numpy as np
import pytesseract

def binary_image (image_src):

  gray = cv2.cvtColor(image_src, cv2.COLOR_BGR2GRAY)
  ret, binary = cv2.threshold(gray, 70, 255, cv2.THRESH_BINARY_INV)

  kernel = np.ones((2, 2), np.uint8)
  binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

  return binary


def find_columns(binary_image):

  kernel = np.ones((30, 10), np.uint8)
  img_dilation = cv2.dilate(binary_image, kernel, iterations=1)
  
  im2, contours, hierarchy = cv2.findContours(img_dilation.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

  columns = []
  for contour in contours:

    area = cv2.contourArea(contour)
    x, y, w, h = cv2.boundingRect(contour)

    if (area > 4000) and is_valid_column(x, y, w, h):
      columns.append((x, y, w, h))
  
  return columns

def find_rows(binary_image):

  kernel = np.ones((1, 80), np.uint8)
  img_dilation = cv2.dilate(binary_image, kernel, iterations=1)

  #cv2.imshow('dilation', img_dilation)
  #cv2.waitKey(0)

  im2, contours, hierarchy = cv2.findContours(img_dilation.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

  rows = []
  for contour in contours:

    area = cv2.contourArea(contour)
    x, y, w, h = cv2.boundingRect(contour)

    if (area > 1000):
      rows.append((x, y, w, h))

  return rows

def clean_columns(columns):

  cleaned = []

  for column_a in columns:
    inside = False

    for column_b in columns:
      if column_a != column_b:
        inside = is_inside(column_a, column_b) or inside
    
    if inside:
      cleaned.append(column_a)
  
  return cleaned

def clean_rows(rows, columns):

  clean = []

  for i, row in enumerate(rows):
    intersections = []

    for j, column in enumerate(columns):
      if are_instersected(row, column):
        intersections.append(column)
    
    if len(intersections) > 0:
      clean.append(row)
  
  return clean
    
def is_valid_column(x, y, w, h):
  ratio = w / h

  return (ratio < 1.0) and (w > 30)

def draw_boxes(boxes, stroke, image):

  for box in boxes:
    x, y, w, h = box
    cv2.rectangle(image, (x, y), (x + w, y + h), stroke, 1)

def is_inside(box_a, box_b):
  x_a, y_a, w_a, h_a = box_a
  x_b, y_b, w_b, h_b = box_b

  inside_x = (x_b <= x_a) and ((x_b + w_b) >= (x_a + w_a))
  inside_y = (y_b <= y_a) and ((y_b + h_b) >= (y_a + h_a))

  return inside_x and inside_y

def are_instersected(box_a, box_b):
  x_a, y_a, w_a, h_a = box_a
  x_b, y_b, w_b, h_b = box_b

  test_axis_x = (abs(x_a - x_b) * 2) <= (w_a + w_b)
  test_axis_y = (abs(y_a - y_b) * 2) <= (h_a + h_b)

  return test_axis_x and test_axis_y

# Main script

def main():
  for i in range(1, 2):
    image_src = cv2.imread('images/annuary/BaseGuerra000' + str(i) + '.jpg')
    image_src = image_src[0:3200, 0:2550]

    binary = binary_image(image_src)

    columns = find_columns(binary)
    #columns = clean_columns(columns)

    if len(columns) != 18:
      print('En la ' + str(i) + ' no hay todas las columnas')
      print(len(columns))

    rows = find_rows(binary)
    #rows = clean_rows(rows, columns)

    draw_boxes(columns, (0, 0, 255), image_src)
    draw_boxes(rows, (255, 0, 0), image_src)

  #cv2.imshow('result', image_src)
  cv2.imwrite('output' + str(i) + '.png', image_src)
  #cv2.waitKey(0)

  print('Done ' + str(i))

main()