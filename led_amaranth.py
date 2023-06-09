from amaranth import *


class LEDBlinker(Elaboratable):
    def __init__(self):
        
        # Ports
        self.led  = Signal()

       
    def elaborate(self, platform):
        m = Module()

        led = self.led
        half_freq = int(27e6 // 2)
        timer = Signal(range(half_freq + 1))
        

        with m.If(timer == half_freq):
            m.d.sync += led.eq(~led)
            m.d.sync += timer.eq(0)
        with m.Else():
            m.d.sync += timer.eq(timer + 1)

        return m

from amaranth.back import verilog

led_amaranth = LEDBlinker()
with open("led_amaranth.v", "w") as f:
    f.write(verilog.convert(led_amaranth, ports=[led_amaranth.led]))