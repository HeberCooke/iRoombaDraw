#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 27 May 2015

###########################################################################
# Copyright (c) 2015 iRobot Corporation
# http://www.irobot.com/
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#   Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
#
#   Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in
#   the documentation and/or other materials provided with the
#   distribution.
#
#   Neither the name of iRobot Corporation nor the names
#   of its contributors may be used to endorse or promote products
#   derived from this software without specific prior written
#   permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
###########################################################################

from Tkinter import *
import tkMessageBox
import tkSimpleDialog
# For the pie
import RPi.GPIO as GPIO

import struct
import sys
import glob  # for listing serial ports
import time
import random
# setting up the pins for the raspberry pie
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT)
servo = GPIO.PWM(11, 50)
servo.start(0)


try:

    import serial
except ImportError:
    tkMessageBox.showerror('Import error', 'Please install pyserial.')
    raise

connection = None

TEXTHEIGHT = 16  # window height, in lines
TEXTWIDTH = 60

VELOCITYCHANGE = 200
ROTATIONCHANGE = 300

helpText = """\
Supported Keys:
P\tPassive
S\tSafe
F\tFull
C\tClean
D\tDock
R\tReset
2\tSong #2
3\tSong #3
Arrows\tMotion
If nothing happens after you connect, try pressing 'P' and then 'S' to get into safe mode.
"""


class TetheredDriveApp(Tk):
    # static variables for keyboard callback -- I know, this is icky
    callbackKeyUp = False
    callbackKeyDown = False
    callbackKeyLeft = False
    callbackKeyRight = False
    callbackKeyLastDriveCommand = ''

    global penUp

    def penUp():
        servo.ChangeDutyCycle(3)
        time.sleep(.3)
        servo.ChangeDutyCycle(0)
    global penDown

    def penDown():
        servo.ChangeDutyCycle(4.3)
        time.sleep(.3)
        servo.ChangeDutyCycle(0)

    def __init__(self):

        Tk.__init__(self)
        self.title("iRobot Create 2 Tethered Drive")
        self.option_add('*tearOff', FALSE)

        self.menubar = Menu()
        self.configure(menu=self.menubar)

        createMenu = Menu(self.menubar, tearoff=False)
        self.menubar.add_cascade(label="Create", menu=createMenu)

        createMenu.add_command(label="Connect", command=self.onConnect)
        createMenu.add_command(label="Help", command=self.onHelp)
        createMenu.add_command(label="Quit", command=self.onQuit)

        self.text = Text(self, height=TEXTHEIGHT, width=TEXTWIDTH, wrap=WORD)
        self.scroll = Scrollbar(self, command=self.text.yview)
        self.text.configure(yscrollcommand=self.scroll.set)
        self.text.pack(side=LEFT, fill=BOTH, expand=True)
        self.scroll.pack(side=RIGHT, fill=Y)

        self.text.insert(END, helpText)

        self.bind("<Key>", self.callbackKey)
        self.bind("<KeyRelease>", self.callbackKey)
        global penUp
        penUp()
    # sendCommandASCII takes a string of whitespace-separated, ASCII-encoded base 10 values to send

    def sendCommandASCII(self, command):
        cmd = ""
        for v in command.split():
            cmd += chr(int(v))

        self.sendCommandRaw(cmd)

    # sendCommandRaw takes a string interpreted as a byte array
    def sendCommandRaw(self, command):
        global connection

        try:
            if connection is not None:
                connection.write(command)
            else:
                tkMessageBox.showerror(
                    'Not connected!', 'Not connected to a robot!')
                print "Not connected."
        except serial.SerialException:
            print "Lost connection"
            tkMessageBox.showinfo('Uh-oh', "Lost connection to the robot!")
            connection = None

        # print ' '.join([ str(ord(c)) for c in command ])
        self.text.insert(END, ' '.join([str(ord(c)) for c in command]))
        self.text.insert(END, '\n')
        self.text.see(END)
    # ---------------------------------------------------------------Draw----------------

    # Explanation:
    # Desired value -> two’s complement and convert to hex -> split into 2 bytes -> convert to decimal
    # Velocity = -200 = 0xFF38 = [0xFF][0x38] = [255][56]
    # Radius = 500 = 0x01F4 = [0x01][0xF4] = [1][244]
    
    
    # Move is to move the pen
    global move
    def move(self):

        time.sleep(1)
        servo.ChangeDutyCycle(15)
        time.sleep(1)
        servo.ChangeDutyCycle(0)

    # This method splits the number and takes the 16 bit
    # value and returns a string
    # representation of the number
    global splitBits
    def splitBits(number):
        n1 = number >> 8
        n2 = number % 256
        if n1 < 0:
            n1 = 255
        return str(n1) + ' ' + str(n2)
# ---------------------------------------Circle--------------------------------
    global circle

    def circle(self):
        global penUp
        global penDown
        global splitBits
        
        randomDifference = random.randint(8,16)
        penDown()
      
        cmd = '145' + ' '+ splitBits(20) + ' '+ splitBits(-20)
        self.sendCommandASCII(cmd)
        time.sleep(18)
        self.sendCommandASCII('145 0 0 0 0')  

        penUp()
        cmd = '145' + ' '+ splitBits(-15)+' '+ splitBits(-15)
        self.sendCommandASCII(cmd)
        time.sleep(2.6)
        self.sendCommandASCII('145 0 0 0 0')
        penUp()
        time.sleep(2)
        draw(self)
    # -----------------------------------------------DRAW-----------
    global draw

    def draw(self):
        global penDown
        global penUp
        penDown()

        for i in range(7):

            self.sendCommandASCII('145 0 14 0 60')
            time.sleep(4.29)

            self.sendCommandASCII('145 255 196 255 236')
            time.sleep(4.29)
        self.sendCommandASCII('145 0 0 0 0')  # Stop
        penUp()
# -------------------------------------------------------Maze------------------
    global maze
    def maze(self):

        while True:
            self.sendCommandASCII('145 0 200 0 200')  # forward
            time.sleep(.1)
            connection.reset_input_buffer()
            self.sendCommandASCII('149 1 7')
            sent = ord(connection.read())

            print(sent)

            if (sent == 3):  # center bumper
                print("In the Front bumper")
                print(sent)
                self.sendCommandASCII('145 0 0 0 0')  # stop
                self.sendCommandASCII('145 255 56 255 56')  # back
                time.sleep(0.5)
                self.sendCommandASCII('145 0 0 0 0')  # stop
                self.sendCommandASCII('145 255 106 0 150')  # turn right
                time.sleep(0.2)
                self.sendCommandASCII('145 0 0 0 0')  # stop

            elif (sent == 1):  # right bumper
                print("INt the right bumper")
                self.sendCommandASCII('145 0 0 0 0')  # stop
                self.sendCommandASCII('145 255 56 255 56')  # back
                time.sleep(0.5)
                self.sendCommandASCII('145 0 150 255 106')  # turn left
                time.sleep(0.2)
                self.sendCommandASCII('145 0 0 0 0')  # stop

            elif (sent == 2):  # left bumper
                print("Int the left bumper")
                self.sendCommandASCII('145 0 0 0 0')  # stop
                self.sendCommandASCII('145 255 56 255 56')  # back
                time.sleep(0.5)
                self.sendCommandASCII('145 0 0 0 0')  # stop
                self.sendCommandASCII('145 255 106 0 150')  # turn right
                time.sleep(0.2)
                self.sendCommandASCII('145 0 0 0 0')  # stop

    # ----------------------------------------SQUARE----------------------------
    global square

    def square(self):
        print "In the SQUARE"
        for _ in range(4):
            # Forward
            self.sendCommandASCII('145 0 200 0 200')
            time.sleep(3)
            self.sendCommandASCII('145 0 0 0 0')  # Stop

            # Right
            self.sendCommandASCII('145 0 150 255 106')
            time.sleep(1.248)
            self.sendCommandASCII('145 0 0 0 0')

    # getDecodedBytes returns a n-byte value decoded using a format string.
    # Whether it blocks is based on how the connection was set up.

    def getDecodedBytes(self, n, fmt):
        global connection

        try:
            return struct.unpack(fmt, connection.read(n))[0]
        except serial.SerialException:
            print "Lost connection"
            tkMessageBox.showinfo('Uh-oh', "Lost connection to the robot!")
            connection = None
            return None
        except struct.error:
            print "Got unexpected data from serial port."
            return None

    # get8Unsigned returns an 8-bit unsigned value.
    def get8Unsigned(self):
        return getDecodedBytes(1, "B")

    # get8Signed returns an 8-bit signed value.
    def get8Signed(self):
        return getDecodedBytes(1, "b")

    # get16Unsigned returns a 16-bit unsigned value.
    def get16Unsigned(self):
        return getDecodedBytes(2, ">H")

    # get16Signed returns a 16-bit signed value.
    def get16Signed(self):
        return getDecodedBytes(2, ">h")

    # A handler for keyboard events. Feel free to add more!
    def callbackKey(self, event):
        k = event.keysym.upper()
        motionChange = False

        if event.type == '2':  # KeyPress; need to figure out how to get constant
            if k == 'P':   # Passive
                self.sendCommandASCII('128')
            elif k == 'S':  # Safe
                self.sendCommandASCII('131')
            elif k == 'F':  # Full
                self.sendCommandASCII('132')
            elif k == 'C':  # Clean
                self.sendCommandASCII('135')
            elif k == 'D':  # Dock
                self.sendCommandASCII('143')
            elif k == '1':
                self.sendCommandASCII(
                    '140 0 16 76 16 76 16 76 32 76 16 76 16 76 32 76 16 79 16 72 16 74 16 76 32 77 16 77 16 77 16 77 32 77 16')
                self.sendCommandASCII(
                    '140 1 7 76 16 76 32 79 16 79 16 77 16 74 16 72 32')
                self.sendCommandASCII('141 0')
                time.sleep(5)
                self.sendCommandASCII('141 1')
            elif k == '2':  # Beep
                # Serial sequence: [140] [Song Number] [Song Length] [Note Number 1] [Note Duration 1] etc.
                print "store part 1"
                # self.sendCommandASCII('140 1 1 28 64')
                self.sendCommandASCII(
                    '140 1 16 57 24 57 8 59 32 57 32 62 32 61 64 57 24 57 8 59 32 57 32 64 32 62 64 57 24 57 8 69 32 66 32')
                print "store part 2"
                # self.sendCommandASCII('140 2 1 25 48')
                self.sendCommandASCII(
                    '140 2 9 62 32 60 32 59 64 67 24 67 8 66 32 62 32 64 32 62 64')
                print "playing part 1"
                self.sendCommandASCII('141 1')

                time.sleep(7.5)
                print "playing part 2"
                self.sendCommandASCII('141 2')
                print "done"
            elif k == '3':  # Beep
                # Serial sequence: [140] [Song Number] [Song Length] [Note Number 1] [Note Duration 1] etc.
                self.sendCommandASCII(
                    '140 3 9 45 48 45 48 45 48 41 36 48 12 45 48 41 36 48 12 45 96 48 141 3')
            elif k == 'R':  # Reset
                self.sendCommandASCII('7')
            elif k == 'UP':
                self.callbackKeyUp = True
                motionChange = True
            elif k == 'DOWN':
                self.callbackKeyDown = True
                motionChange = True
            elif k == 'LEFT':
                self.callbackKeyLeft = True
                motionChange = True
            elif k == 'RIGHT':
                self.callbackKeyRight = True
                motionChange = True

            # Code to run in a square--------------------------------------------------
            elif k == 'Z':
                global square
                square(self)
                self.sendCommandASCII('141 3')  # Song at the end

            elif k == "M":
                global maze
                maze(self)
            elif k == "X":
                global draw
                draw(self)
            elif k == "L":
                global move
                move(self)
            elif k == "O":
                global circle
                circle(self)
            else:
                print repr(k), "not handled"
        elif event.type == '3':  # KeyRelease; need to figure out how to get constant
            if k == 'UP':
                self.callbackKeyUp = False
                motionChange = True
            elif k == 'DOWN':
                self.callbackKeyDown = False
                motionChange = True
            elif k == 'LEFT':
                self.callbackKeyLeft = False
                motionChange = True
            elif k == 'RIGHT':
                self.callbackKeyRight = False
                motionChange = True

        if motionChange == True:
            velocity = 0
            velocity += VELOCITYCHANGE if self.callbackKeyUp is True else 0
            velocity -= VELOCITYCHANGE if self.callbackKeyDown is True else 0
            rotation = 0
            rotation += ROTATIONCHANGE if self.callbackKeyLeft is True else 0
            rotation -= ROTATIONCHANGE if self.callbackKeyRight is True else 0

            # compute left and right wheel velocities
            vr = velocity + (rotation/2)
            vl = velocity - (rotation/2)

            # create drive command
            cmd = struct.pack(">Bhh", 145, vr, vl)
            if cmd != self.callbackKeyLastDriveCommand:
                self.sendCommandRaw(cmd)
                self.callbackKeyLastDriveCommand = cmd

    def onConnect(self):
        global connection

        if connection is not None:
            tkMessageBox.showinfo('Oops', "You're already connected!")
            return

        try:
            ports = self.getSerialPorts()
            port = tkSimpleDialog.askstring(
                'Port?', 'Enter COM port to open.\nAvailable options:\n' + '\n'.join(ports))
        except EnvironmentError:
            port = tkSimpleDialog.askstring('Port?', 'Enter COM port to open.')

        if port is not None:
            print "Trying " + str(port) + "... "
            try:
                connection = serial.Serial(port, baudrate=115200, timeout=1)
                print "Connected!"
                tkMessageBox.showinfo('Connected', "Connection succeeded!")
            except:
                print "Failed."
                tkMessageBox.showinfo(
                    'Failed', "Sorry, couldn't connect to " + str(port))

    def onHelp(self):
        tkMessageBox.showinfo('Help', helpText)

    def onQuit(self):
        if tkMessageBox.askyesno('Really?', 'Are you sure you want to quit?'):
            self.destroy()

    def getSerialPorts(self):
        """Lists serial ports
        From http://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of available serial ports
        """
        if sys.platform.startswith('win'):
            ports = ['COM' + str(i + 1) for i in range(256)]

        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this is to exclude your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')

        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')

        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result


if __name__ == "__main__":
    app = TetheredDriveApp()
    app.mainloop()
    
    # reset the raspberry pie pins
    servo.stop()
    GPIO.cleanup()
