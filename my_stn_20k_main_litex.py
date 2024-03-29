#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# Copyright (c) 2022 Icenowy Zheng <icenowy@aosc.io>
# Copyright (c) 2022 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.gen import *
from litex.soc.interconnect.wishbone import SRAM
from litex.build.io import DDROutput

from litex.soc.cores.clock.gowin_gw2a import GW2APLL
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.builder import *
from litex.soc.cores.gpio import GPIOIn
from litex.soc.cores.led import LedChaser, WS2812
from litex.soc.interconnect.csr import *
from litex.soc.interconnect.wishbone import Interface

from litedram.modules import M12L64322A  # FIXME: use the real model number
from litedram.phy import GENSDRPHY

import my_sipeed_tang_nano_20k as sipeed_tang_nano_20k

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst      = Signal()
        self.cd_sys   = ClockDomain()
        self.cd_por   = ClockDomain()

        # Clk
        clk27 = platform.request("clk27")

        # Power on reset
        por_count = Signal(16, reset=2**16-1)
        por_done  = Signal()
        self.comb += self.cd_por.clk.eq(clk27)
        self.comb += por_done.eq(por_count == 0)
        self.sync.por += If(~por_done, por_count.eq(por_count - 1))

        # PLL
        self.pll = pll = GW2APLL(devicename=platform.devicename, device=platform.device)
        self.comb += pll.reset.eq(~por_done)
        pll.register_clkin(clk27, 27e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=48e6,
        with_led_chaser     = False, #change defaut to custom
        with_rgb_led        = True,
        **kwargs):

        platform = sipeed_tang_nano_20k.Platform(toolchain="gowin")
        
        # add led.v, led_amaranth.v, led.sv
        platform.add_source("led.v")
        platform.add_source("led_amaranth.v")
        platform.add_source("led.sv")
        # end

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Tang Nano 20K", **kwargs)

        # TODO: XTX SPI Flash

        # SDR SDRAM --------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            class SDRAMPads:
                def __init__(self):
                    self.clk   = platform.request("O_sdram_clk")
                    self.cke   = platform.request("O_sdram_cke")
                    self.cs_n  = platform.request("O_sdram_cs_n")
                    self.cas_n = platform.request("O_sdram_cas_n")
                    self.ras_n = platform.request("O_sdram_ras_n")
                    self.we_n  = platform.request("O_sdram_wen_n")
                    self.dm    = platform.request("O_sdram_dqm")
                    self.a     = platform.request("O_sdram_addr")
                    self.ba    = platform.request("O_sdram_ba")
                    self.dq    = platform.request("IO_sdram_dq")
            sdram_pads = SDRAMPads()

            self.specials += DDROutput(0, 1, sdram_pads.clk, ClockSignal("sys"))

            self.sdrphy = GENSDRPHY(sdram_pads, sys_clk_freq)
            self.add_sdram("sdram",
                phy           = self.sdrphy,
                module        = M12L64322A(sys_clk_freq, "1:1"), # FIXME.
                l2_cache_size = 128,
            )
      
         # RGB Led ----------------------------------------------------------------------------------
        if with_rgb_led: #we don't use it
            self.rgb_led = WS2812(
                pad          = platform.request("rgb_led"),
                nleds        = 3,
                sys_clk_freq = sys_clk_freq
            )
            self.bus.add_slave(name="rgb_led", slave=self.rgb_led.bus, region=SoCRegion(
                origin = 0x2000_0000,
                size   = 4,
            ))


        class WBMasterWrite(Module,AutoCSR):
            def __init__(self, data_width=32):
                # Create a Wishbone master interface
                self.ws2812 = CSRStorage(32,description="WS2812 CSR") 
                self.csr_counter = CSRStorage(24,description="counter") 
                self.wb_master = Interface(data_width=data_width)
                self.counter = Signal(24)
                self.data=Signal(24)
                         
              # Create a state machine for writing
                self.submodules.fsm = fsm = FSM(reset_state="WRITE")
                fsm.act("WRITE", 
                    # Set the address, data, select, and write enable signals
                    self.wb_master.adr.eq(0x2000_0000 >> 2), #Byte to Word conversion
                    # The DDR_BASE_ADDRESS is the base address of the DDR memory in bytes, 
                    # so it needs to be shifted right by 2 bits to convert it to words. 
                    # For example, if the DDR_BASE_ADDRESS is 0x40000000, 
                    # then the wishbone bus address is 0x10000000.
                    self.wb_master.dat_w.eq(self.data),
                    self.wb_master.sel.eq(0xf),
                    self.wb_master.we.eq(1),
                    # Assert cyc and stb signals
                    self.wb_master.cyc.eq(1),
                    self.wb_master.stb.eq(1),     
                    
                    # Go to WAIT state
                    NextState("WAIT")
                )
                fsm.act("WAIT",
                    # Wait for the ack signal from the slave
                    If  (self.wb_master.ack,
                        # Deassert cyc and stb signals
                        self.wb_master.cyc.eq(0),
                        self.wb_master.stb.eq(0),
                      ),

                    NextValue(self.counter, self.counter + 1),
                    NextValue(self.csr_counter.storage, self.counter + 1),
                    If (self.counter[23] == 1, #Color change speed
                            NextValue(self.counter, 0),
                            #Change color
                            If(self.data==0,NextValue(self.data,0xff)).Else(
                            NextValue(self.data,self.data << 2)),
                            NextState("READ")
                        )
                    )
                fsm.act("READ",
                        self.wb_master.stb.eq(1),
                        self.wb_master.cyc.eq(1),
                        self.wb_master.we.eq(0),
                        self.wb_master.sel.eq(0xf),
                        self.wb_master.adr.eq(0x2000_0000 >> 2),
                        If(self.wb_master.ack,
                                NextValue(self.ws2812.storage, self.wb_master.dat_r),
                                NextState("WRITE"),
                        )
                    )
        wb = WBMasterWrite()
        self.submodules.wbm = wb
        self.bus.add_master(name="ws2812 master",master = self.wbm.wb_master)

       
        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser: #we don't use it
            self.leds = LedChaser(
                pads         = platform.request_all("led_n"),
                sys_clk_freq = sys_clk_freq
            )

        # add led.v verilog code
        # module led(
        #         input       clk,
        #         output      led
        # );

        led_1    = platform.request("led_n",0)
        self.specials += Instance("led",
        i_clk    = ClockSignal("sys"),
        o_led = led_1
        )
        # end led.v

        #add led_amaranth.v generated by amaranth
        led_2    = platform.request("led_n",1)
        self.specials += Instance("top", #this is module name, not file
        i_clk = ClockSignal("sys"),
        o_led = led_2,
        i_rst = ResetSignal("sys")
        )
        #end  led_amaranth.v

        # add led.sv systemverilog code
        # module led_sv(
        # input  logic clk,
        # output logic led
        # );

        led_5 = platform.request("led_n",4)
        self.specials += Instance("led_sv", #this is module name, not file
        i_clk = ClockSignal("sys"),
        o_led = led_5,
        )
        #end led_sv.sv

        # class example for led with add CSR
        class Led(Module, AutoCSR):
            def __init__(self,buttons):
                self.nleds = 1
                
                self.led = CSRStorage(1,description="Led Output(s) Control.") #add CSRStorage
                self.pwm = CSRStorage(24,description="PWM Blink") 
                
                leds_m = []
                for i in range(0,self.nleds):
                    leds_m.append(self.led.storage[0])
                
                led_3 = platform.request("led_n",2) #for all leds can use platform.request_all("led_n")
                led_4 = platform.request("led_n",3)
                led_6 = platform.request("led_n",5)
                

                counter = Signal(24) #Decrase this for faster blink
                self.sync += counter.eq(counter + 1)
                self.sync += [
                      If (counter < self.pwm.storage, led_3.eq(0)).Else(led_3.eq(1)), #PWM blink via CSR pwm reg
                    ]
                
                self.comb +=led_6.eq(~leds_m[0])  #Control via CSR led reg   
                
                self.comb+=led_4.eq(buttons._in.status[0]) #control via CSRStatus reg from GPIOIn button 

        # Buttons 
        self.buttons = GPIOIn(pads=~platform.request_all("btn")) 
        # Add Led class and csr
        self.led = Led(self.buttons)
        self.add_csr("led")

       

       
       
        

        self.add_uartbone(name="serial", baudrate=115200) #add uartbone


# Build --------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=sipeed_tang_nano_20k.Platform, description="LiteX SoC on Tang Nano 20K.")
    parser.add_target_argument("--flash",        action="store_true",      help="Flash Bitstream.")
    parser.add_target_argument("--sys-clk-freq", default=48e6, type=float, help="System clock frequency.")
    sdopts = parser.target_group.add_mutually_exclusive_group()
    sdopts.add_argument("--with-spi-sdcard",            action="store_true", help="Enable SPI-mode SDCard support.")
    sdopts.add_argument("--with-sdcard",                action="store_true", help="Enable SDCard support.")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq        = args.sys_clk_freq,
        **parser.soc_argdict
    )
    if args.with_spi_sdcard:
        soc.add_spi_sdcard()
    if args.with_sdcard:
        soc.add_sdcard()

    builder = Builder(soc, **parser.builder_argdict)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

    if args.flash:
        prog = soc.platform.create_programmer()
        prog.flash(0, builder.get_bitstream_filename(mode="flash", ext=".fs"), external=True)

if __name__ == "__main__":
    main()
