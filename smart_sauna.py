import os
import glob
import random
import time
import subprocess
import datetime  # Importing the datetime library
import telepot   # Importing the telepot library
from telepot.loop import MessageLoop    # Library function to communicate with telegram bot
import RPi.GPIO as GPIO     # Importing the GPIO library to use the GPIO pins of Raspberry pi
import pygame.mixer

# Telepot
f=open("telepot.txt","r")
lines=f.readlines()
apitoken=lines[0]
f.close()
bot = telepot.Bot(apitoken)

print (bot.getMe())

GPIO_pump = 16
GPIO_button2= 21
#GPIO_temp = 13
GPIO_button1 = 20
GPIO.setmode(GPIO.BCM)
#GPIO.setup(GPIO_temp, GPIO.OUT)
GPIO.setup(GPIO_pump, GPIO.OUT)
GPIO.setup(GPIO_button1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(GPIO_button2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

#Setting the audio with pygame
pygame.mixer.init(48000, -16, 1, 1024)


# Temperature sensor. GPIO 4
"""
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'
 
def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines
 
def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c
"""

"""def turn_servo(servo_turn):
    servo = GPIO.PWM(GPIO_servo, 50) # GPIO 17 for PWM with 50Hz
    servo.start(2.5) # Initialization
    servo.ChangeDutyCycle(servo_turn)
    time.sleep(1)
    servo.stop()"""
    
def printit():
    print ("Pumppu päällä")
    GPIO.output(GPIO_pump, GPIO.HIGH)
    time.sleep(throw_water_amount)
    print ("Pumppu pois")
    GPIO.output(GPIO_pump, GPIO.LOW)
    time.sleep(throw_water_delay)

def send_message(command):
    message = {'message_id': 2001, 'from': {'id': 442989985, 'is_bot': False, 'first_name': 'Henrikki',
                                      'username': 'helangor', 'language_code': 'fi'},
         'chat': {'id': 442989985, 'first_name': 'Henrikki', 'username': 'helangor', 'type': 'private'},
         'date': 1571569803, 'text': command, 'entities': [{'offset': 0, 'length': 3, 'type': 'bot_command'}]}
    global temperature_alarm
    temperature_alarm = False
    handle(message)

#Checks new messages 
def handle(msg):
    chat_id = msg['chat']['id'] # Receiving the message from telegram
    command = msg['text']   # Getting text from the message    
    print ('Received:')
    print(command)
    # Comparing the incoming message to send a reply according to it
    if command == '/hi':
        bot.sendMessage (chat_id, str("Moro!"))
    elif command == '/temp':
        temp = read_temp()
        bot.sendMessage(chat_id, str("Lämpötila on ") + (str(temp)[:4]) + str(" astetta"))
    elif command == '/sauna_ready':
        bot.sendMessage(chat_id, str("Saunan lämpötila on ") + (str(temp)[:4]) + str(" astetta, tulkaa saunaan!"))
    elif command.startswith('/cta'):
        global lämpövahti_lämpötila
        try:
            lämpövahti_lämpötila = float(command.split(' ')[1])
            print(lämpövahti_lämpötila)
            bot.sendMessage(chat_id, str("Lämpövahdin raja muutettu ") + (str(lämpövahti_lämpötila)[:4]) + str(" asteeseen"))
        except:
            bot.sendMessage(chat_id, str("Anna uusi lämpötila komennon jälkeen esim: /cta 45"))
    elif command == '/temp_alarm_on':
        global temperature_alarm
        temperature_alarm = True
        bot.sendMessage(chat_id, str("Lämpövahti kytketty päälle ") + (str(lämpövahti_lämpötila)[:4]) + str(" asteeseen"))
    elif command == 'löyly':
        threading.Timer(5.0, printit).start()
        bot.sendMessage(chat_id, str("Löyly moodi kytketty päälle: "))
    elif command == 'help':
        bot.sendMessage(chat_id, str("Komennot ovat: "))
    else:
        pass


MessageLoop(bot, handle).run_as_thread()
print ('Listening....')
#temperature_alarm = True
temperature_alarm = False

lämpövahti_lämpötila = 80
throw_water_delay = 10
throw_water_amount = 2

i = 0
while True:

    if temperature_alarm == True:
        temp = read_temp()
        if temp > lämpövahti_lämpötila:
            send_message("/sauna_ready")
        else:
            pass

    #Plays 1 of the 5 beer sounds, each in turn
    if GPIO.input(GPIO_button1) == GPIO.HIGH:
        if i > 4:
            i=0
        sound = ("/home/pi/Projektit/SmartSauna/sounds/kaliaa" + str(i) + ".wav")
        pygame.mixer.Sound(sound).play()
        time.sleep(0.5)
        i+=1
        
    if GPIO.input(GPIO_button2) == GPIO.LOW:
        GPIO.output(GPIO_pump, GPIO.LOW)
    if GPIO.input(GPIO_button2) == GPIO.HIGH:
        print ('Pump on')
        GPIO.output(GPIO_pump, GPIO.HIGH)
        
    time.sleep(0.1)