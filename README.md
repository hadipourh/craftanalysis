# Comprehensive Security Analysis of CRAFT

![craft_round_function](/Images/CRAFT/craft_round_function.svg "A Round of CRAFT")


## Zero-Correlation Cryptanalysis

We use MILP-based method to find zero-correlation distinguishers, and then prove them mathematicaly. You can find all the codes we've used for zero-correlation attack in the file [Zero-Correlation](https://github.com/hadipourh/craftanalysis/tree/master/Zero-Correlation). Since the linear behavior of CRAFT in the related tweak model, depends on the starting round, there are four sub-folders in this file, each one is associated with one out of four cases RKT0, RKT1, RKT2, and RKT3.

In order to find a zero-correlation distinguisher, a MILP model containing all constraints modeling the propagation rules of linear masks through the cipher is extracted at first, and then input/output linear masks are set to be a fixed vector with Hamming weight of one, and finally a MILP solver is called to see whether the obtained MILP problem is feasible or not. If the obtained model is infeasible, we can conclude that the correlation of linear hull with that fixed input/output masks must be zero. Since the block-size of CRAFT is 64 bits, there are 4096 possibilities for a fixed input/output with Hamming weight of one. Therefore 4096 different cases must be probed. In order to probe all these cases much faster, we use data-parallel programming.

### RTK0

We found a 14-round zero-correlation distinguisher for the case RTK0. You can see the proof of this case in more details in the paper.

![ZC-TK0](/Images/ZeroCorrelation/zc_14rounds_rt0.svg)

### RTK2

To do ...

![ZC-TK2](/Images/ZeroCorrelation/ZC-TK2-14Rounds.svg "Linear Equivalent of CRAFT")

### RTK3

Todo ...

![ZC-TK3](/Images/ZeroCorrelation/ZC-TK3-14Rounds.svg "Linear Equivalent of CRAFT")

---

## Differential Cryptanalysis

Todo ...

![ein_even](/Images/Even/ein_even_new.svg)

![em_even](/Images/Even/em_even_new.svg)
![em_even_2r_matrix](/Results-Diff-ST/Even/em_even_2r.svg)
![em_even_4r_matrix](/Results-Diff-ST/Even/em_even_4r.svg)
![eout_even](/Images/Even/eout_even_new.svg)

![ein_odd](/Images/Odd/ein_odd_new.svg)

![em_odd](/Images/Odd/em_odd_new.svg)
![em_odd_2r_matrix](/Results-Diff-ST/Odd/em_odd_2r.svg)

![eout_odd](/Images/Odd/eout_odd_new.svg)

---

## Integral Cryptanalysis Based on Division Property

Todo ...

![integral_vars](/Images/Integral/craft_integral_vars.svg)

---
