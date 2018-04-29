# Digitalization from Francoise Xavier Guerra Database.

This project contains the digitalization of the Francoise Xavier Guerra database in CSV format files.
The data was obtained scanning book pages with the OCR Tesseract library, preprocessed by computer vision algorithms, and the
CSV files was produces with a python script.

## CSV Files ##

The database in csv format can simply be downloaded here:

## Dependencies ##

To run this project you should have install this technologies:

* Python 2.7
* OpenCV
* Tesseract
* pytesseract

## Installation ##

Once dependencies are already installed, clone this repo and thats all.

## Usage ##

To run the annuary digitalization:

```bash
$ python annuary_ocr.py -i imageinput.jpg

```

To run and see the debug:

```bash
$ python annuary_ocr.py -i imageinput.jpg --debug

```

To see the status of the data:

```bash
$ python annuary_ocr.py --status

```
