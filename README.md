# Comprehensive Security Analysis of CRAFT

![craft_round_function](/Images/CRAFT/craft_round_function.svg "A Round of CRAFT")

## Prerequisites
 Todo ...

## Zero-Correlation Cryptanalysis

We use MILP-based method to find zero-correlation distinguishers, and then give a mathematical proof for them. You can find all the codes we've used for zero-correlation attack in the file [Zero-Correlation](https://github.com/hadipourh/craftanalysis/tree/master/Zero-Correlation). Since the linear behavior of CRAFT in the related tweak model, depends on the starting round, there are four sub-folders in this file, each one is associated with one out of four cases RTK0, RTK1, RTK2, and RTK3.

In order to find a zero-correlation distinguisher, a MILP model containing all constraints modeling the propagation rules of linear masks through the cipher is extracted at first, and then input/output linear masks are set to be a fixed vector with Hamming weight of one, and finally a MILP solver is called to see whether the obtained MILP problem is feasible. If the obtained model is infeasible, we can conclude that the correlation of linear hull with that fixed input/output masks must be zero. Since the block-size of CRAFT is 64 bits, and the length of tweak is 64 bits too, there are 262144 possibilities for a fixed input/output masks with Hamming weight of one in the related-tweak model. Therefore 262144 different cases must be probed. In order to check all these cases much faster, we use data-parallel programming, and devide the tasks between 16 threads of one CPU, when each single thread probe (262144/16) 16384 cases. If you use a CPU equiped with 16 different cores, then all tasks is executed in parallel. 

### RTK0

We've found a 14-round zero-correlation distinguisher for the case RTK0. You can see the proof of this case in more details in the paper. If you are interested to know how we could find it, we invite you to take a look at the codes in : `/Zero-Correlation/ZeroCorrelation-rev1-tk0/`, and the run the following command:
```
python3 main.py
```
If you would like to use this tool for inspecting a specified numer of rounds in case RTK0, you mereley need to change the value of a parameter called `rounds`, in line 34 of `main.py` file, and use `python3 main.py` again, to run the modified program. 

![ZC-TK0](/Images/ZeroCorrelation/zc_14rounds_rt0.svg)

### RKT1
For this case we have not found a zero-correlation distinguisher covering more than 13 rounds of CRAFT, in the related tweak mode, by our MILP-based tool. All the codes we have used for this case, can be found in directory `./Zero-Correlation/ZeroCorrelation-rev1-tk1/`. If want to check our claim for this case, you are invited take a look at the codes, and run the following command, to reproduce our results:
```
python3 main.py
```
### RTK2

For this case we have also found a 14-round distinguisher via our MILP-based tool. The following picture shows a mathematical proof for our distinguiser. The codes we have used for this case, are placed in directory `./Zero-Correlation/ZeroCorrelation-rev1-tk2`, and if you want to run the program, and reproduce our results, you need to open your terminal in this directory and type the following command: 
```
python3 main.py
```
Just like the other cases, the value of the parameter `rounds` in line 34 of `main.py`, depicting the number of rounds in the analysis. 

![ZC-TK2](/Images/ZeroCorrelation/ZC-TK2-14Rounds.svg "Linear Equivalent of CRAFT")

### RTK3
The following figure, shows a mathematical proof, for the 14-round zero-correlation distinguisher we have found in case RTK3, by our MILP-based tool. The codes associated with this case can be found in directory `./Zero-Correlation/ZeroCorrelation-rev1-tk3`, and can be execute by the following command:
```
python3 main.py
```
![ZC-TK3](/Images/ZeroCorrelation/ZC-TK3-14Rounds.svg "Linear Equivalent of CRAFT")

Although we inspected 15 rounds of CRAFT, in cases RTK0, RTK2, and RTK3 by this method, we didn't find a zero-correlation distinguisher, covering more than 14 rounds in these cases. Note that, sometimes finding a mathematical proof for the obtained distinguishre, might be not easy, just like the distinguisher we have presented for 14-rounds of CRAFT in case RTK0. 

---

## Differential Cryptanalysis

In order to find a lower bound for differential, we did the following steps:
1- Find an optimal activity pattern via a word oriented MILP model
2- Check to see wther there exist an optimum differential trail with the obtained activity pattern. To do this, we construct a SMT model corresponding to the problem of finding an optimum differential trail, and then add all constraints corresponding to zero words in the obtained activity pattern, which makes the probelm very easier. Then an SMT solver like stp, is called to solve the obtained SMT problem. However, all this steps can be done by a MILP solver too. 
2- Divide a long differential trail into some smaller pices (divide and conqure), which makes the problem of counting differential trails easier. 
3- Fixed the input/output difference of each smaller pieces, and then call the optimized CryptoSMT to find a lower bound for the obtained differential effect.

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
