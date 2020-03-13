# pyportal_risk_dice
Use with the board game Risk.
Select the number of Attack and Defend die, then Battle | Roll to see the results.
Works, but sometimes the wrong button is selected, seems like "bounce" on the touch screen.
Running CircuitPython 5.0.0 release on Adafruit PyPortal.

Uses these libraries from adafruit-circuitpython-bundle-5.x-mpy-20200307:

import time

import board

import busio

import random

import neopixel

import displayio

import adafruit_imageload

import adafruit_touchscreen

from adafruit_button import Button

from adafruit_pyportal import PyPortal

from adafruit_bitmap_font import bitmap_font

from adafruit_display_text.label import Label
