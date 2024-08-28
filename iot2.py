import gc
import network 
import machine
from machine import Pin, ADC
import time
import BlynkLib

WIFI_SSID = 'F'
WIFI_PASS = 'yakindek'
BLYNK_AUTH = 'Xp6u7QQjcB0Xruvjf2rciVlR3_H--j0k'

dAnalog = 80
dAplikasi = 80
dKedip = 80

led = [None] * 5
indexLed = 0
tickMs = 0
ledRev = False
ledNyala = False

tombol = Pin(14, Pin.IN)
tickTombol = 0
statusTombol = 0

analog = ADC(0)
tickAnalog = 0
speedManual = True

p = machine.Pin(12)
pwn = machine.PWM(p)
nilaiPwn = 512

gc.enable()

led[0]=Pin(16,Pin.OUT)
led[1]=Pin(5,Pin.OUT)
led[2]=Pin(4,Pin.OUT)
led[3]=Pin(0,Pin.OUT)
led[4]=Pin(2,Pin.OUT)


gc.collect()

wifi = network.WLAN(network.STA_IF)
if not wifi.isconnected():
    wifi.active(True)
    wifi.connect(WIFI_SSID, WIFI_PASS)
    while not wifi.isconnected():
        pass
print('IP:', wifi.ifconfig()[0])

gc.collect()
blynk = BlynkLib.Blynk(BLYNK_AUTH)

@blynk.on("connected")
def blynk_connected(ping):
    blynk.sync_virtual(0)
    blynk.sync_virtual(1)
    blynk.sync_virtual(2)
    blynk.sync_virtual(3)
    print("Blynk ok")
    
@blynk.on("disconnected")
def blynk_disconnected():
  print('Blynk putus')
  
@blynk.on("V0")
def v0_write_handler(value):
  global ledNyala
  #print('V0: ' + str(value[0]))
  ledNyala = int(value[0])>0
def v0_read_handler():
  if ledNyala:
    blynk.virtual_write(0, 1)
  else:
    blynk.virtual_write(0, 0)
    
@blynk.on("V1")
def v1_write_handler(value):
  #print('V1: ' + str(value[0]))
  global nilaiPwn, pwn
  nilaiPwn = int(value[0])
  pwn.duty(1023-nilaiPwn)
def v1_read_handler():
  global nilaiPwn
  blynk.virtual_write(1, nilaiPwn)

@blynk.on("V2")
def v2_write_handler(value):
  #print('V2: ' + str(value[0]))
  global speedManual
  speedManual = int(value[0])==0
def v2_read_handler():
  global speedManual
  if speedManual:
    blynk.virtual_write(2, 0)
  else:
    blynk.virtual_write(2, 1)

@blynk.on("V3")
def v3_write_handler(value):
  #print('V3: ' + str(value[0]))
  global dAplikasi
  dAplikasi =  1024 - int(value[0])
def v3_read_handler():
  blynk.virtual_write(3, 1024-dAplikasi)
  
blynk.virtual_write(4, "Bima Satria Buana")
print("Enter loop")
while True:
  blynk.run()
  if (time.ticks_ms()-tickTombol>80):
    
    tickAnalog = time.ticks_ms()
    #v = analog.read()
    dAnalog = analog.read()
    
    tickTombol = time.ticks_ms()
    tekan = tombol.value()
    if (tekan==0):
      statusTombol = True
    else:
      #tunggu sampai tombol dilepas
      if (statusTombol):

        statusTombol = False
        #print("Tombol dipencet")
        ledNyala = not(ledNyala)
        if ledNyala:
          blynk.virtual_write(0, 1)
        else:
          blynk.virtual_write(0, 0)
  
  #Mengurusi LED
  if not(ledNyala):
    indexLed=-1
  elif ledNyala and ((time.ticks_ms() - tickMs) > dKedip):
    tickMs = time.ticks_ms()
    if (ledRev):
      indexLed=indexLed-1
      if (indexLed<0):
        indexLed = 2
        ledRev = False
    else:
      indexLed=indexLed+1
      if (indexLed>4):
        indexLed = 3
        ledRev = True
      
  for i in range(0, 5):
    if (indexLed==i):
      led[i].value(1)
    else:
      led[i].value(0)
    
  if (speedManual):
    dKedip = dAnalog
  else:
    dKedip = dAplikasi
    
  machine.idle()
  gc.collect()
  


