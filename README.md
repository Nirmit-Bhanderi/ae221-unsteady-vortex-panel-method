# Unsteady Vortex Panel Method

A computational aerodynamics project completed for **AE221: Aerodynamics** at the Indian Institute of Science (IISc).

## Overview

This project investigates the impulsive start of a two-dimensional flat plate using an unsteady vortex panel method.

The flat plate is initially at rest and is suddenly accelerated to a free-stream velocity of 40 m/s at an angle of attack of 5°.

The simulation computes the time evolution of:

- Bound circulation, Γ(t)
- Unsteady lift per unit span, L′(t)
- Induced drag coefficient, C_D(t)

## Methodology

The implementation follows the formulation presented in Katz and Plotkin, *Low-Speed Aerodynamics*, Section 13.8.

Key elements include:

- Discretization of the flat plate into bound-vortex panels
- Enforcement of the no-penetration boundary condition
- Discrete wake-vortex modelling
- Conservation of circulation through Kelvin's theorem
- Numerical solution of the resulting linear system at each time step
- Calculation and visualization of transient aerodynamic loads

## Simulation parameters

| Parameter | Value |
|---|---:|
| Angle of attack | 5° |
| Free-stream velocity | 40 m/s |
| Chord length | 1 m |
| Air density | 1.225 kg/m³ |
| Number of panels | 10 |
| Non-dimensional time step | 0.25 |
| Number of time steps | 600 |

## Results

The simulation examines the transient build-up of circulation, the evolution of lift following the impulsive start, and the decay of induced drag as the starting vortex moves downstream.

The accompanying report contains the theoretical derivation, numerical results, plots, and discussion.

## Reference

Katz, J. and Plotkin, A. *Low-Speed Aerodynamics*, 2nd edition, Cambridge University Press, 2001, Section 13.8.

## Academic context

AE221 Aerodynamics — Term Paper, Part 1, Question 2.

This repository documents coursework completed as part of my undergraduate studies. The report and implementation should be shared only in accordance with applicable course policies.
