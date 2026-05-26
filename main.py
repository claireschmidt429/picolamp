import bluetooth
from machine import Pin, PWM
import time

# RGB pins - GP0, GP1, GP2
r = PWM(Pin(0))
g = PWM(Pin(1))
b = PWM(Pin(2))
r.freq(1000)
g.freq(1000)
b.freq(1000)

# State
mode = 0
brightness = 1.0
speed = 0.02
solid_color = (255, 255, 255)

def set_color(red, green, blue):
    r.duty_u16(int(red * brightness * 257))
    g.duty_u16(int(green * brightness * 257))
    b.duty_u16(int(blue * brightness * 257))

def off():
    set_color(0, 0, 0)

def solid(red=255, green=255, blue=255):
    set_color(red, green, blue)

def slow_fade():
    steps = [(255,0,0),(0,255,0),(0,0,255),(255,0,255),(255,255,0),(0,255,255)]
    for i in range(len(steps)):
        c1 = steps[i]
        c2 = steps[(i+1) % len(steps)]
        for t in range(100):
            if mode != 2: return
            ri = int(c1[0] + (c2[0]-c1[0]) * t/100)
            gi = int(c1[1] + (c2[1]-c1[1]) * t/100)
            bi = int(c1[2] + (c2[2]-c1[2]) * t/100)
            set_color(ri, gi, bi)
            time.sleep(speed * 2)

def fast_fade():
    steps = [(255,0,0),(0,255,0),(0,0,255),(255,0,255),(255,255,0),(0,255,255)]
    for i in range(len(steps)):
        c1 = steps[i]
        c2 = steps[(i+1) % len(steps)]
        for t in range(100):
            if mode != 3: return
            ri = int(c1[0] + (c2[0]-c1[0]) * t/100)
            gi = int(c1[1] + (c2[1]-c1[1]) * t/100)
            bi = int(c1[2] + (c2[2]-c1[2]) * t/100)
            set_color(ri, gi, bi)
            time.sleep(speed * 0.3)

def pulse():
    rc, gc, bc = solid_color
    for i in range(255):
        if mode != 4: return
        set_color(rc*i//255, gc*i//255, bc*i//255)
        time.sleep(speed)
    for i in range(255):
        if mode != 4: return
        set_color(rc*(255-i)//255, gc*(255-i)//255, bc*(255-i)//255)
        time.sleep(speed)

def strobe():
    rc, gc, bc = solid_color
    set_color(rc, gc, bc)
    time.sleep(speed * 0.5)
    if mode != 5: return
    set_color(0, 0, 0)
    time.sleep(speed * 0.5)

def rainbow():
    def wheel(pos):
        if pos < 85:
            return (pos*3, 255-pos*3, 0)
        elif pos < 170:
            pos -= 85
            return (255-pos*3, 0, pos*3)
        else:
            pos -= 170
            return (0, pos*3, 255-pos*3)
    for i in range(255):
        if mode != 6: return
        set_color(*wheel(i))
        time.sleep(speed)

def brightness_cycle():
    global brightness
    # Slowly pulses brightness from full down to 10% and back
    for i in range(100, 9, -1):
        if mode != 7: return
        brightness = i / 100.0
        rc, gc, bc = solid_color
        set_color(rc, gc, bc)
        time.sleep(speed * 1.5)
    for i in range(10, 101):
        if mode != 7: return
        brightness = i / 100.0
        rc, gc, bc = solid_color
        set_color(rc, gc, bc)
        time.sleep(speed * 1.5)

# --- Bluetooth BLE setup ---
_IRQ_CENTRAL_CONNECT    = 1
_IRQ_CENTRAL_DISCONNECT = 2
_IRQ_GATTS_WRITE        = 3

_UART_UUID = bluetooth.UUID("6E400001-B5B3-F393-E0A9-E50E24DCCA9E")
_RX_UUID   = bluetooth.UUID("6E400002-B5B3-F393-E0A9-E50E24DCCA9E")
_TX_UUID   = bluetooth.UUID("6E400003-B5B3-F393-E0A9-E50E24DCCA9E")

_RX = (_RX_UUID, bluetooth.FLAG_WRITE | bluetooth.FLAG_WRITE_NO_RESPONSE)
_TX = (_TX_UUID, bluetooth.FLAG_NOTIFY | bluetooth.FLAG_READ)
_UART_SERVICE = (_UART_UUID, (_TX, _RX))

ble = bluetooth.BLE()
ble.active(True)
((tx, rx),) = ble.gatts_register_services((_UART_SERVICE,))
conn_handle = None

def ble_irq(event, data):
    global conn_handle, mode, brightness, speed, solid_color
    if event == _IRQ_CENTRAL_CONNECT:
        conn_handle, _, _ = data
    elif event == _IRQ_CENTRAL_DISCONNECT:
        conn_handle = None
        advertise()
    elif event == _IRQ_GATTS_WRITE:
        buf = ble.gatts_read(rx)
        msg = buf.decode().strip()
        handle_command(msg)

def handle_command(msg):
    global mode, brightness, speed, solid_color
    if msg.startswith("MODE:"):
        mode = int(msg.split(":")[1])
    elif msg.startswith("BRIGHT:"):
        brightness = int(msg.split(":")[1]) / 100.0
    elif msg.startswith("SPEED:"):
        val = int(msg.split(":")[1])
        speed = 0.1 / val
    elif msg.startswith("COLOR:"):
        parts = msg.split(":")[1].split(",")
        solid_color = (int(parts[0]), int(parts[1]), int(parts[2]))
        mode = 1

ble.irq(ble_irq)

def advertise():
    name = b"PicoLamp"
    adv = bytearray()
    adv += bytes([2, 0x01, 0x06])
    adv += bytes([len(name) + 1, 0x09]) + name
    resp = bytearray()
    resp += bytes([len(name) + 1, 0x09]) + name
    ble.gap_advertise(100000, adv_data=bytes(adv), resp_data=bytes(resp))

advertise()

# Main loop
while True:
    if   mode == 0: off()
    elif mode == 1: solid(*solid_color)
    elif mode == 2: slow_fade()
    elif mode == 3: fast_fade()
    elif mode == 4: pulse()
    elif mode == 5: strobe()
    elif mode == 6: rainbow()
    elif mode == 7: brightness_cycle()
    time.sleep(0.01)
