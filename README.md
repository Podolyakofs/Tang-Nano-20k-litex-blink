### Litex примеры
Пример использования [litex](https://github.com/enjoy-digital/litex) для FPGA Tang Nano 20k
- 1 led - подключен через verilog
- 2 led - через сгенерированный verilog через [amaranth-hdl](https://github.com/amaranth-lang/amaranth)
- 3 led - управляется через CSRStorage регистр (регулируется заполнение)
- 4 led - через кнопку и CSRStatus регистр
- 5 led - через SystemVerilog
- 6 led - через CSRStorage регистр


Сборка командой 
```
python3 amaranth_led.py
python3 ./my_stn_20k_main_litex.py  --build --load --cpu-type None --csr-csv "csr.csv" --no-uart
```

Затем можно подключиться через litex_server и litex_cli:
```
litex_server --uart --uart-port=/dev/ttyUSB1
litex_cli --gui
```