* diode+C
I1 0 1 sin(0 2 10meg)
C2 2 0 0.5f
D1 1 2 test
.TRAN 100ps 100ns
.PRINT tran I(C2)
.END






