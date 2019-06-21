import time
import board
import pulseio
import digitalio
import analogio
import array

import supervisor
supervisor.set_rgb_status_brightness(10)

# 38 for NEC
ir_led1 = pulseio.PWMOut(board.D9, frequency=1000*38, duty_cycle=0) 
ir_led_send = pulseio.PulseOut(ir_led1)

# recv = pulseio.PulseIn(board.D3, maxlen=150, idle_state = True)
recv = pulseio.PulseIn(board.D3, maxlen=1000, idle_state = True)

rec_button = digitalio.DigitalInOut(board.D11)
play_button = digitalio.DigitalInOut(board.D10)

# setting up indicator LED
led0 = digitalio.DigitalInOut(board.D12)
led0.switch_to_output()

# led1 is used to indicate recording and playback
led1 = digitalio.DigitalInOut(board.D13)
led1.switch_to_output()

dial = analogio.AnalogIn(board.A0)

# waits for IR to be detected, returns
def get_ir(inter_but=None, inter_fun=None):
    ir_f = array.array('H')
    print('waiting for ir')
    recv.clear()
    while len(recv) == 0:
        if inter_but != None and not inter_but.value:
            if inter_fun != None: inter_fun()
            return None
    # time to collect more ir stuff
    time.sleep(.2) 
    print(len(recv))
    for i in range(len(recv)):
        ir_f.append(recv[i])
    recv.clear()
    time.sleep(.01)
    print('recieved')
    return ir_f

def imitate_u(ir_f):
    # enable_out()
    ir_led1.duty_cycle = (2**16)//3 #???
    time.sleep(.4)
    print('sending')
    if ir_f[0] == 65535:
        ir_led_send.send(ir_f[1:])
    else:
        ir_led_send.send(ir_f)
    # give some cooldown time
    time.sleep(.5)
    ir_led1.duty_cycle = 0

# so nothing devastating happens if play before record
to_send = array.array('H')
lst = []
current = 0

def reset_lst():
    global lst
    global current
    lst = []
    current = 0
    print('list reset')

if __name__ == '__main__':
    while True:
        if not rec_button.value:
            led1.value = True
            to_send = get_ir(play_button, reset_lst)
            if to_send != None:
                lst.append(to_send)
                print(to_send)
            led1.value = False
        elif not play_button.value:
            print(lst)
            if len(lst) != 0:
                print(len(lst))
                for i in range(5):
                    time.sleep(.05)
                    led1.value = not led1.value
                if current == len(lst): current = 0
                imitate_u(lst[current])
                current += 1
                led1.value = False
