/* Generated by Yosys 0.27+22 (git sha1 53c0a6b78, gcc 10.4.0-4ubuntu1~22.04 -fPIC -Os) */

(* \amaranth.hierarchy  = "top" *)
(* top =  1  *)
(* generator = "Amaranth" *)
module top(clk, rst, led);
  reg \$auto$verilog_backend.cc:2097:dump_module$3  = 0;
  (* src = "/media/theodore/Linux_data/Gowin/litex_test/./led_amaranth.py:19" *)
  wire \$1 ;
  (* src = "/media/theodore/Linux_data/Gowin/litex_test/./led_amaranth.py:20" *)
  wire \$3 ;
  (* src = "/media/theodore/Linux_data/Gowin/litex_test/./led_amaranth.py:19" *)
  wire \$5 ;
  (* src = "/media/theodore/Linux_data/Gowin/litex_test/./led_amaranth.py:23" *)
  wire [24:0] \$7 ;
  (* src = "/media/theodore/Linux_data/Gowin/litex_test/./led_amaranth.py:23" *)
  wire [24:0] \$8 ;
  (* src = "/home/theodore/.local/lib/python3.10/site-packages/amaranth/hdl/ir.py:527" *)
  input clk;
  wire clk;
  (* src = "/media/theodore/Linux_data/Gowin/litex_test/./led_amaranth.py:8" *)
  output led;
  reg led = 1'h0;
  (* src = "/media/theodore/Linux_data/Gowin/litex_test/./led_amaranth.py:8" *)
  reg \led$next ;
  (* src = "/home/theodore/.local/lib/python3.10/site-packages/amaranth/hdl/ir.py:527" *)
  input rst;
  wire rst;
  (* src = "/media/theodore/Linux_data/Gowin/litex_test/./led_amaranth.py:16" *)
  reg [23:0] timer = 24'h000000;
  (* src = "/media/theodore/Linux_data/Gowin/litex_test/./led_amaranth.py:16" *)
  reg [23:0] \timer$next ;
  assign \$1  = timer == (* src = "/media/theodore/Linux_data/Gowin/litex_test/./led_amaranth.py:19" *) 24'hcdfe60;
  assign \$3  = ~ (* src = "/media/theodore/Linux_data/Gowin/litex_test/./led_amaranth.py:20" *) led;
  assign \$5  = timer == (* src = "/media/theodore/Linux_data/Gowin/litex_test/./led_amaranth.py:19" *) 24'hcdfe60;
  assign \$8  = timer + (* src = "/media/theodore/Linux_data/Gowin/litex_test/./led_amaranth.py:23" *) 1'h1;
  always @(posedge clk)
    timer <= \timer$next ;
  always @(posedge clk)
    led <= \led$next ;
  always @* begin
    if (\$auto$verilog_backend.cc:2097:dump_module$3 ) begin end
    \led$next  = led;
    (* src = "/media/theodore/Linux_data/Gowin/litex_test/./led_amaranth.py:19" *)
    casez (\$1 )
      /* src = "/media/theodore/Linux_data/Gowin/litex_test/./led_amaranth.py:19" */
      1'h1:
          \led$next  = \$3 ;
    endcase
    (* src = "/home/theodore/.local/lib/python3.10/site-packages/amaranth/hdl/xfrm.py:519" *)
    casez (rst)
      1'h1:
          \led$next  = 1'h0;
    endcase
  end
  always @* begin
    if (\$auto$verilog_backend.cc:2097:dump_module$3 ) begin end
    (* full_case = 32'd1 *)
    (* src = "/media/theodore/Linux_data/Gowin/litex_test/./led_amaranth.py:19" *)
    casez (\$5 )
      /* src = "/media/theodore/Linux_data/Gowin/litex_test/./led_amaranth.py:19" */
      1'h1:
          \timer$next  = 24'h000000;
      /* src = "/media/theodore/Linux_data/Gowin/litex_test/./led_amaranth.py:22" */
      default:
          \timer$next  = \$8 [23:0];
    endcase
    (* src = "/home/theodore/.local/lib/python3.10/site-packages/amaranth/hdl/xfrm.py:519" *)
    casez (rst)
      1'h1:
          \timer$next  = 24'h000000;
    endcase
  end
  assign \$7  = \$8 ;
endmodule
