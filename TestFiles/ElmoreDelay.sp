#ElmoreDelay.sp
vin 1 0 pulse 0 1
r1 1 2 1k
c1 2 0 1f
r2 2 3 1k
c2 3 0 1f
r3 2 4 1k
c3 4 0 1f
r4 4 5 1k
c4 5 0 1f
r5 4 6 1k
c5 6 0 1f
.tran 10p 0.5n
.print tran v(6)
.end

