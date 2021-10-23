module SPI_SLAVE(
    input spi_csn,
    input spi_mosi,
    input spi_clk,
    output spi_miso,

    output reg_cs,
    output reg_wr,
    output reg_rd,
    output reg_addr,
    output reg_wdata,
    input  reg_rdata,

    output crc_err
);

always@(negedge spi_clk or posedge spi_csn) begin
    if(spi_csn)
        cnt <= 6'b0; //<6>
    else if(cnt < 6'd63)
        cnt <= cnt + 6'b1;
end

always@(posedge spi_clk or posedge spi_csn) begin
    if(spi_csn)
        buffer <= 32'b0; //<32>
    else
        buffer <= {buffer[30:0],spi_mosi};
end

always@(negedge spi_clk or posedge spi_csn) begin
    if(spi_csn)
        lb <= 1'b0; //<1> loop back 
        ma <= 7'd9; //<7> module address
        rsv_or_ce <= 1'b0; //<1> rsv for write, crc enable for read
        cs_or_rsv <= 1'b0; //<1> current or store for write, rsv for read
        sr <= 1'b0; //<1> 0 for sequential, 1 for repeat
        rw <= 1'b0; //<1> 0 for read, 1 for write
        ra <= 12'b0; //<12> register address
    else
        case(cnt):
            6'd0: lb <= buffer[0];
            6'd7: ma <= buffer{6:0];
            6'd8: rsv_or_ce <= buffer[0];
            6'd9: cs_or_rsv <= buffer[0];
            6'd10: sr <= buffer[0];
            6'd11: rw <= buffer[0];
            6'd23: ra <= buffer[11:0];
        endcase
end


