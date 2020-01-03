# Comprehensive Security Analysis of CRAFT

![craft_round_function](/Images/CRAFT/craft_round_function.svg "A Round of CRAFT")

## Prerequisites
 Todo ...

## Zero-Correlation Cryptanalysis

We use MILP-based method to find zero-correlation distinguishers, and then give a mathematical proof for them. You can find all the codes we've used for zero-correlation attack in the file [Zero-Correlation](https://github.com/hadipourh/craftanalysis/tree/master/Zero-Correlation). Since the linear behavior of CRAFT in the related tweak model, depends on the starting round, there are four sub-folders in this file, each one is associated with one out of four cases RTK0, RTK1, RTK2, and RTK3.

In order to find a zero-correlation distinguisher, a MILP model containing all constraints modeling the propagation rules of linear masks through the cipher is extracted at first, and then input/output linear masks are set to be a fixed vector with Hamming weight of one, and finally a MILP solver is called to see whether the obtained MILP problem is feasible or not. If the obtained model is infeasible, we can conclude that the correlation of linear hull with that fixed input/output linear masks must be zero. Since the block-size of CRAFT is 64 bits, and the length of tweak is 64 bits too, there are 262144 possibilities for a fixed input/output masks with Hamming weight of one in the related-tweak model. Therefore 262144 different cases must be probed. In order to check all these cases much faster, we use data-parallel programming, and devide the tasks between 16 threads of one CPU, when each single thread probe (262144/16) 16384 different cases. If you use a CPU equiped with 16 different cores, then all tasks is executed in parallel. 

### RTK0

We've found a 14-round zero-correlation distinguisher for the case RTK0. You can see the proof of this case in more details in the paper. If you are interested to know how we could find it, we invite you to take a look at the codes in : `/Zero-Correlation/ZeroCorrelation-rev1-tk0/`, and then run the following command to reproduce our results:
```
python3 main.py
```
If you would like to use this tool for inspecting a specified numer of rounds in case RTK0, you mereley need to change the value of a parameter `rounds`, in line 34 of `main.py` file, and use `python3 main.py` again, to run the modified program.  

![ZC-TK0](/Images/ZeroCorrelation/zc_14rounds_rt0.svg)

### RKT1
For this case we have not found a zero-correlation distinguisher covering more than 13 rounds of CRAFT, in the related tweak model, by our MILP-based tool. All the codes we have used for this case, can be found in directory `./Zero-Correlation/ZeroCorrelation-rev1-tk1/`. If you want to check our claim for this case, you are invited to take a look at the codes, and run the following command, to reproduce our results:
```
python3 main.py
```
### RTK2

For this case we have also found a 14-round distinguisher via our MILP-based tool. The following picture shows a mathematical proof for our distinguiser. The codes we have used for this case, are placed in directory `./Zero-Correlation/ZeroCorrelation-rev1-tk2`, and if you want to run the program, and reproduce our results, you need to open your terminal in this directory, and type the following command: 
```
python3 main.py
```
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

The first observation that motivated us to begin the cryptanalysis of CRAFT, is related to the influence of clustering effect on the differential cryptanalysis of CRAFT. It dates back to that day, we added CRAFT to the CryptoSMT's cipher suite. When we was checking the corretness of our implementation we obserevd that the existing bounds for the differential effects of CRAFT that were claimed by the designers, can be dramatically improved, but we only could use CryptoSMT, or bit-oriented MILP models, for the small number of rounds, and we couldn't find a bound for large number of rounds, because SAT/SMT or MILP-based methods are not that efficient for large number of rounds. 

So we decided to find a way to overcome this problem. The first idea we used, was building a word-oriented MILP model for CRAFT, and using the obtained activity pattern to make the bit-oriented model easier, beacuse in contrast to bit-oriented MILP or SMT/SAT models, a word-oriented one can be solved very fast even for large number of rounds. As we already mentioned, we use Gurobi to solve the obtained MILP prolems. After solving the word-oriented MILP problem, we used the obtained solutions to make the bit-oriented models easier to solve. 

In other words, the obtained solutions from the word-roiented MILP problem, showed us what the activity pattern of an optimum differential trail could be, and then we substituted all passive variables in the bit-oriented models with zeros, which made the problem easier, and we could solve the bit-oriented model faster, to find a real differential trail. Another interesting fact we have found in this stage was that the activity pattern of an optimum differential trail with a fixed input/output actiity pattern is unique for CRAFT! However the problem of finding an obtimum differential trail for large number of rounds were still time consuming when we used CryptoSMT. 

We knew that CryptoSMT uses a naive approach to model differntial behaviour of a given Sbox. Therefore, we improved the Sbox encoding method used in CryptoSMT and then it could find an optimum trial very faster than before. Although we could find an optimum or (non-optimum) tril for large number of round very faster than before, but the problem of computing the differential effect for a given input/output differences were still time consuming for large number of rounds. In other words, the number of distinct optimum (and non-optimum) diffrential trails with the same input/output diffrences for CRAFT were so much that we couln't count all of them for large number of rounds. In this stage we used divide and conquer strategy! We divided a long part to some smaller pices, since we could compute the differential effect for smaller pieces efficiently. 

The following pictures, depict those smaller pieces we have used to improve differentil distiguisher of CRAFT in the single tweak setting. As you can see in these pictures, all of them are optimimum from the numuber of active Sboxes point of view. We evaluate the probability of each part spereately, and then multiply them together (according to markov assumption) to fint the probability of the whole differntial distinguisher.

![ein_even](/Images/Even/ein_even_new.svg)


![em_even](/Images/Even/em_even_new.svg)
![em_even_2r_matrix](/Results-Diff-ST/Even/em_even_2r.svg)
![em_even_4r_matrix](/Results-Diff-ST/Even/em_even_4r.svg)
![eout_even](/Images/Even/eout_even_new.svg)

![ein_odd](/Images/Odd/ein_odd_new.svg)

![em_odd](/Images/Odd/em_odd_new.svg)
![em_odd_2r_matrix](/Results-Diff-ST/Odd/em_odd_2r.svg)

![eout_odd](/Images/Odd/eout_odd_new.svg)

## Experimental Verification of Some Differential Distinguishers

Todo ...

---

## Integral Cryptanalysis Based on Division Property

Todo ...

![integral_vars](/Images/Integral/craft_integral_vars.svg)

---
