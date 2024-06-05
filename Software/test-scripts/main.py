from machine import Timer
from machine import Pin, PWM
import utime as time

class Encoder:

    def __init__(self, time_function, pins = (16, 17)):
        self._last_time = 0
        self._time = 0        
        self._diff = 0
        self._time_function = time_function
        self._hall0 = Pin(pins[0], Pin.IN)
        self._hall1 = Pin(pins[1], Pin.IN)
        
        self._dir_forward = (2, 0, 3, 1) # 0 -> 2 -> 3 -> 1 -> 0
        self._dir_backward = (1, 3, 0, 2) # 1 -> 3 -> 2 -> 0 -> 1
        self._last_state = 0
        self._state = 0
        self._x = 0
        self._v = 0
        self.A = 0
    @micropython.native
    def timer_interrupt_handler(self, timer):
        self.A += 1
    
        hall0 = self._hall0.value()
        hall1 = self._hall1.value()
        
        
        next_state = (hall1 * 2 + hall0) & 0x03
            
        self._last_state = self._state
        self._state = next_state & 0x03
        
        if self._last_state == self._state:
            self._v = 0
            return
        
        self._last_time = self._time
        self._time = self._time_function()
        self._diff = self._time - self._last_time
        
        if self._dir_forward[self._last_state] == self._state:
            self._x += 1
            self._v = 1e6/12 / self._diff
        elif self._dir_backward[self._last_state] == self._state:
            self._x -= 1
            self._v = -1e6/12 / self._diff
        else:
            pass
            #print(self._last_state, self._state, next_state)
            #print('Error encoder skipped states.')
        



enc = Encoder(time.ticks_us)

timer = Timer(freq=10000, mode=Timer.PERIODIC, callback=enc.timer_interrupt_handler)

enable = Pin(15, Pin.OUT)
enable.value(1)
input2 = Pin(13, Pin.OUT)
input2.value(0)
input1 = PWM(Pin(14))
input1.freq(100000) # 100kHz 
input1.duty_u16(int(45/100*65536))


t0 = time.time()
t = time.time()

while t - t0 <= 1:
    t = time.time()
    print(enc._x/12)
timer.deinit()
print(enc.A)

    
input1.duty_u16(0)
