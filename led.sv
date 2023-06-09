module led_sv(
    input       logic clk,
    output logic led
);

logic count_1s_flag;
logic [23:0] count_1s = 0;

always_ff @(posedge clk ) begin
    if( count_1s < 27000000/2 ) begin
        count_1s <= count_1s + 1;
        count_1s_flag <= 0;
    end
    else begin
        count_1s <= 0;
        count_1s_flag <= 1;
    end
end

logic led_value = 1;

always_ff @(posedge clk ) begin
    if( count_1s_flag ) begin
    led_value <= ~led_value;
    end
end

assign led = led_value;

endmodule