#crosstalk
vin 1 0 pulse 0 1 0p 10p 10p 90p
c2 2 0 5f
c1 1 2 5f
r1 2 0 1k
.tran 50fs 200ps
.print tran v(2)
.end 








