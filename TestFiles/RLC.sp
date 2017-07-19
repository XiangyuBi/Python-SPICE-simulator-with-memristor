#RLC circuit
VS 1 0 1 AC 1
R1 1 2 1k
C1 2 3 1u
L1 3 0 10m
.AC dec 10 10 1000k
.PRINT ac vm(3)
.PRINT ac vp(3)
.end


#RLC Circuit
VS 1 0  pulse 0 4
R1 1 2 5
L1 1 2 0.1
C1 2 0 0.2
.tran 50ms 6s
.print tran v(2)
.end

#RLC circuit(Step Control)
VS 1 0 pulse 0 5
R1 1 2 0.3
L1 2 3 0.2
C1 3 0 0.2
.TRAN 40ms 8s
.PRINT tran v(3)
.end




