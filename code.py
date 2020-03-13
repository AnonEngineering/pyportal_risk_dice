# * ------------------------------------------------------------
# The Diceinator
# V. Sherry 2020
# A Pyportal project to roll dice for the Risk board game.
# * ------------------------------------------------------------
# * ------------------------------------------------------------
# "THE BEERWARE LICENSE" (Revision 42):
# Van Sherry wrote this code. As long as you retain this
# notice, you can do whatever you want with it. If we meet
# someday, and you think this code is worth it, you can
# buy me a beer in return.
# * ------------------------------------------------------------

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

# ------------- neopixel setup ------------- #
pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=1)
WHITE = 0xffffff
LITE_WHT = 0x404040
RED = 0xff0000
LITE_RED = 0x400000
GREEN = 0x00ff00
BLUE = 0x0000ff
BLACK = 0x000000

# Globals
att_wins = 0
def_wins = 0
att_num_die = 3
def_num_die = 2
red_dice_position = [1, 3, 5]
wht_dice_position = [2, 4]

# ------------- Sound Effects -------------- #
soundBeep = '/sounds/beep.wav'
soundRoll = '/sounds/Roll_Dice.wav'

# ------------- Display setup -------------- #
pyportal = PyPortal()
display = board.DISPLAY
display.rotation = 0    # or - display.rotation = 270

# Touchscreen setup
# Rotate 0:
screen_width = 320
screen_height = 240
ts = adafruit_touchscreen.Touchscreen(board.TOUCH_XL, board.TOUCH_XR,
                                      board.TOUCH_YD, board.TOUCH_YU,
                                      samples = 10,
                                      calibration=((5200, 59000), (5800, 57000)),
                                      size=(screen_width, screen_height))

# Rotate 270:
# screen_width = 240
# screen_height = 320
# ts = adafruit_touchscreen.Touchscreen(board.TOUCH_YD, board.TOUCH_YU,
#                                       board.TOUCH_XR, board.TOUCH_XL,
#                                       calibration=((5200, 59000), (5800, 57000)),
#                                       size=(screen_width, screen_height))

# ------------- Display Groups ------------- #
main = displayio.Group(max_size=15)        # Main display group
att_view = displayio.Group(max_size=5)     # Group for attack select objects
def_view = displayio.Group(max_size=5)     # Group for defend select objects
roll_view = displayio.Group(max_size=10)   # Group for roll view objects

# Load the red dice sheet (bitmap)
red_dice_sheet, palette = adafruit_imageload.load("/images/dice_red.bmp",
                                                bitmap=displayio.Bitmap,
                                                palette=displayio.Palette)

# Load the white dice sheet (bitmap)
wht_dice_sheet, palette = adafruit_imageload.load("/images/dice_white.bmp",
                                                bitmap=displayio.Bitmap,
                                                palette=displayio.Palette)

# ------------- Setup for Images ------------- #
# Display an image until the loop starts
pyportal.set_background('/images/risk_board1.bmp')
bg_group = displayio.Group(max_size=1)
main.append(bg_group)

# ------------- Font stuff ------------------- #
# Set the font and preload letters
font16 = bitmap_font.load_font("/fonts/Helvetica-Bold-16.bdf")
#font16 = bitmap_font.load_font("/fonts/Arial-16.bdf")
font24 = bitmap_font.load_font("/fonts/Arial-Bold-24.bdf")
font16.load_glyphs(b'abcdefghjiklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890- ()')
font24.load_glyphs(b'abcdefghjiklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890- ()')

# ------------- Button groups ---------------- #
buttons = []
att_buttons = []
def_buttons = []
roll_buttons = []

# ---------- Main view -----------------------------------------------------------------#
TABS_HEIGHT = 40
TABS_WIDTH = 104    # Leaves space between buttons
# TABS_WIDTH = int(screen_width/3)

# Main User Interface Buttons, three across top of screen
button_att_view = Button(x=2, y=10,
                      width=TABS_WIDTH, height=TABS_HEIGHT,
                      label="Att Sel", label_font=font16, label_color=0xFFFFFF,
                      fill_color=0xFF0000, outline_color=0x000000,
                      selected_fill=0x3a3a3a, selected_outline=0x2e2e2e,
                      style = Button.ROUNDRECT, selected_label=0x828282)
buttons.append(button_att_view)  # adding this button to the buttons group

button_def_view = Button(x=TABS_WIDTH + 4, y=10,
                      width=TABS_WIDTH+1, height=TABS_HEIGHT,
                      label="Def Sel", label_font=font16, label_color=0x000000,
                      fill_color=0xFFFFFF, outline_color=0x000000,
                      selected_fill=0x3a3a3a, selected_outline=0x2e2e2e,
                      style = Button.ROUNDRECT, selected_label=0x828282)
buttons.append(button_def_view)  # adding this button to the buttons group

button_roll_view = Button(x=TABS_WIDTH*2 + 7, y=10,
                      width=TABS_WIDTH, height=TABS_HEIGHT,
                      label="Battle !", label_font=font16, label_color=0xFFFFFF,
                      fill_color=0x1030F0, outline_color=0x000000,
                      selected_fill=0x3a3a3a, selected_outline=0x2e2e2e,
                      style = Button.ROUNDRECT, selected_label=0x828282)
buttons.append(button_roll_view)  # adding this button to the buttons group

# Add all of the main buttons to the main Group
for b in buttons:
    main.append(b.group)

# ---------- Attack select view --------------------------------------------------------#
att_label = Label(font16, text="Choose number of attackers", color=0xFFFFFF, max_glyphs=50)
att_label.x = 50
att_label.y = 80
att_view.append(att_label)

att_win_label = Label(font16, text="Attacker wins:% d" % att_wins, color=0xFFFFFF, max_glyphs=50)
att_win_label.x = 50
att_win_label.y = 130
roll_view.append(att_win_label)

# Make a button to change numer of attackers to 1
button_att_die1 = Button(x=60, y=110,
                     width=40, height=60,
                     label="DIE1", label_font=font16, label_color=0x000000,
                     fill_color=0x10C050, outline_color=0x000000)
att_buttons.append(button_att_die1)  # adding this button to the buttons group

# Make a button to change numer of attackers to 2
button_att_die2 = Button(x=140, y=110,
                      width=40, height=60,
                      label="DIE2", label_font=font16, label_color=0x000000,
                      fill_color=0x10C050, outline_color=0x000000)
att_buttons.append(button_att_die2)  # adding this button to the buttons group

# Make a button to change numer of attackers to 3
button_att_die3 = Button(x=220, y=110,
                      width=40, height=60,
                      label="DIE3", label_font=font16, label_color=0x000000,
                      fill_color=0x10C050, outline_color=0x000000)
att_buttons.append(button_att_die3)  # adding this button to the buttons group

# Add all of the att buttons to the att_view Group
for att in att_buttons:
    att_view.append(att.group)

# Create the att select red dice TileGrid
att_red_dice = displayio.TileGrid(red_dice_sheet, pixel_shader=palette,
                                x=20,  # Position relative to its parent group
                                y=120,
                                width = 7,  # Number of tiles in the grid
                                height = 1,
                                tile_width = 40,
                                tile_height = 40,
                                # tile_width=None,  # Number of tiles * tile size must match BMP size
                                # tile_height=None,  # None means auto size the tiles
                                default_tile = 0)

att_red_dice[1,0] = 1
att_red_dice[3,0] = 2
att_red_dice[5,0] = 3

att_view.append(att_red_dice)

# ---------- Def select view -----------------------------------------------------------#
def_label = Label(font16, text="Choose number of defenders", color=0xFFFFFF, max_glyphs=50)
def_label.x = 50
def_label.y = 80
def_view.append(def_label)

def_win_label = Label(font16, text="Defender wins:% d" % def_wins, color=0xFFFFFF, max_glyphs=50)
def_win_label.x = 50
def_win_label.y = 210
roll_view.append(def_win_label)

# Make a button to change number of defenders to 1
button_def_die1 = Button(x=100, y=110,
                      width=40, height=60,
                      label="DIE1", label_font=font16, label_color=0x000000,
                      fill_color=0x10C050, outline_color=0x000000)
def_buttons.append(button_def_die1)  # adding this button to the buttons group

# Make a button to change number of defenders to 2
button_def_die2 = Button(x=180, y=110,
                      width=40, height=60,
                      label="DIE2", label_font=font16, label_color=0x000000,
                      fill_color=0x10C050, outline_color=0x000000)
def_buttons.append(button_def_die2)  # adding this button to the buttons group

# Add all of the def buttons to the def_view Group
for defend in def_buttons:
    def_view.append(defend.group)

# Create the white dice TileGrid
def_wht_dice = displayio.TileGrid(wht_dice_sheet, pixel_shader=palette,
                                x=20,  # Position relative to its parent group
                                y=120,
                                width = 7,  # Number of tiles in the grid
                                height = 1,
                                tile_width = 40,
                                tile_height = 40,
                                # tile_width=None,  # Number of tiles * tile size must match BMP size
                                # tile_height=None,  # None means auto size the tiles
                                default_tile = 0)

def_wht_dice[2,0] = 1
def_wht_dice[4,0] = 2

def_view.append(def_wht_dice)

# ---------- Roll view -----------------------------------------------------------------#
# Make a button to roll dice
btn_roll_dice = Button(x=255, y=80,
                    width=50, height=100,
                    label="Roll", label_font=font16, label_color=0x000000,
                    fill_color=0x10A0F0, outline_color=0x000000,
                    style=Button.ROUNDRECT)
roll_buttons.append(btn_roll_dice)  # add this button to the buttons group

# Create the roll red dice TileGrid
red_dice = displayio.TileGrid(red_dice_sheet, pixel_shader=palette,
                                x=-15,  # Position relative to its parent group
                                y=70,
                                width = 7,  # Number of tiles in the grid
                                height = 1,
                                tile_width = 40,
                                tile_height = 40,
                                # tile_width=None,  # Number of tiles * tile size must match BMP size
                                # tile_height=None,  # None means auto size the tiles
                                default_tile = 0)

red_dice[1,0] = 1
red_dice[3,0] = 2
red_dice[5,0] = 3

roll_view.append(red_dice)

# Create the roll white dice TileGrid
wht_dice = displayio.TileGrid(wht_dice_sheet, pixel_shader=palette,
                                x=-15,  # Position relative to its parent group
                                y=150,
                                width = 7,  # Number of tiles in the grid
                                height = 1,
                                tile_width = 40,
                                tile_height = 40,
                                # tile_width=None,  # Number of tiles * tile size must match BMP size
                                # tile_height=None,  # None means auto size the tiles
                                default_tile = 0)

wht_dice[2,0] = 1
wht_dice[4,0] = 2

roll_view.append(wht_dice)

# Append the roll button on top
for r in roll_buttons:
    roll_view.append(r.group)

# ------------- Functions ------------------------------------------------------------- #
# Backlight function, 0 - 1
def set_backlight(val):
    val = max(0, min(1.0, val))
    board.DISPLAY.auto_brightness = False
    board.DISPLAY.brightness = val

# Hide layer function
def hideLayer(hide_target):
    try:
        main.remove(hide_target)
    except ValueError:
        pass

# Show layer function
def showLayer(show_target):
    try:
        time.sleep(0.1)
        main.append(show_target)
    except ValueError:
        pass

# Function to sort the list by i item of tuple
def Sort_Tuple(tup):
    # Small anonymous function <lambda x> determines key
    # key is set to sort using x[i] element of
    # supplied tuple
    # reverse = False is default (Sorts in Ascending order)
    return(sorted(tup, key = lambda x: x[0], reverse = True))

# Roll dice function
def roll_dice(att_num_die, def_num_die):
    global red_dice_position
    global wht_dice_position
    global att_wins
    global def_wins
    att_tup = []
    def_tup = []
    att_label = ''
    def_label = ''

    def_win_label.text = ("Defender wins: -")
    att_win_label.text = ("Attacker wins: -")
    pyportal.play_file(soundRoll)

    for num in range(att_num_die):
        rand_num = random.randint(1, 6)
        red_dice[red_dice_position[num], 0] = rand_num
        attack_tuple = ((rand_num,) + (num,),)
        att_tup += (attack_tuple)

    att_sort_tup = Sort_Tuple(att_tup)
    #print(att_sort_tup)
    att_hiDice = att_sort_tup[0]

    for num in range(def_num_die):
        rand_num = random.randint(1, 6)
        wht_dice[wht_dice_position[num], 0] = rand_num
        defend_tuple = ((rand_num,) + (num,),)
        def_tup += (defend_tuple)

    def_sort_tup = Sort_Tuple(def_tup)
    def_hiDice = def_sort_tup[0]

    if (def_hiDice[0] >= att_hiDice[0]):
        def_wins += 1
        #def_win_label.text = "Defender wins: " + str(def_wins)
        def_label = "Defender wins: " + str(def_wins)
        blink_color = WHITE

    if (att_hiDice[0] > def_hiDice[0]):
        att_wins += 1
        #att_win_label.text = "Attacker wins: " + str(att_wins)
        att_label = "Attacker wins: " + str(att_wins)
        blink_color = RED

    time.sleep(1)
    blinkDie(att_hiDice[0], def_hiDice[0], att_hiDice[1], def_hiDice[1], blink_color)
    def_win_label.text = def_label
    att_win_label.text = att_label

    if att_num_die > 1 and def_num_die > 1:
        att_loDice = att_sort_tup[1]
        def_loDice = def_sort_tup[1]
        if (def_loDice[0] >= att_loDice[0]):
            def_wins += 1
            #def_win_label.text = "Defender wins: " + str(def_wins)
            def_label = "Defender wins: " + str(def_wins)
            blink_color = WHITE

        if (att_loDice[0] > def_loDice[0]):
            att_wins += 1
            #att_win_label.text = "Attacker wins: " + str(att_wins)
            att_label = "Attacker wins: " + str(att_wins)
            blink_color = RED

        time.sleep(1)
        blinkDie(att_loDice[0], def_loDice[0], att_loDice[1], def_loDice[1], blink_color)
        def_win_label.text = def_label
        att_win_label.text = att_label

# Blink winners function
def blinkDie(att_val, def_val, att_pos, def_pos, blink_color):

    for i in range(3):
        red_dice[red_dice_position[att_pos], 0] = 0
        wht_dice[wht_dice_position[def_pos], 0] = 0
        pixel.fill(BLACK)
        time.sleep(.5)
        red_dice[red_dice_position[att_pos], 0] = att_val
        wht_dice[wht_dice_position[def_pos], 0] = def_val
        pixel.fill(blink_color)
        time.sleep(.5)

    pixel.fill(BLUE)

# This handles switching Images and Icons
def set_image(group, filename):
    """Set the image file for a given goup for display.
    This is most useful for Icons or image slideshows.
        :param group: The chosen group
        :param filename: The filename of the chosen image
    """
    # print("Set image to ", filename)
    if group:
        group.pop()

    if not filename:
        return  # we're done, no icon desired

    image_file = open(filename, "rb")
    image = displayio.OnDiskBitmap(image_file)
    try:
        image_sprite = displayio.TileGrid(image, pixel_shader=displayio.ColorConverter())
    except TypeError:
        image_sprite = displayio.TileGrid(image, pixel_shader=displayio.ColorConverter(),
                                          position=(0, 0))
    group.append(image_sprite)

# View switching function
#pylint: disable=global-statement
def switch_view(what_view):
    global view_live
    if what_view == 1:
        pixel.fill(LITE_RED)
        hideLayer(def_view)
        hideLayer(roll_view)
        button_att_view.selected = False
        button_def_view.selected = True
        button_roll_view.selected = True
        showLayer(att_view)
        view_live = 1
        print("Att View On")
        print()
    elif what_view == 2:
        pixel.fill(LITE_WHT)
        hideLayer(att_view)
        hideLayer(roll_view)
        button_att_view.selected = True
        button_def_view.selected = False
        button_roll_view.selected = True
        showLayer(def_view)
        view_live = 2
        print("Def View On")
        print()
    #else:
    elif what_view == 3:
        def_win_label.text = ("Defender wins: -")
        att_win_label.text = ("Attacker wins: -")
        pixel.fill(BLUE)
        hideLayer(att_view)
        hideLayer(def_view)
        button_att_view.selected = True
        button_def_view.selected = True
        button_roll_view.selected = False
        showLayer(roll_view)
        view_live = 3
        print("Roll View On")
        print()
#pylint: enable=global-statement

#----------- End functions -------------------------------------------------------------#

# Set variables and startup states
# Set the background
set_image(bg_group, "/images/bg_green.bmp")
# Set the Backlight
set_backlight(0.75)
# Init the view_live variable
view_live = 1
# Set neopixel to lite red
pixel.fill(LITE_RED)
# Set up buttons
button_att_view.selected = False
button_def_view.selected = True
button_roll_view.selected = True
# Set up layers
showLayer(att_view)
print('Att view initialized')
print()
hideLayer(def_view)
hideLayer(roll_view)
# Come out of splash screen
board.DISPLAY.show(main)

# ------------- Code Loop ------------- #
while True:

    touch = ts.touch_point
    #while ts.touch_point:  # for debounce
        #time.sleep(.5)
        #pass

    # ------------- Handle Button Press Detection  ------------- #
    if touch:  # Only do this if the screen is touched
        print("Touch" + str(touch))
        #time.sleep(.5)
        # loop with buttons using enumerate() to number each button group as i
        for i, b in enumerate(buttons):
            if b.contains(touch):  # Test each button to see if it was pressed
                print('Main button% d pressed' % i)
                if i == 0 and view_live != 1:  # only if att_view is visible
                    pyportal.play_file(soundBeep)
                    switch_view(1)
                    while ts.touch_point:  # for debounce
                        time.sleep(.1)
                        pass
                if i == 1 and view_live != 2:  # only if def_view is visible
                    pyportal.play_file(soundBeep)
                    switch_view(2)
                    while ts.touch_point:
                        time.sleep(.1)
                        pass
                if i == 2 and view_live != 3:  # only if roll_view is visible
                    pyportal.play_file(soundBeep)
                    switch_view(3)
                    while ts.touch_point:
                        time.sleep(.1)
                        pass
                    if att_num_die == 1:
                        red_dice[1,0] = 1
                        red_dice[3,0] = 0
                        red_dice[5,0] = 0
                    elif att_num_die == 2:
                        red_dice[1,0] = 1
                        red_dice[3,0] = 2
                        red_dice[5,0] = 0
                    else:
                        red_dice[1,0] = 1
                        red_dice[3,0] = 2
                        red_dice[5,0] = 3

                    if def_num_die == 1:
                        wht_dice[2,0] = 1
                        wht_dice[4,0] = 0
                    else:
                        wht_dice[2,0] = 1
                        wht_dice[4,0] = 2

        for j, att in enumerate(att_buttons):
            if att.contains(touch):  # Test each button to see if it was pressed
                #switch_view(1)
                print('Att select% d pressed' % j)
                if j == 0 and view_live == 1:  # only if att_view is visible:
                    #att.selected = True
                    while ts.touch_point:
                        time.sleep(.1)
                        pass
                    att_red_dice[1, 0] = 1
                    att_red_dice[3, 0] = 0
                    att_red_dice[5, 0] = 0
                    att_num_die = 1
                if j == 1 and view_live == 1:  # only if att_view is visible:
                    #att.selected = True
                    while ts.touch_point:
                        time.sleep(.1)
                        pass
                    att_red_dice[1, 0] = 0
                    att_red_dice[3, 0] = 2
                    att_red_dice[5, 0] = 0
                    att_num_die = 2
                if j == 2 and view_live == 1:  # only if att_view is visible:
                    #att.selected = True
                    while ts.touch_point:
                        time.sleep(.1)
                        pass
                    att_red_dice[1, 0] = 0
                    att_red_dice[3, 0] = 0
                    att_red_dice[5, 0] = 3
                    att_num_die = 3

        for k, defend in enumerate(def_buttons):
            if defend.contains(touch):  # Test each button to see if it was pressed
                print('Def select% d pressed' % k)
                if k == 0 and view_live == 2:  # only if def_view is visible:
                    while ts.touch_point:
                        time.sleep(.1)
                        pass
                    def_wht_dice[2, 0] = 1
                    def_wht_dice[4, 0] = 0
                    def_num_die = 1
                if k == 1 and view_live == 2:  # only if def_view is visible:
                    while ts.touch_point:
                        time.sleep(.1)
                        pass
                    def_wht_dice[2, 0] = 0
                    def_wht_dice[4, 0] = 2
                    def_num_die = 2

        for m, roll in enumerate(roll_buttons):
            if roll.contains(touch):  # Test each button to see if it was pressed
                print("Roll button pressed")
                if m == 0 and view_live == 3:  # only if roll_view is visible:
                    while ts.touch_point:
                        time.sleep(.1)
                        pass
                    print('Number of attackers% d' % att_num_die)
                    print('Number of defenders% d' % def_num_die)
                    roll_dice(att_num_die,def_num_die)
                    att_wins = 0
                    def_wins = 0
                    att_tup = []
                    def_tup = []

        #touch = (0, 0, 0)
        #time.sleep(0.5)