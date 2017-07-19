*
Vin 3 1 pulse 0 3 0 0 0 100n 1 2
C1 1 0 30n
C2 2 0 10n
L1 3 2 1u
x1 1 0 100 28k 2k

.TRAN 1n 50u
.Print tran v(1)  v(2) v(3)
.end