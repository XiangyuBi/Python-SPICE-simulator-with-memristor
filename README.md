# Python-SPICE-simulator-with-memristor
A HSPICE-like simulator including memristor device

This program presents a practical solution of SPICE-like simulator for comprehensive memristor simulation, 
using Modified Nodal Analysis method. Different memristor models are introduced with a general stamps method, 
the flexibility of the simulator makes it possible for further extension. 
To keep the accuracy and effectiveness of the method, 
three different dynamic approximation methods—Forward Euler, Backward Euler and Trapezoidal Rule 
are adopted to solve the differential equations, 
meanwhile to solve nonlinearity, we implement inner iteration loop of Newton-Raphson method. 

In addition, dynamic time step control can modify the time step dynamically. 
The simulation results verified the correctness and practicability of the simulator. 
Furtherly we can extend more memristor model or memristive devices into the simulator.
