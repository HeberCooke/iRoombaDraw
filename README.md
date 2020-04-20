# iRoombaDraw
Draw with the iroomba with raspberry pie and a servo
---
This program sends comands to the iroomba to be able to draw. The servo controlls the ben to move it up or down. To set up the Pi for the servo
```
import RPi.GPIO as GPIO

# setting up the pins for the raspberry pie
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT)
servo = GPIO.PWM(11, 50)
servo.start(0)

```
To reset the pins.
```
# reset the raspberry pie pins
servo.stop()
GPIO.cleanup()
```
To send commands to the iroomba: 
1. Explanation:
2. Desired value -> two’s complement and convert to hex -> split into 2 bytes -> convert to decimal
3. Velocity = -200 = 0xFF38 = [0xFF][0x38] = [255][56]
4. Radius = 500 = 0x01F4 = [0x01][0xF4] = [1][244]
    
This method takes the input values and splits it into 2 bytes and returns a string representation of the value. 
```
def splitBits(number):
        n1 = number >> 8
        n2 = number % 256
        if n1 < 0:
            n1 = 255
        return str(n1) + ' ' + str(n2)
```
