'''
Applying the MILP-based method to find zero-correlation distinguishers of CRAFT
Copyright (C) March 7, 2019  Hosein Hadipour

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

16 Esfand, 1397
'''

import time
from gurobipy import *
"""
x_roundNumber_nibbleNumber_bitNumber
x_roundNumber_nibbleNumber_0: msb
x_roundNumber_nibbleNumber_3: lsb


Input of (i + 1)-th round:
x_i_0	x_i_1	x_i_2	x_i_3
x_i_4	x_i_5	x_i_6	x_i_7
x_i_8	x_i_9	x_i_10	x_i_11
x_i_12	x_i_13	x_i_14	x_i_15

Output of MC in (i + 1)-th round:
y_i_0	y_i_1	y_i_2	y_i_3
y_i_4	y_i_5	y_i_6	y_i_7
x_i_8	x_i_9	x_i_10	x_i_11
x_i_12	x_i_13	x_i_14	x_i_15

Output of AddTweakey in (i + 1)-th round:
z_i_0	z_i_1	z_i_2	z_i_3
z_i_4	z_i_5	z_i_6	z_i_7
z_i_8	z_i_9	z_i_10	z_i_11
z_i_12	z_i_13	z_i_14	z_i_15

SBox indicators variables:
q_roundNumber_nibbleNumber
q3_roundNumber_nibbleNumber
q2_roundNumber_nibbleNumber
q_roundNumber_nibbleNumber = q3_roundNumber_nibbleNumber + q2_roundNumber_nibbleNumber
Objective function: Minimize Sum(2 q_2 + 3 q_3)
"""


class Craft:
    def __init__(self, rounds, related_tweak=0):
        self.rounds = rounds
        self.big_m = 2*8
        # self.dummy_var_index = 0
        self.related_tweak = related_tweak
        self.block_size = 64
        self.p_permute_nibbles = [
            0xf, 0xc, 0xd, 0xe, 0xa, 0x9, 0x8, 0xb, 0x6, 0x5, 0x4, 0x7, 0x1, 0x2, 0x3, 0x0]
        self.q_permute_teakey_nibbles = [
            0xc, 0xa, 0xf, 0x5, 0xe, 0x8, 0x9, 0x2, 0xb, 0x3, 0x7, 0x4, 0x6, 0x0, 0x1, 0xd]
        self.TK = [[[0] for _ in range(16)] for _ in range(4)]
        self.tweak = [["tk_" + str(nibble_number) + "_" + str(bit_number) for bit_number in range(4)]
                      for nibble_number in range(16)]
        if (self.related_tweak == 0):
            self.filename_model = "craft" + "_s_" + str(self.rounds) + ".lp"
            self.filename_result = "result" + \
                "_s_" + str(self.rounds) + ".txt"
        else:
            self.filename_model = "craft" + "_r_" + str(self.rounds) + ".lp"
            self.filename_result = "result" + \
                "_r_" + str(self.rounds) + ".txt"
        fileobj = open(self.filename_model, "w")
        fileobj.close()
        fileobj = open(self.filename_result, "w")
        fileobj.close()

        self.s_3_pos_ineqs = [[0, 0, -1, 1, 0, 1, -1, 0, -1],
                              [0, 1, -1, 0, 0, 0, -1, 1, -1],
                              [1, 1, 0, 1, 0, 0, 0, 0, 1],
                              [0, 0, 0, 0, 1, 1, 0, 1, 1],
                              [0, 1, -1, 0, 0, 1, -1, 0, -1],
                              [0, 0, -1, 1, 0, 0, -1, 1, -1],
                              [0, 1, 0, 1, 0, 1, 0, 1, 1],
                              [0, 1, 0, 1, 0, -1, 0, -1, -1],
                              [1, 1, 1, 0, -1, 0, 0, -1, -1],
                              [-1, 0, 0, -1, 1, 1, 1, 0, -1],
                              [1, 0, 1, 1, -1, -1, 0, 0, -1],
                              [-1, -1, 0, 0, 1, 0, 1, 1, -1],
                              [0, -1, 0, -1, 0, 1, 0, 1, -1],
                              [0, -1, 0, -1, 0, -1, 0, -1, -3],
                              [0, 0, 1, 0, -1, -1, 0, -1, -2],
                              [-1, -1, 0, -1, 0, 0, 1, 0, -2],
                              [1, 0, 1, -1, 0, 1, -1, 0, -1],
                              [0, -1, -1, -1, 0, 0, 1, 0, -2],
                              [0, 0, -1, 1, 1, -1, 1, 0, -1],
                              [0, 0, 1, 0, 0, -1, -1, -1, -2],
                              [0, 1, -1, 0, 1, 0, 1, -1, -1],
                              [1, -1, 1, 0, 0, 0, -1, 1, -1],
                              [-1, -1, 0, 1, 0, 1, -1, 0, -2],
                              [0, 0, -1, 1, -1, 1, 0, -1, -2],
                              [-1, 1, 0, -1, 0, 0, -1, 1, -2],
                              [0, 1, -1, 0, -1, -1, 0, 1, -2],
                              [-1, -1, 1, 1, 1, 1, 0, 0, -1],
                              [1, 0, 0, 1, -1, 1, 1, -1, -1],
                              [-1, 1, 1, -1, 1, 0, 0, 1, -1],
                              [1, 1, 0, 0, -1, -1, 1, 1, -1]]

        self.s_2_pos_ineqs = [[0, 0, 1, 0, 0, 0, 1, 0, 1],
                              [0, 0, 0, 1, 1, -1, -1, 0, -1],
                              [1, 0, -1, 0, -1, 0, -1, 0, -2],
                              [0, 1, 0, 0, 1, 0, -1, -1, -1],
                              [0, 0, 1, 0, 0, -1, 0, 1, 0],
                              [0, 1, 1, 1, 0, 0, 0, 0, 1],
                              [0, 0, -1, 0, 1, 1, 0, 1, 0],
                              [1, 0, 0, 1, 0, -1, 0, -1, -1],
                              [-1, 0, 0, 1, 0, 1, 0, -1, -1],
                              [-1, -1, 0, 0, 0, 0, 1, 0, -1],
                              [0, 1, 0, -1, 0, 0, 1, 0, 0],
                              [0, -1, 0, -1, 0, 1, 0, -1, -2],
                              [0, -1, 0, 1, -1, 1, 0, 0, -1],
                              [0, -1, 0, -1, 1, 0, 0, 1, -1],
                              [0, 0, 1, 0, -1, 0, 0, -1, -1],
                              [0, -1, 0, 0, 0, 1, 1, 0, 0],
                              [-1, 0, 0, -1, 0, -1, 0, 1, -2],
                              [0, 1, 0, -1, -1, 0, 0, 1, -1],
                              [-1, 1, 0, 0, 0, -1, 0, 1, -1],
                              [0, -1, 0, 0, 0, 0, 1, 1, 0],
                              [0, 0, -1, 0, 1, -1, -1, -1, -3],
                              [0, -1, 0, 1, 0, -1, 0, -1, -2],
                              [0, 0, 0, 0, 0, 1, 1, 1, 1],
                              [0, 1, 0, -1, 0, -1, 0, -1, -2],
                              [0, 0, 1, 0, 0, 1, 0, -1, 0]]

    def initialize_tweakey_differences(self):
        for nibble_number in range(16):
            self.TK[0][nibble_number] = self.tweak[nibble_number]
            self.TK[1][nibble_number] = self.tweak[nibble_number]
            self.TK[2][nibble_number] = self.tweak[self.q_permute_teakey_nibbles[nibble_number]]
            self.TK[3][nibble_number] = self.tweak[self.q_permute_teakey_nibbles[nibble_number]]

    def create_objective_function(self):
        """
        Create objective function of the MILP model.
        """
        fileobj = open(self.filename_model, "a")
        fileobj.write("Minimize\n")
        minus_log_p1 = ["3 q3_" + str(round_number) + "_" + str(nibble_number)
                        for round_number in range(self.rounds) for nibble_number in range(16)]
        minus_log_p2 = ["2 q2_" + str(round_number) + "_" + str(nibble_number)
                        for round_number in range(self.rounds) for nibble_number in range(16)]
        temp = " + ".join(minus_log_p1 + minus_log_p2)
        fileobj.write(temp)
        fileobj.write("\n")
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
        for i in range(8, 16):
            for j in range(0, 4):
                array[i][j] = s2 + "_" + str(r) + "_" + str(i) + "_" + str(j)
        return array

    def constraints_by_xor(self, a, b, c):
        fileobj = open(self.filename_model, "a")
        # a XOR b = c can be modeled with 4 inequalities
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

    def constraints_by_xor3(self, b, a2, a1, a0):
        fileobj = open(self.filename_model, "a")
        """
        These inequalities are obtained with LogicFriday(QM algorithm, exact)
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

    def constraints_by_mixing_layer(self, x, y):
        """
        Generate constraints related to mixing layer (MC)
        """
        for nibble_number in range(4):
            for bit_number in range(4):
                self.constraints_by_xor3(y[nibble_number][bit_number], x[nibble_number + 8][bit_number],
                                         x[nibble_number + 12][bit_number], x[nibble_number][bit_number])
                self.constraints_by_xor(x[nibble_number + 4][bit_number], x[nibble_number + 12][bit_number],
                                        y[nibble_number + 4][bit_number])

    def constraints_by_atk(self, tk, y, z):
        """
        Generate the constraints by AddTweakey
        """
        for nibble_number in range(16):
            for bit_number in range(4):
                self.constraints_by_xor(tk[nibble_number][bit_number], y[nibble_number][bit_number],
                                        z[nibble_number][bit_number])

    def permute_nibbles(self, state):
        temp = [0]*16
        for i in range(16):
            temp[self.p_permute_nibbles[i]] = state[i]
        return temp

    def constraints_by_sbox(self, variable1, variable2, r):
        """
        Generate the constraints by Sbox layer.
        """
        fileobj = open(self.filename_model, "a")

        for k in range(0, 16):
            # k = nibble number
            for c in self.s_3_pos_ineqs:
                temp = []
                for u in range(0, 4):
                    temp.append(str(c[u]) + " " + variable1[k][u])
                for v in range(0, 4):
                    temp.append(str(c[4 + v]) + " " + variable2[k][v])
                temp = " + ".join(temp)
                temp = temp.replace("+ -", "- ")
                # s = str(-self.big_m - c[8])
                s = str(c[8] - self.big_m)
                q3 = " q3_" + str(r) + "_" + str(k)
                temp += " - " + str(self.big_m) + q3
                temp += " >= " + s
                fileobj.write(temp)
                fileobj.write("\n")
        for k in range(0, 16):
            for c in self.s_2_pos_ineqs:
                temp = []
                for u in range(0, 4):
                    temp.append(str(c[u]) + " " + variable1[k][u])
                for v in range(0, 4):
                    temp.append(str(c[4 + v]) + " " + variable2[k][v])
                temp = " + ".join(temp)
                temp = temp.replace("+ -", "- ")
                # s = str(-self.big_m - c[8])
                s = str(c[8] - self.big_m)
                q2 = " q2_" + str(r) + "_" + str(k)
                temp += " - " + str(self.big_m) + q2
                temp += " >= " + s
                fileobj.write(temp)
                fileobj.write("\n")
        q3 = ["q3_" + str(r) + "_" + str(nibble_number)
              for nibble_number in range(16)]
        q2 = ["q2_" + str(r) + "_" + str(nibble_number)
              for nibble_number in range(16)]
        q = ["q_" + str(r) + "_" + str(nibble_number)
             for nibble_number in range(16)]
        for nibble_number in range(16):
            temp = " - ".join([q[nibble_number],
                               q3[nibble_number], q2[nibble_number]]) + " = 0\n"
            fileobj.write(temp)
            for bit_number in range(4):
                temp = q[nibble_number] + " - " + \
                    variable1[nibble_number][bit_number] + " >= 0\n"
                fileobj.write(temp)
            temp = " + ".join(variable1[nibble_number]) + \
                " - " + q[nibble_number] + " >= 0\n"
            fileobj.write(temp)
            # For a bijective S-box we have:
            temp = " + 4 ".join(variable2[nibble_number])
            temp = "4 " + temp
            temp += " - " + " - ".join(variable1[nibble_number]) + " >= 0\n"
            fileobj.write(temp)
            temp = " + 4 ".join(variable1[nibble_number])
            temp = "4 " + temp
            temp += " - " + " - ".join(variable2[nibble_number]) + " >= 0\n"
            fileobj.write(temp)
        fileobj.close()

    def constraint(self):
        """
        Generate the constraints of MILP model
        """
        assert(1 <= self.rounds <= 32)
        fileobj = open(self.filename_model, "a")
        fileobj.write("Subject To\n")
        fileobj.close()
        x_in = self.create_variables(0, "x")
        y = self.create_variables_after_mc(0, "y", "x")
        z = self.create_variables(0, "z")
        x_out = self.create_variables(1, "x")
        if self.rounds == 1:
            self.constraints_by_mixing_layer(x_in, y)
            if (self.related_tweak == 1):
                self.constraints_by_atk(self.TK[1], y, z)
                self.constraints_by_sbox(self.permute_nibbles(z), x_out, 0)
            else:
                self.constraints_by_sbox(self.permute_nibbles(y), x_out, 0)
        else:
            self.constraints_by_mixing_layer(x_in, y)
            if (self.related_tweak == 1):
                self.constraints_by_atk(self.TK[0], y, z)
                self.constraints_by_sbox(self.permute_nibbles(z), x_out, 0)
            else:
                self.constraints_by_sbox(self.permute_nibbles(y), x_out, 0)
            for r in range(1, self.rounds):
                x_in = x_out
                y = self.create_variables_after_mc(r, "y", "x")
                z = self.create_variables(r, "z")
                x_out = self.create_variables(r + 1, "x")
                if (self.related_tweak == 1):
                    self.constraints_by_mixing_layer(x_in, y)
                    self.constraints_by_atk(self.TK[r % 4], y, z)
                else:
                    self.constraints_by_mixing_layer(x_in, y)
                if r != 31:
                    if (self.related_tweak == 1):
                        self.constraints_by_sbox(
                            self.permute_nibbles(z), x_out, r)
                    else:
                        self.constraints_by_sbox(
                            self.permute_nibbles(y), x_out, r)

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
        # z
        if (self.related_tweak == 1):
            for round_number in range(self.rounds):
                for nibble_number in range(16):
                    for bit_number in range(4):
                        fileobj.write("z_" + str(round_number) + "_" +
                                      str(nibble_number) + "_" + str(bit_number))
                        fileobj.write("\n")
        # q, q2, q3
        for round_number in range(self.rounds):
            for nibble_number in range(16):
                temp1 = "q_" + str(round_number) + "_" + \
                    str(nibble_number) + "\n"
                temp2 = "q2_" + str(round_number) + "_" + \
                    str(nibble_number) + "\n"
                temp3 = "q3_" + str(round_number) + "_" + \
                    str(nibble_number) + "\n"
                fileobj.write(temp1)
                fileobj.write(temp2)
                fileobj.write(temp3)

        # tk
        if (self.related_tweak == 1):
            for nibble_number in range(16):
                for bit_number in range(4):
                    fileobj.write("tk_" + str(nibble_number) +
                                  "_" + str(bit_number))
                    fileobj.write("\n")

        fileobj.write("END")
        fileobj.close()

    def init(self):
        """
        Generate the initial constraints induced by the initial constraints
        """
        fileobj = open(self.filename_model, "a")
        x0 = self.create_variables(0, "x")
        x_in = [x0[i][j] for i in range(16) for j in range(4)]
        tk = [self.tweak[i][j] for i in range(16) for j in range(4)]
        x_condition = " + ".join(x_in) + " >= 1"
        fileobj.write(x_condition)
        fileobj.write("\n")
        if (self.related_tweak == 1):
            tweak_condition = " + ".join(tk) + " >= 0"
            fileobj.write(tweak_condition)
            fileobj.write("\n")
        fileobj.close()

    def make_model(self):
        """
        Generate the MILP model of CRAFT
        """
        if (self.related_tweak == 1):
            self.initialize_tweakey_differences()
        self.create_objective_function()
        self.constraint()
        self.init()
        self.variable_binary()

    def write_objective(self, obj):
        """
        Write the objective value into filename_result.
        """
        fileobj = open(self.filename_result, "a")
        fileobj.write("The objective value = %d\n" % obj.getValue())
        eqn1 = []
        eqn2 = []
        for i in range(0, self.block_size):
            u = obj.getVar(i)
            if u.getAttr("x") != 0:
                eqn1.append(u.getAttr('VarName'))
                eqn2.append(u.getAttr('x'))
        length = len(eqn1)
        for i in range(0, length):
            s = eqn1[i] + "=" + str(eqn2[i])
            fileobj.write(s)
            fileobj.write("\n")
        fileobj.close()

    def solve_model(self):
        """
        Solve the MILP model to search the integral distinguisher of MIBS.
        """
        time_start = time.time()
        m = read(self.filename_model)
        m.setParam(GRB.Param.Threads, 16)
        m.optimize()
        # Gurobi syntax: m.Status == 2 represents the model is feasible.
        if m.Status == 2:
            obj = m.getObjective()
            print("\nMaximum probability of differential characteristic for %s rounds : 2^-(%s)" %
                  (self.rounds, obj.getValue()))
            print("\nDifferential trail:\n")
            for r in range(self.rounds + 1):
                v_names = ["x_" + str(r) + "_" + str(nibble_number) + "_" + str(bit_number)
                           for nibble_number in range(16) for bit_number in range(4)]
                temp = map(m.getVarByName, v_names)
                v_values = [str(int(e.X)) for e in temp]
                temp_values = []
                for i in range(16):
                    temp = "".join(v_values[i*4 : i*4 + 4])
                    temp = int(temp, 2)
                    temp = hex(temp)[2:]
                    temp_values.append(temp)
                temp_values.reverse()
                temp_values = "0x" + "".join(temp_values)
                print(temp_values)

        # Gurobi syntax: m.Status == 3 represents the model is infeasible.
        elif m.Status == 3:
            print("The model is infeasible!")
        else:
            print("Unknown error!")
        time_end = time.time()
        print(("Time used = " + str(time_end - time_start)))
