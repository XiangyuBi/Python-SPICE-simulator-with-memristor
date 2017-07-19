*spiking test
V1 1 0 1
V2 5 0 1
C2 1 2 1.5n
x2 1 2 100 16k 1k
R2 2 4 1k 
R1 4 6 1k
C1 4 5 0.5n
x1 5 4 100 16k 1k
R3 2 3 1k
C3 2 3 1n
Vin 6 0 pulse 0 3 0 0 0 100p 1 2
.tran 500fs 2000ps
.print tran v(3) v(6)
.end 