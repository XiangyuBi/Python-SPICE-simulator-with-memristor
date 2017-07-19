*

x1 1 0 100 25k 2k
Vin 1 2 pulse 0 1.8 0 10n 10n 100n 1 2
V2  0 2 pulse 0 1.8 120n 10n 10n 100n 1 2
.TRAN 0.1n 500n
.Print tran v(1) v(2)  i(x1) 
.end