*opamp
Vdd 1 0 3
Iref 0 2 1m
m8 2 2 1 1 pmos
m5 3 2 1 1 pmos
m1 4 5 3 3 pmos
m2 6 7 3 3 pmos
m3 4 4 0 0 nmos
m4 6 4 0 0 nmos
m6 8 6 0 0 nmos
Cc 6 8 1u
m7 8 2 1 1 pmos
vin1 5 0 1
vin2 7 5 sin(0 0.01 50meg)
.TRAN 100ps 100ns
.Print tran v(8)
.end

*opamp
Vdd 1 0 3
Iref 2 0 3u
m8 2 2 1 1 pmos
m5 3 2 1 1 pmos
m1 4 5 3 3 pmos
m2 6 7 3 3 pmos
m3 4 4 0 0 nmos
m4 6 4 0 0 nmos
m6 8 6 0 0 nmos
Cc 6 8 1u
m7 8 2 1 1 pmos
vin1 5 0 1
vin2 7 5 0
.DC vin1 0 3 0.01
.Print dc v(8) v(5)
.end

*multi MOSFETs
vs 1 0 sin(1.5 1.5 20meg)
vd 3 0 3
M1 2 1 0 0 NMOS
M2 2 1 3 3 pmos
M3 4 2 0 0 NMOS
M4 4 2 3 3 pmos
M5 5 4 0 0 NMOS
M6 5 4 3 3 pmos
M7 6 5 0 0 NMOS
M8 6 5 3 3 pmos
M9 7 6 0 0 NMOS
M10 7 6 3 3 pmos
M11 8 7 0 0 NMOS
M12 8 7 3 3 pmos
.tran 100ps 100ns
.print tran v(8) v(1)
.end








*MOSFET .TRAN
vi 1 0 sin(0.8 0.01 50meg)
vd 3 0 3
M1 2 1 0 0 nmos
R 2 3 10meg
.TRAN 100ps 100ns
.PRINT TRAN v(2)
.end

*NMOS+R
vd 1 0 3
vi 3 0 3
m1 2 1 0 0 nmos
r1 3 2 10meg
.dc vd 0 3 0.01
.print dc v(2) v(1)
.end




*MOSFET .AC
vi 1 0 1 AC 1
vd 3 0 3
M1 2 1 0 0 nmos
R1 3 2 1meg
C1 2 0 10p
.AC dec 10 10 10meg
.print ac vp(2)
.print ac vm(2)
.end


*Inverter
vin 1 0 1
vdd 3 0 3
M1 2 1 0 0 nmos
M2 2 1 3 3 pmos
.dc vin 0 3 0.01
.print dc v(2) v(1)
.end


*Buffer
vin 1 0 pulse 0 3 1n 4n 4n 20n 50n
vdd 3 0 3
M1 2 1 0 0 nmos
M2 2 1 3 3 pmos
M3 4 2 0 0 nmos
M4 4 2 3 3 pmos
.tran 100ps 105ns
.print tran v(1) v(4)
.end

*~(A+B)
va 1 0 pulse 0 3 1n 0 0 4n 8n
vb 2 0 pulse 0 3 1n 0 0 2n 4n
vd 3 0 3
M1 4 1 0 0 nmos
M2 4 2 0 0 nmos
M3 4 1 5 5 pmos
M4 5 2 3 3 pmos
.tran 100ps 9ns
.print tran v(4)
.end




*PMOS+R
vd 1 0 sin(1.5 1.5 100meg)
vi 3 0 1
m1 2 3 1 1 pmos
r1 2 0 1meg
*.dc vi 0 3 0.01
*.print dc v(2)
.tran 100ps 100ns
.print tran v(2)
.end

*NMOS+R
vd 1 0 3
vi 3 0 3
m1 2 1 0 0 nmos
.model nmos nmos
r1 3 2 1meg
.dc vd 0 3 0.01
.print dc v(2)
.end





*~(AB)
va 1 0 pulse 0 3 1n 0 0 4n 8n
vb 2 0 pulse 0 3 1n 0 0 2n 4n
vd 3 0 3
M1 4 1 5 5 nmos
M2 5 2 0 0 nmos
M3 4 1 3 3 pmos
M4 4 2 3 3 pmos
.tran 100ps 9ns
.print tran v(4)
.end






*MOSFET .tran
vs 1 0 sin(1.5 1.5 100meg)
vd 3 0 3
M1 2 1 0 0 nmos
M2 2 1 3 3 pmos
.tran 100ps 100ns
.print tran v(2)
.end