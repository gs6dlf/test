// (1) pclk whether can support gating need negotiate with rambus or synopsys
// (2) only support APB2
// SPI first translate to regmap interface, this module only translate the
// regmap interface to APB
module REGMAP2APB #(
    parameter ASIZE = 32,
    parameter DSIZE = 32
)(
    //spi generate apb write and read
    input spi_clk,
    // whether need to stretch the wr and rd width***
    input wr,
    input rd,
    input [ASIZE-1:0] addr,
    input [DSIZE-1:0] wdata,
    output [DSIZE-1:0] rdata,

    input apb_clk,  // for apb clock
    input rstn, 

    //apb interface
    // whether support pclk gating TBD***
    output pclk,
    output prstn,
    output pwrite,   //1: write, 0: read
    output psel,
    output penable,
    output [ASIZE-1:0] paddr,
    output [DSIZE-1:0] pwdata,
    input [DSIZE-1:0] prdata
    //no need to support APB3, only support APB2, for the SPI need
    //return time in 8 spi clock
    //input   pready,
    //input pslverr
);

always@(posedge spi_clk)begin
    wr_1d <= wr;
    rd_1d <= rd;
end


