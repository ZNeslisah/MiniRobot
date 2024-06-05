import time
from rp2 import PIO, StateMachine, asm_pio
from machine import Pin
import utime

class Encoder:
    FORWARD = 0
    BACKWARD = 1
    FAULT = 2
    def __init__(self, ID=0):
        self._last_time = 0
        self._time = 0        
        self._diff = 0
        self._id = ID
        
        self._dir_forward = (2, 0, 3, 1) # 0 -> 2 -> 3 -> 1 -> 0
        self._dir_backward = (1, 3, 0, 2) # 1 -> 3 -> 2 -> 0 -> 1
        self._last_state = 0
        self._state = 0
        self._dir = Encoder.FORWARD
        
    def update_state(self, next_state):
        self._last_state = self._state
        self._state = next_state & 0x03
        
    def update_dir(self):
        if self._dir_forward[self._last_state] == self._state:
            self._dir = Encoder.FORWARD
        elif self._dir_backward[self._last_state] == self._state:
            self._dir = Encoder.BACKWARD
        else:
            self._dir = Encoder.FAULT
        return self._dir
    
    @property
    def dir(self):
        return self._dir
        
    
    def update_time(self, new_time):
        self._last_time = self._time
        self._time = new_time
        
    def update_diff(self):
        self._diff = time.ticks_diff(self._time, self._last_time)
        return self._diff
        
    @property
    def diff(self):
        return self._diff
    
    @micropython.native
    def irq_handler(self, sm):
        t = time.ticks_us()
        self.update_time(t)
        self.update_diff()
        self.update_state(sm.get())
        self.update_dir()
        
    @property
    def state(self):
        return self._state
    
@asm_pio()
def encoder_pio():
    set(x, 0)
    set(y, 0)
    mov(isr, x)
    label("start")
    mov(isr,null)
    in_(pins, 2)
    mov(x,isr)
    jmp(x_not_y, "change")
    jmp("start")
    label("change")
    mov(y,x)
    push()
    irq(noblock,rel(0))
    jmp("start")
    wrap()

enc = Encoder(0)
sm = StateMachine(0, encoder_pio, freq=100_000, in_base=Pin(16))
sm.irq(enc.irq_handler)
sm.active(1)

while True:
    print(enc.diff)