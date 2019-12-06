"""
Applying the MILP-based method to find zero-correlation distinguishers of CRAFT
Copyright (C) 2019  Hosein Hadipour

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import time
from gurobipy import *

"""
x_roundNumber_nibbleNumber_bitNumber
x_roundNumber_nibbleNumber_0: msb
x_roundNumber_nibbleNumber_3: lsb

Input mask of (i + 1)-th round:
x_i_0	x_i_1	x_i_2	x_i_3
x_i_4	x_i_5	x_i_6	x_i_7
x_i_8	x_i_9	x_i_10	x_i_11
x_i_12	x_i_13	x_i_14	x_i_15

Output mask of MC in (i + 1)-th round:
x_i_0	x_i_1	x_i_2	x_i_3
x_i_4	x_i_5	x_i_6	x_i_7
y_i_0	y_i_1	y_i_2	y_i_3
y_i_4	y_i_5	y_i_6	y_i_7

Input mask of tewak : t_nibbleNumber_bitNumber

t_0     t_1     t_2     t_3       
t_4     t_5     t_6     t_7
t_8     t_9     t_10    t_11
t_12    t_13    t_14    t_15

tweaks used in each round:

tkt_i_0	tkt_i_1	tkt_i_2	tkt_i_3
tkt_i_4	tkt_i_5	tkt_i_6	tkt_i_7
tkt_i_0	tkt_i_1	tkt_i_2	tkt_i_3
tkt_i_4	tkt_i_5	tkt_i_6	tkt_i_7

tkn_i_0	tkn_i_1	tkn_i_2	tkn_i_3
tkn_i_4	tkn_i_5	tkn_i_6	tkn_i_7
tkn_i_0	tkn_i_1	tkn_i_2	tkn_i_3
tkn_i_4	tkn_i_5	tkn_i_6	tkn_i_7

for example for 2 rounds of CRAFT we have the following branch points:

t ====|-> tkn_0 ====|-> tkn_1 ====|-> tk_n2====|->...
      |             |             |            |
      |-> tkt_0     |-> tkt_1     |-> tkt_2    |->...


Effective operation in (i + 1)'th round:
x_i ---> split points in MixColumn ---> (x_i/2 || y_i/2) --- constraints of equality of round teakey mask and state's mask
---> PermuteNibbles ---> SubNibbles ---> x_(i + 1)
|x_i| = 64, |y_i| = 32

Two linear hulls with zero correlation covering 14 rounds of CRAFT:
t:	0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 1000 0000 0000 0000 0000
y0:	0000 0000 0000 0000 0010 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000
xo:	0000 0000 0000 0000 0001 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000

t:	0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 1000 0000 0000 0000 0000
y0:	0000 0000 0000 0000 0010 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000
xo:	0000 0000 0000 0000 0100 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000
"""


class Craft:
    def __init__(self, rounds, related_tweak=0, slice_number=0):
        self.rounds = rounds
        self.related_tweak = related_tweak
        self.block_size = 64
        self.slice_number = slice_number
        self.p_permute_nibbles = [
            0xf, 0xc, 0xd, 0xe, 0xa, 0x9, 0x8, 0xb, 0x6, 0x5, 0x4, 0x7, 0x1, 0x2, 0x3, 0x0]
        self.q_permute_teakey_nibbles = [
            0xc, 0xa, 0xf, 0x5, 0xe, 0x8, 0x9, 0x2, 0xb, 0x3, 0x7, 0x4, 0x6, 0x0, 0x1, 0xd]
        if (self.related_tweak == 0):
            self.filename_model = "craft_stk_%d_%d.lp" % (
                self.rounds, self.slice_number)
            self.filename_result = "result_stk_%d_%d.txt" % (
                self.rounds, self.slice_number)
        else:
            self.filename_model = "craft_rtk_%d_%d.lp" % (
                self.rounds, self.slice_number)
            self.filename_result = "result_rtk_%d_%d.txt" % (
                self.rounds, self.slice_number)

        fileobj = open(self.filename_model, "w")
        fileobj.close()
        fileobj = open(self.filename_result, "w")
        fileobj.close()
        """
        # a0, b0, p0 : lsb
        # a3, b3, p1 : msb        
        """
        self.s_pos_ineqs = ["a3 + a2 + a1 + a0 - b0 >= 0",
                            "a3 + a2 + a1 + a0 - b2 >= 0",
                            "- a0 + b3 + b2 + b1 + b0 >= 0",
                            "- a2 + b3 + b2 + b1 + b0 >= 0",
                            "a3 + b3 - b2 + b1 - b0 >= -1",
                            "a3 - a2 + a1 - a0 + b3 >= -1",
                            "a3 + a2 + a1 + a0 - b3 >= 0",
                            "a3 + a2 + a0 - b1 >= 0",
                            "- a1 + b3 + b2 + b0 >= 0",
                            "- a3 + b3 + b2 + b1 + b0 >= 0",
                            "a3 + a0 - b3 + b2 - b1 - b0 >= -2",
                            "- a3 - a2 - a1 + a0 + b3 + b2 >= -2",
                            "a3 + a2 - b3 - b2 - b1 + b0 >= -2",
                            "a3 + a2 - b3 + b2 - b1 - b0 >= -2",
                            "- a3 + a2 - a1 - a0 + b3 + b2 >= -2",
                            "a1 + b3 - b2 - b0 >= -1",
                            "a3 + a0 - b3 - b2 - b1 + b0 >= -2",
                            "- a3 + a2 - a1 - a0 + b3 + b0 >= -2",
                            "- a3 - a2 - a1 + a0 + b3 + b0 >= -2",
                            "a3 - a2 - a0 + b1 >= -1",
                            "a3 - a2 - a1 - a0 - b2 - b0 >= -4",
                            "- a2 - a0 + b3 - b2 - b1 - b0 >= -4",
                            "a2 + a1 + a0 - b3 + b2 - b1 + b0 >= -1",
                            "- a3 + a2 - a1 + a0 + b2 + b1 + b0 >= -1",
                            "- a3 + a2 + a0 - b3 - b2 - b0 >= -3",
                            "- a3 - a2 - a0 - b3 + b2 + b0 >= -3",
                            "a2 + a0 - b2 - b1 - b0 >= -2",
                            "- a2 - a1 - a0 + b2 + b0 >= -2",
                            "- a3 - a2 + a1 - a0 - b2 - b1 - b0 >= -5",
                            "- a2 - a1 - a0 - b3 - b2 + b1 - b0 >= -5",
                            "- a3 - a2 + a0 + b3 + b2 - b1 >= -2",
                            "a3 - a1 + a0 - b3 + b2 - b0 >= -2",
                            "- a3 + a2 - a0 + b3 - b1 + b0 >= -2",
                            "a3 + a2 - a1 - b3 - b2 + b0 >= -2",
                            "a3 + a2 + a1 - b3 + b2 - b0 >= -1",
                            "- a3 + a2 - a0 + b3 + b2 + b1 >= -1",
                            "a3 + a1 + a0 - b3 - b2 + b0 >= -1",
                            "- a3 - a2 + a0 + b3 + b1 + b0 >= -1"]

    def constraints_by_sbox(self, variable1, variable2):
        """
        Generate the constraints by Sbox layer.
        """
        fileobj = open(self.filename_model, "a")
        for k in range(0, 16):
            for ineq in self.s_pos_ineqs:
                temp = ineq
                for i in range(4):
                    temp = temp.replace("a%d" % (3 - i), variable1[k][i])
                for i in range(4):
                    temp = temp.replace("b%d" % (3 - i), variable2[k][i])
                fileobj.write(temp)
                fileobj.write("\n")
        fileobj.close()

    def create_objective_function(self):
        """
        Create objective function of the MILP model.
        """
        fileobj = open(self.filename_model, "a")
        fileobj.write("Minimize\n")
        temp = "1\n"
        fileobj.write(temp)
        fileobj.close()

    @staticmethod
    def create_variables(r, s):
        """
        Generate the variables used in the model.
        """
        array = [["" for i in range(0, 4)] for j in range(0, 16)]
        for i in range(0, 16):
            for j in range(0, 4):
                array[i][j] = s + "_" + str(r) + "_" + str(i) + "_" + str(j)
        return array

    @staticmethod
    def create_variables_after_mc(r, s1, s2):
        """
        Generate the variables used in the model.
        """
        array = [["" for i in range(0, 4)] for j in range(0, 16)]
        for i in range(0, 8):
            for j in range(0, 4):
                array[i][j] = s1 + "_" + str(r) + "_" + str(i) + "_" + str(j)
                array[i + 8][j] = s2 + "_" + \
                    str(r) + "_" + str(i) + "_" + str(j)
        return array

    @staticmethod
    def create_tweak_vars(s):
        """
        Generate the initial tweak variables used in the model.
        """
        array = [["" for i in range(0, 4)] for j in range(0, 16)]
        for i in range(0, 16):
            for j in range(0, 4):
                array[i][j] = s + "_" + str(i) + "_" + str(j)
        return array

    def constraints_by_fork(self, c, a, b):
        fileobj = open(self.filename_model, "a")
        # c ---fork---> (a, b) can be modeled with 4 inequalities
        # (without definition of dummy variable) by removing
        # each impossible (a, b, c).
        ineq1 = a + " + " + b + " - " + c + " >= 0\n"
        ineq2 = a + " - " + b + " + " + c + " >= 0\n"
        ineq3 = str(-1) + " " + a + " + " + b + " + " + c + " >= 0\n"
        ineq4 = str(-1) + " " + " - ".join([a, b, c]) + " >= -2\n"
        fileobj.write(ineq1)
        fileobj.write(ineq2)
        fileobj.write(ineq3)
        fileobj.write(ineq4)
        fileobj.close()

    def constraints_by_three_fork(self, b, a2, a1, a0):
        fileobj = open(self.filename_model, "a")
        """
        b ---threeFork--> (a2, a1, a0)
        These inequalitie were obtained via LogicFriday(QM algorithm, exact)
        b - a2 - a1 - a0 >= -2
        - b + a2 - a1 - a0 >= -2
        - b - a2 + a1 - a0 >= -2
        b + a2 + a1 - a0 >= 0
        - b - a2 - a1 + a0 >= -2
        b + a2 - a1 + a0 >= 0
        b - a2 + a1 + a0 >= 0
        - b + a2 + a1 + a0 >= 0
        """
        ineq1 = b + " - " + a2 + " - " + a1 + " - " + a0 + " >= -2\n"
        ineq2 = " - " + b + " + " + a2 + " - " + a1 + " - " + a0 + " >= -2\n"
        ineq3 = " - " + b + " - " + a2 + " + " + a1 + " - " + a0 + " >= -2\n"
        ineq4 = b + " + " + a2 + " + " + a1 + " - " + a0 + " >= 0\n"
        ineq5 = " - " + b + " - " + a2 + " - " + a1 + " + " + a0 + " >= -2\n"
        ineq6 = b + " + " + a2 + " - " + a1 + " + " + a0 + " >= 0\n"
        ineq7 = b + " - " + a2 + " + " + a1 + " + " + a0 + " >= 0\n"
        ineq8 = " - " + b + " + " + a2 + " + " + a1 + " + " + a0 + " >= 0\n"
        fileobj.write(ineq1)
        fileobj.write(ineq2)
        fileobj.write(ineq3)
        fileobj.write(ineq4)
        fileobj.write(ineq5)
        fileobj.write(ineq6)
        fileobj.write(ineq7)
        fileobj.write(ineq8)
        fileobj.close()

    def state_fork(self, s, s1, s2):
        for i in range(16):
            for j in range(4):
                self.constraints_by_fork(s[i][j], s1[i][j], s2[i][j])

    def state_equality(self, s1, s2):
        fileobj = open(self.filename_model, "a")
        for i in range(16):
            for j in range(4):
                equality = s1[i][j] + " - " + s2[i][j] + " = 0\n"
                fileobj.write(equality)
        fileobj.close()

    def flatten_state(self, s):
        temp = [s[i][j] for i in range(16) for j in range(4)]
        return temp

    def constraints_by_mixing_layer(self, x, y):
        """
        Generate constraints related to mixing layer (MC)
        """
        y_offset = 8
        for nibble_number in range(4):
            for bit_number in range(4):
                self.constraints_by_three_fork(x[nibble_number + 12][bit_number], x[nibble_number + 4][bit_number],
                                               y[y_offset + nibble_number + 4][bit_number], x[nibble_number][bit_number])
                self.constraints_by_fork(x[nibble_number + 8][bit_number], x[nibble_number][bit_number],
                                         y[y_offset + nibble_number][bit_number])

    def constraints_by_atk(self, tk, xy):
        """
        Generate the constraints by AddTweakey
        """
        fileobj = open(self.filename_model, "a")
        for nibble_number in range(16):
            for bit_number in range(4):
                equality = tk[nibble_number][bit_number] + \
                    " - " + xy[nibble_number][bit_number] + " = 0\n"
                fileobj.write(equality)
        fileobj.close()

    def permute_nibbles(self, state):
        temp = [0]*16
        for i in range(16):
            temp[self.p_permute_nibbles[i]] = state[i]
        return temp

    def q_permte_nibbles(self, state):
        temp = [0]*16
        for i in range(16):
            temp[i] = state[self.q_permute_teakey_nibbles[i]]
        return temp

    def constraint(self):
        """
        Generate the constraints of MILP model
        """
        assert(1 <= self.rounds <= 32)

        fileobj = open(self.filename_model, "a")
        fileobj.write("Subject To\n")
        fileobj.close()

        x_in = self.create_variables(0, "x")
        y = self.create_variables_after_mc(0, "x", "y")
        x_out = self.create_variables(1, "x")
        t = self.create_tweak_vars("t")
        if self.rounds == 1:
            self.constraints_by_mixing_layer(x_in, y)
            if (self.related_tweak == 1):
                this_round_tk = self.create_variables(0, "tkt")
                self.constraints_by_atk(this_round_tk, y)
            self.constraints_by_sbox(self.permute_nibbles(y), x_out)
        else:
            self.constraints_by_mixing_layer(x_in, y)
            if (self.related_tweak == 1):
                this_round_tk = self.create_variables(0, "tkt")
                self.constraints_by_atk(this_round_tk, y)
            self.constraints_by_sbox(self.permute_nibbles(y), x_out)
            for r in range(1, self.rounds):
                x_in = x_out
                y = self.create_variables_after_mc(r, "x", "y")
                x_out = self.create_variables(r + 1, "x")
                self.constraints_by_mixing_layer(x_in, y)
                if (self.related_tweak == 1):
                    this_round_tk = self.create_variables(r, "tkt")
                    if (r % 4 in [0, 3]):
                        self.constraints_by_atk(
                            self.q_permte_nibbles(this_round_tk), y)
                    else:
                        self.constraints_by_atk(this_round_tk, y)
                self.constraints_by_sbox(self.permute_nibbles(y), x_out)
        if (self.related_tweak == 1):
            for r in range(self.rounds):
                if (r == 0):
                    old_tk = t
                else:
                    old_tk = self.create_variables(r - 1, "tkn")
                this_round_tk = self.create_variables(r, "tkt")
                if (r < self.rounds - 1):
                    next_tk = self.create_variables(r, "tkn")
                    self.state_fork(old_tk, this_round_tk, next_tk)
                else:
                    self.state_equality(old_tk, this_round_tk)

    # Variables declaration
    def variable_binary(self):
        """
        Specifying variables type.
        """
        fileobj = open(self.filename_model, "a")
        fileobj.write("Binary\n")
        # x
        for round_number in range(self.rounds + 1):
            for nibble_number in range(16):
                for bit_number in range(4):
                    fileobj.write("x_" + str(round_number) + "_" +
                                  str(nibble_number) + "_" + str(bit_number))
                    fileobj.write("\n")
        # y
        for round_number in range(self.rounds):
            for nibble_number in range(8):
                for bit_number in range(4):
                    fileobj.write("y_" + str(round_number) + "_" +
                                  str(nibble_number) + "_" + str(bit_number))
                    fileobj.write("\n")
        # tweak variables
        if (self.related_tweak == 1):
            for nibble_number in range(16):
                for bit_number in range(4):
                    fileobj.write("t_%d_%d\n" % (nibble_number, bit_number))
            for r in range(self.rounds):
                for nibble_number in range(16):
                    for bit_number in range(4):
                        fileobj.write("tkt_%d_%d_%d\n" %
                                      (r, nibble_number, bit_number))
                        if (r < self.rounds - 1):
                            fileobj.write("tkn_%d_%d_%d\n" %
                                          (r, nibble_number, bit_number))
        fileobj.write("END")
        fileobj.close()

    def convert_str_to_states(self, st):
        assert(len(st) == 16)
        num_of_active_nibbles = st.count("1")
        st_list = list(st)
        active_nibbles = [i for i, v in enumerate(st_list) if v == "1"]
        num_of_different_states = 16 - 1  # (16 ** num_of_active_nibbles) - 1
        nonzero_values = [list(bin(i)[2:].zfill(4)) for i in range(1, 16)]
        #comb = combinations(nonzero_values, num_of_active_nibbles)
        states = [[['0', '0', '0', '0']
                   for i in range(16)] for j in range(num_of_different_states)]
        for i in range(num_of_different_states):
            for k in range(num_of_active_nibbles):
                states[i][active_nibbles[k]] = nonzero_values[i]
        return state

    def make_model(self):
        """
        Generate the MILP model of CRAFT
        """
        self.create_objective_function()
        self.constraint()
        self.variable_binary()

    def search_masks_with_hamming_weight_of_one_stk(self):
        fileobj = open(self.filename_result, "a")
        time_start = time.time()
        self.make_model()
        m = read(self.filename_model)
        m.setParam(GRB.Param.OutputFlag, False)
        m.setParam(GRB.Param.Threads, 32)

        y_in = self.create_variables_after_mc(0, "x", "y")
        x_out = self.create_variables(self.rounds, "x")

        y_in = self.flatten_state(y_in)
        x_out = self.flatten_state(x_out)

        y_in = [m.getVarByName(y) for y in y_in]
        x_out = [m.getVarByName(x) for x in x_out]

        total_tests = 64 * 64
        counter = 0
        for i in range(0, 64):
            y = list(bin(1 << i)[2:].zfill(64))
            temporary_constraints1 = m.addConstrs(
                (y_in[k] == int(y[k]) for k in range(64)), name='temp_constraints1')
            for j in range(0, 64):
                x = list(bin(1 << j)[2:].zfill(64))
                temporary_constraints2 = m.addConstrs(
                    (x_out[k] == int(x[k]) for k in range(64)), name='temp_constraints2')
                m.optimize()
                if (m.Status == GRB.Status.INFEASIBLE):
                    y_temp = ["".join(y[4*ind:4*ind+4]) for ind in range(16)]
                    y_temp = " ".join(y_temp)
                    line1 = "y0:\t%s\n" % "".join(y_temp)
                    x_temp = ["".join(x[4*ind:4*ind+4]) for ind in range(16)]
                    x_temp = " ".join(x_temp)
                    line2 = "xo:\t%s\n" % "".join(x_temp)
                    fileobj.write(line1)
                    fileobj.write(line2)
                    fileobj.write("\n")
                    print(line1)
                    print(line2)
                    print("\n")
                m.remove(temporary_constraints2)
                # m.update()
                counter += 1
                print("%d/%d" % (counter, total_tests))
            m.remove(temporary_constraints1)
        time_end = time.time()
        print(("Time used = " + str(time_end - time_start)))
        fileobj.close()

    def search_masks_with_hamming_weight_of_one_rtk(self):
        fileobj = open(self.filename_result, "a")
        time_start = time.time()
        self.make_model()
        m = read(self.filename_model)
        m.setParam(GRB.Param.OutputFlag, False)
        m.setParam(GRB.Param.Threads, 32)
        m.setParam(GRB.Param.Presolve, 0)

        y_in = self.create_variables_after_mc(0, "x", "y")
        x_out = self.create_variables(self.rounds, "x")
        tweak = self.create_tweak_vars("t")

        y_in = self.flatten_state(y_in)
        x_out = self.flatten_state(x_out)
        tweak = self.flatten_state(tweak)

        y_in = [m.getVarByName(y) for y in y_in]
        x_out = [m.getVarByName(x) for x in x_out]
        tweak = [m.getVarByName(t) for t in tweak]

        total_tests = 64 * 64 * 4
        counter = 0
        zc_counter = 0
        for n in range(0 + 4*self.slice_number, 4 + 4*self.slice_number):
            t = list(bin(1 << n)[2:].zfill(64))
            temporary_constraints0 = m.addConstrs(
                (tweak[k] == int(t[k]) for k in range(64)), name='temp_constraints0')
            for i in range(0, 64):
                y = list(bin(1 << i)[2:].zfill(64))
                temporary_constraints1 = m.addConstrs(
                    (y_in[k] == int(y[k]) for k in range(64)), name='temp_constraints1')
                for j in range(0, 64):
                    x = list(bin(1 << j)[2:].zfill(64))
                    temporary_constraints2 = m.addConstrs(
                        (x_out[k] == int(x[k]) for k in range(64)), name='temp_constraints2')
                    m.optimize()
                    if (m.Status == GRB.Status.INFEASIBLE):
                        t_temp = ["".join(t[4*ind:4*ind+4])
                                  for ind in range(16)]
                        t_temp = " ".join(t_temp)
                        line0 = "t:\t%s" % "".join(t_temp)
                        y_temp = ["".join(y[4*ind:4*ind+4])
                                  for ind in range(16)]
                        y_temp = " ".join(y_temp)
                        line1 = "y0:\t%s" % "".join(y_temp)
                        x_temp = ["".join(x[4*ind:4*ind+4])
                                  for ind in range(16)]
                        x_temp = " ".join(x_temp)
                        line2 = "xo:\t%s" % "".join(x_temp)
                        fileobj.write(line0 + "\n")
                        fileobj.write(line1 + "\n")
                        fileobj.write(line2 + "\n")
                        fileobj.write("\n")
                        zc_counter += 1
                        print(line0)
                        print(line1)
                        print(line2)
                        print("\n")
                    m.remove(temporary_constraints2)
                    m.update()
                    counter += 1
                    print("%d/%d \t #ZC : %d" %
                          (counter, total_tests, zc_counter))
                m.remove(temporary_constraints1)
            m.remove(temporary_constraints0)
        time_end = time.time()
        print(("Time used = " + str(time_end - time_start)))
        fileobj.close()
    
    def search_for_fixed_activity_pattern_st(self, si_target_nibble, so_target_nibble):
        fileobj = open(self.filename_result, "a")
        time_start = time.time()
        
        self.make_model()
        m = read(self.filename_model)
        m.setParam(GRB.Param.OutputFlag, False)
        m.setParam(GRB.Param.Threads, 32)
        m.setParam(GRB.Param.Presolve, 0)

        y_in = self.create_variables_after_mc(0, "x", "y")
        x_out = self.create_variables(self.rounds, "x")        

        y_in = self.flatten_state(y_in)
        x_out = self.flatten_state(x_out)

        y_in = [m.getVarByName(y) for y in y_in]
        x_out = [m.getVarByName(x) for x in x_out]

        total_tests = 15*15
        cnt = 0
        zc_counter = 0
        
        for i in range(1, 16):
            si = ['0' for ind in range(64)]
            si[4*si_target_nibble: 4*si_target_nibble +
                4] = list(bin(i)[2:].zfill(4))
            temporary_constraints1 = m.addConstrs(
                (y_in[k] == int(si[k]) for k in range(64)), name='temp_constraints1')
            for j in range(1, 16):
                so = ['0' for ind in range(64)]
                so[4*so_target_nibble: 4*so_target_nibble +
                    4] = list(bin(j)[2:].zfill(4))
                temporary_constraints2 = m.addConstrs(
                    (x_out[k] == int(so[k]) for k in range(64)), name='temp_constraints2')                
                m.optimize()
                cnt += 1
                if (m.Status == GRB.Status.INFEASIBLE):
                    temp_si = ["".join(si[4*ind:4*ind+4]) for ind in range(16)]
                    temp_so = ["".join(so[4*ind:4*ind+4]) for ind in range(16)]
                    line1 = "y0:\t%s" % " ".join(temp_si)
                    line2 = "xo:\t%s" % " ".join(temp_so)
                    fileobj.write(line1 + "\n")
                    fileobj.write(line2 + "\n")
                    fileobj.write("\n")
                    print(line1)
                    print(line2)
                    zc_counter += 1
                    #m.computeIIS()
                    #m.write("out%d.ilp" % zc_counter)
                print("%d / %d \t #ZC : %d" % (cnt, total_tests, zc_counter))
                fileobj.write("%d / %d \t #ZC : %d\n" %
                              (cnt, total_tests, zc_counter))
                m.remove(temporary_constraints2)
                m.update()
            m.remove(temporary_constraints1)
        time_end = time.time()
        print(("Time used = " + str(time_end - time_start)))
        fileobj.close()

    def get_value_of_master_tweak_variables(self, m):        
        v_names = self.create_tweak_vars("t")
        v_names = self.flatten_state(v_names)
        temp = map(m.getVarByName, v_names)
        v_values = [str(int(e.X)) for e in temp]
        temp_values = []
        for i in range(16):
            temp = "".join(v_values[i*4: i*4 + 4])
            temp = int(temp, 2)
            temp = hex(temp)[2:]
            temp_values.append(temp)
        temp_values = "%s:\t%s" % ("t", "".join(temp_values))
        return temp_values

    def get_value_of_tweak_variables(self, m, s, r):        
        v_names = self.create_variables(r, s)        
        if ((r % 4) in [0, 3]):
            v_names = self.q_permte_nibbles(v_names)        
        v_names = self.flatten_state(v_names)
        temp = map(m.getVarByName, v_names)
        v_values = [str(int(e.X)) for e in temp]
        temp_values = []
        for i in range(16):
            temp = "".join(v_values[i*4: i*4 + 4])
            temp = int(temp, 2)
            temp = hex(temp)[2:]
            temp_values.append(temp)
        temp_values = "%s%d:\t%s" % (s, r, "".join(temp_values))
        return temp_values  

    def get_value_of_variables(self, m, s, r):        
        v_names = self.create_variables(r, s)
        v_names = self.flatten_state(v_names)
        temp = map(m.getVarByName, v_names)
        v_values = [str(int(e.X)) for e in temp]
        temp_values = []
        for i in range(16):
            temp = "".join(v_values[i*4: i*4 + 4])
            temp = int(temp, 2)
            temp = hex(temp)[2:]
            temp_values.append(temp)
        temp_values = "%s%d:\t%s" % (s, r, "".join(temp_values))
        return temp_values        
    
    def get_value_of_mixcol_output_vars(self, m, s1, s2, r):
        v_names = self.create_variables_after_mc(r, s1, s2)
        v_names = self.flatten_state(v_names)
        temp = map(m.getVarByName, v_names)
        v_values = [str(int(e.X)) for e in temp]
        temp_values = []
        for i in range(16):
            temp = "".join(v_values[i*4: i*4 + 4])
            temp = int(temp, 2)
            temp = hex(temp)[2:]
            temp_values.append(temp)
        temp_values = "%s%d:\t%s" % (s2, r, "".join(temp_values))
        return temp_values

    def search_for_fixed_tweak_and_fixed_activity_pattern(self, si_target_nibble, so_target_nibble):
        fileobj = open(self.filename_result, "a")
        time_start = time.time()
        #t = list("0000000000000000000000000000000000000000000000000000000000000000")
        t = list("1111111111111111111111111111111111111111111100001111111111111111")
        #t = list("0000000000000000000000000000000000000000000010000000000000000000")
        #t = list("0000000000000000000000000000000000000000000000001000000000000000")
        self.make_model()
        m = read(self.filename_model)
        m.setParam(GRB.Param.OutputFlag, False)
        m.setParam(GRB.Param.Threads, 32)
        m.setParam(GRB.Param.Presolve, 0)

        y_in = self.create_variables_after_mc(0, "x", "y")
        x_out = self.create_variables(self.rounds, "x")
        tweak = self.create_tweak_vars("t")

        y_in = self.flatten_state(y_in)
        x_out = self.flatten_state(x_out)
        tweak = self.flatten_state(tweak)

        y_in = [m.getVarByName(y) for y in y_in]
        x_out = [m.getVarByName(x) for x in x_out]
        tweak = [m.getVarByName(t) for t in tweak]

        total_tests = 15*15
        cnt = 0
        zc_counter = 0

        #temporary_constraints0 = m.addConstrs((tweak[k] == int(t[k]) for k in range(64)), name='temp_constraints0')
        temporary_constraints0 = m.addConstrs(
            (tweak[k] == int(t[k]) for k in range(64)), name='temp_constraints0')
        temp_t = ["".join(t[4*ind:4*ind+4]) for ind in range(16)]
        temp_t = " ".join(temp_t)
        line0 = "t:\t%s" % temp_t
        for i in range(1, 16):
            si = ['0' for ind in range(64)]
            si[4*si_target_nibble: 4*si_target_nibble +
                4] = list(bin(i)[2:].zfill(4))
            temporary_constraints1 = m.addConstrs(
                (y_in[k] == int(si[k]) for k in range(64)), name='temp_constraints1')
            for j in range(1, 16):
                so = ['0' for ind in range(64)]
                so[4*so_target_nibble: 4*so_target_nibble +
                    4] = list(bin(j)[2:].zfill(4))
                temporary_constraints2 = m.addConstrs(
                    (x_out[k] == int(so[k]) for k in range(64)), name='temp_constraints2')                
                m.optimize()
                cnt += 1
                if (m.Status == GRB.Status.INFEASIBLE):
                    temp_si = ["".join(si[4*ind:4*ind+4]) for ind in range(16)]
                    temp_so = ["".join(so[4*ind:4*ind+4]) for ind in range(16)]
                    line1 = "y0:\t%s" % " ".join(temp_si)
                    line2 = "xo:\t%s" % " ".join(temp_so)
                    fileobj.write(line0 + "\n")
                    fileobj.write(line1 + "\n")
                    fileobj.write(line2 + "\n")
                    fileobj.write("\n")
                    print(line0)
                    print(line1)
                    print(line2)
                    zc_counter += 1
                    #m.computeIIS()
                    #m.write("out%d.ilp" % zc_counter)
                if (m.Status == 2):
                    temp0 = self.get_value_of_master_tweak_variables(m)
                    print(temp0)
                    for r in range(self.rounds + 1):                        
                        temp1 = self.get_value_of_variables(m, "x", r)                        
                        if (r < self.rounds):
                            temp3 = self.get_value_of_tweak_variables(m, "tkt", r)
                            temp2 = self.get_value_of_mixcol_output_vars(m, "x", "y", r)
                            print("%s \t %s \t %s" % (temp1, temp2, temp3))
                        else:
                            print("%s" % temp1)
                print("%d / %d \t #ZC : %d" % (cnt, total_tests, zc_counter))
                fileobj.write("%d / %d \t #ZC : %d\n" %
                              (cnt, total_tests, zc_counter))
                m.remove(temporary_constraints2)
                m.update()
            m.remove(temporary_constraints1)
        time_end = time.time()
        print(("Time used = " + str(time_end - time_start)))
        fileobj.close()

    def search_for_fixed_activity_pattern_rtk(self, tweak_target_nibble, si_target_nibble, so_target_nibble):
        fileobj = open(self.filename_result, "a")
        time_start = time.time()
        self.make_model()
        m = read(self.filename_model)
        m.setParam(GRB.Param.OutputFlag, True)
        m.setParam(GRB.Param.Threads, 32)

        y_in = self.create_variables_after_mc(0, "x", "y")
        x_out = self.create_variables(self.rounds, "x")
        tweak = self.create_tweak_vars("t")

        y_in = self.flatten_state(y_in)
        x_out = self.flatten_state(x_out)
        tweak = self.flatten_state(tweak)

        y_in = [m.getVarByName(y) for y in y_in]
        x_out = [m.getVarByName(x) for x in x_out]
        tweak = [m.getVarByName(t) for t in tweak]

        total_tests = 15*15*15
        cnt = 0
        zc_counter = 0
        for n in range(1, 16):
            t = ['0' for ind in range(64)]
            t[4*tweak_target_nibble: 4*tweak_target_nibble +
                4] = list(bin(n)[2:].zfill(4))
            temporary_constraints0 = m.addConstrs(
                (tweak[k] == int(t[k]) for k in range(64)), name='temp_constraints0')
            for i in range(1, 16):
                si = ['0' for ind in range(64)]
                si[4*si_target_nibble: 4*si_target_nibble +
                    4] = list(bin(i)[2:].zfill(4))
                temporary_constraints1 = m.addConstrs(
                    (y_in[k] == int(si[k]) for k in range(64)), name='temp_constraints1')
                for j in range(1, 16):
                    so = ['0' for ind in range(64)]
                    so[4*so_target_nibble: 4*so_target_nibble +
                        4] = list(bin(j)[2:].zfill(4))
                    temporary_constraints2 = m.addConstrs(
                        (x_out[k] == int(so[k]) for k in range(64)), name='temp_constraints2')
                    m.optimize()
                    cnt += 1
                    if (m.Status == GRB.Status.INFEASIBLE):
                        temp_t = ["".join(t[4*ind:4*ind+4])
                                  for ind in range(16)]
                        temp_si = ["".join(si[4*ind:4*ind+4])
                                   for ind in range(16)]
                        temp_so = ["".join(so[4*ind:4*ind+4])
                                   for ind in range(16)]
                        line0 = "t:\t%s" % " ".join(temp_t)
                        line1 = "y0:\t%s" % " ".join(temp_si)
                        line2 = "xo:\t%s" % " ".join(temp_so)
                        fileobj.write(line0 + "\n")
                        fileobj.write(line1 + "\n")
                        fileobj.write(line2 + "\n")
                        fileobj.write("\n")
                        print(line0)
                        print(line1)
                        print(line2)
                        zc_counter += 1
                    print("%d / %d \t #ZC : %d" %
                          (cnt, total_tests, zc_counter))
                    m.remove(temporary_constraints2)
                    m.update()
                m.remove(temporary_constraints1)
            m.renove(temporary_constraints0)
        time_end = time.time()
        print(("Time used = " + str(time_end - time_start)))
        fileobj.close()
##################################################################

    def search_for_fixed_tweak_and_fixed_activity_pattern_file(self, si_target_nibble, so_target_nibble):
        fileobj_result = open(self.filename_result, "a")        
        time_start = time.time()
        #t = list("0000000000000000000000000000000000000000000010000000000000000000")
        t = list("1111111111111111111111111111111111111111111111011111111111111111")                    

        y_in = self.create_variables_after_mc(0, "x", "y")
        y_in = self.flatten_state(y_in)

        x_out = self.create_variables(self.rounds, "x")
        x_out = self.flatten_state(x_out)

        tweak = self.create_tweak_vars("t")                
        tweak = self.flatten_state(tweak)

        total_tests = 15*15
        cnt = 0
        zc_counter = 0
        
        for i in range(1, 16):
            
            si = ['0' for ind in range(64)]
            si[4*si_target_nibble: 4*si_target_nibble +
                4] = list(bin(i)[2:].zfill(4))
            for j in range(1, 16):                
                so = ['0' for ind in range(64)]
                so[4*so_target_nibble: 4*so_target_nibble +
                    4] = list(bin(j)[2:].zfill(4))
                #--------------------------------------------------------
                fileobj_model = open(self.filename_model, "w")
                fileobj_model.close()
                #self.create_objective_function()
                self.constraint()
                fileobj_model = open(self.filename_model, "a")
                for k in range(64):
                    fileobj_model.write("%s = %s\n" % (y_in[k], si[k]))
                for k in range(64):
                    fileobj_model.write("%s = %s\n" % (x_out[k], so[k]))
                for k in range(64):
                    fileobj_model.write("%s = %s\n" % (tweak[k], t[k]))
                fileobj_model.close()
                self.variable_binary()                
                #---------------------------------------------------------
                m = read(self.filename_model)
                m.setParam(GRB.Param.OutputFlag, False)
                m.setParam(GRB.Param.Threads, 32)
                m.optimize()                
                cnt += 1
                if (m.Status == 3):
                    #GRB.Status.INFEASIBLE
                    temp_si = ["".join(si[4*ind:4*ind+4]) for ind in range(16)]
                    temp_so = ["".join(so[4*ind:4*ind+4]) for ind in range(16)]
                    temp_t = ["".join(t[4*ind:4*ind+4]) for ind in range(16)]
                    line0 = "t:\t%s" % " ".join(temp_t)
                    line1 = "y0:\t%s" % " ".join(temp_si)
                    line2 = "xo:\t%s" % " ".join(temp_so)
                    fileobj_result.write(line0 + "\n")
                    fileobj_result.write(line1 + "\n")
                    fileobj_result.write(line2 + "\n")
                    fileobj_result.write("\n")
                    print(line0)
                    print(line1)
                    print(line2)
                    #m.computeIIS()
                    #m.write("out.ilp")
                    zc_counter += 1
                print("%d / %d \t #ZC : %d" % (cnt, total_tests, zc_counter))
                #print(m.Status)
                fileobj_result.write("%d / %d \t #ZC : %d\n" %
                              (cnt, total_tests, zc_counter))
        time_end = time.time()
        print(("Time used = " + str(time_end - time_start)))
        fileobj_result.close()
