'''
Applying the MILP-based method to find zero-correlation distinguishers of CRAFT
Copyright (C) June 1, 2019  Hosein Hadipour

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

11 Khordad, 1398
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
"""


class Craft:
    def __init__(self, rounds, related_tweak=0, starting_round=0):
        self.rounds = rounds
        self.related_tweak = related_tweak
        self.block_size = 64
        self.xor_counter = 0
        self.dummy_var_counter = 0
        self.starting_round = starting_round
        self.p_permute_nibbles = [
            0xf, 0xc, 0xd, 0xe, 0xa, 0x9, 0x8, 0xb, 0x6, 0x5, 0x4, 0x7, 0x1, 0x2, 0x3, 0x0]
        self.q_permute_teakey_nibbles = [
            0xc, 0xa, 0xf, 0x5, 0xe, 0x8, 0x9, 0x2, 0xb, 0x3, 0x7, 0x4, 0x6, 0x0, 0x1, 0xd]
        self.TK = [[[0] for _ in range(16)] for _ in range(4)]
        self.tweak = ["tk_%d" % nibble_number for nibble_number in range(16)]
        if (self.related_tweak == 0):
            self.filename_model = "craft" + "_s_" + str(self.rounds) + ".lp"
            self.filename_result = "craft" + "_s_" + str(self.rounds) + ".txt"
        else:
            self.filename_model = "craft" + "_rtk_" + str(self.rounds) + ".lp"
            self.filename_result = "craft" + \
                "_rtk_" + str(self.rounds) + ".txt"
        fileobj = open(self.filename_model, "w")
        fileobj.close()

    def create_objective_function(self):
        """
        Create objective function of the MILP model.
        """
        fileobj = open(self.filename_model, "a")
        fileobj.write("Minimize\n")
        A = ["x_%d_%d" % (r, i) for r in range(
            1 + self.starting_round, self.rounds + 1 + self.starting_round) for i in range(16)]
        temp = " + ".join(A)
        fileobj.write(temp)
        fileobj.write("\n")
        fileobj.close()

    def initialize_tweakey_differences(self):
        for nibble_number in range(16):
            self.TK[0][nibble_number] = self.tweak[nibble_number]
            self.TK[1][nibble_number] = self.tweak[nibble_number]
            self.TK[2][nibble_number] = self.tweak[self.q_permute_teakey_nibbles[nibble_number]]
            self.TK[3][nibble_number] = self.tweak[self.q_permute_teakey_nibbles[nibble_number]]

    @staticmethod
    def create_variables(r, s):
        """
        Generate the variables used in the model.
        """
        array = ["" for i in range(0, 16)]
        for i in range(0, 16):
            array[i] = "%s_%d_%d" % (s, r, i)
        return array

    @staticmethod
    def create_variables_after_mc(r, s1, s2):
        """
        Generate the variables used in the model.
        """
        array = [["" for i in range(0, 4)] for j in range(0, 16)]
        for i in range(0, 8):
            array[i] = "%s_%d_%d" % (s1, r, i)
        for i in range(8, 16):
            array[i] = "%s_%d_%d" % (s2, r, i)
        return array

    def constraints_by_equality(self, s1, s2):
        fileobj = open(self.filename_model, "a")
        for i in range(16):
            constraint = "%s - %s = 0\n" % (s1[i], s2[i])
            fileobj.write(constraint)
        fileobj.close()

    def constraints_by_truncxor(self, a, b, c):
        fileobj = open(self.filename_model, "a")
        """
        a + b + c >= 2 d
        d >= a
        d >= b
        d >= c
        """
        d = "d_%d" % self.xor_counter
        ineq1 = "%s + %s + %s -  2 %s >= 0\n" % (a, b, c, d)
        ineq2 = "%s - %s >= 0\n" % (d, a)
        ineq3 = "%s - %s >= 0\n" % (d, b)
        ineq4 = "%s - %s >= 0\n" % (d, c)
        fileobj.write(ineq1)
        fileobj.write(ineq2)
        fileobj.write(ineq3)
        fileobj.write(ineq4)
        fileobj.close()
        self.xor_counter += 1

    def constraints_by_mixing_layer(self, x, y):
        """
        Generate constraints related to mixing layer (MC)
        """
        for nibble_number in range(4):
            dummy_var = "dv_%d" % self.dummy_var_counter
            self.constraints_by_truncxor(
                x[nibble_number], x[nibble_number + 8], dummy_var)
            self.constraints_by_truncxor(
                dummy_var, x[nibble_number + 12], y[nibble_number])
            self.constraints_by_truncxor(x[nibble_number + 4], x[nibble_number + 12],
                                         y[nibble_number + 4])
            self.dummy_var_counter += 1

    def constraints_by_atk(self, tk, y, z):
        """
        Generate the constraints by AddTweakey
        """
        for nibble_number in range(16):
            self.constraints_by_truncxor(tk[nibble_number], y[nibble_number],
                                         z[nibble_number])

    def permute_nibbles(self, state):
        temp = [0]*16
        for i in range(16):
            temp[self.p_permute_nibbles[i]] = state[i]
        return temp

    def initial_state_constraint(self, x):
        fileobj = open(self.filename_model, "a")
        temp = " + ".join(x) + " >= 1\n"        
        fileobj.write(temp)
        x_in = self.create_variables(0 + self.starting_round, "x")
        temp1 = " + ".join(x_in) + " = 0\n"
        #fileobj.write(temp1)
        fileobj.close()

    def constraint(self):
        """
        Generate the constraints of MILP model
        """
        assert(1 <= self.rounds <= 32)
        fileobj = open(self.filename_model, "a")
        fileobj.write("Subject To\n")
        fileobj.close()
        x_in = self.create_variables(0 + self.starting_round, "x")

        last_round_state = self.create_variables(self.rounds + self.starting_round, "x")
        if (self.related_tweak == 1):
            self.initial_state_constraint(self.tweak)
            #self.initial_state_constraint(last_round_state)
            #self.initial_state_constraint(x_in + self.tweak)
        else:
            self.initial_state_constraint(x_in + last_round_state)
        y = self.create_variables_after_mc(0 + self.starting_round, "y", "x")
        z = self.create_variables(0 + self.starting_round, "z")
        x_out = self.create_variables(1 + self.starting_round, "x")
        if self.rounds == 1:
            self.constraints_by_mixing_layer(x_in, y)
            if (self.related_tweak == 1):
                self.constraints_by_atk(self.TK[0 + (self.starting_round % 4)], y, z)
                self.constraints_by_equality(self.permute_nibbles(z), x_out)
            else:
                self.constraints_by_equality(self.permute_nibbles(y), x_out)
        else:
            self.constraints_by_mixing_layer(x_in, y)
            if (self.related_tweak == 1):
                self.constraints_by_atk(self.TK[0 + (self.starting_round %4)], y, z)
                self.constraints_by_equality(self.permute_nibbles(z), x_out)
            else:
                self.constraints_by_equality(self.permute_nibbles(y), x_out)
            for r in range(1 + self.starting_round, self.rounds + self.starting_round):
                x_in = x_out
                y = self.create_variables_after_mc(r, "y", "x")
                z = self.create_variables(r, "z")
                x_out = self.create_variables(r + 1, "x")
                if (self.related_tweak == 1):
                    self.constraints_by_mixing_layer(x_in, y)
                    self.constraints_by_atk(self.TK[(self.starting_round + r) % 4], y, z)
                else:
                    self.constraints_by_mixing_layer(x_in, y)
                if r != 31:
                    if (self.related_tweak == 1):
                        self.constraints_by_equality(
                            self.permute_nibbles(z), x_out)
                    else:
                        self.constraints_by_equality(
                            self.permute_nibbles(y), x_out)

    # Variables declaration
    def variable_binary(self):
        """
        Specifying variables type.
        """
        fileobj = open(self.filename_model, "a")
        fileobj.write("Binary\n")
        # x
        for round_number in range(self.starting_round, self.rounds + 1 + self.starting_round):
            for nibble_number in range(16):
                fileobj.write("x_%s_%s\n" % (round_number, nibble_number))
        # y
        for round_number in range(self.starting_round, self.rounds + self.starting_round):
            for nibble_number in range(8):
                fileobj.write("y_%s_%s\n" % (round_number, nibble_number))
        # z
        if (self.related_tweak == 1):
            for round_number in range(self.starting_round, self.rounds + self.starting_round):
                for nibble_number in range(16):
                    fileobj.write("z_%s_%s\n" % (round_number, nibble_number))

        # tk
        if (self.related_tweak == 1):
            for nibble_number in range(16):
                fileobj.write("tk_%s\n" % nibble_number)

        # dummy variables used in xor operations
        for i in range(self.xor_counter):
            fileobj.write("d_%d\n" % i)

        # dummy variables used in mixing layers
        for i in range(self.dummy_var_counter):
            fileobj.write("dv_%d\n" % i)

        fileobj.write("END")
        fileobj.close()

    def make_model(self):
        """
        Generate the MILP model of CRAFT
        """
        fileobj = open(self.filename_model, "w")
        fileobj.close()
        if (self.related_tweak == 1):
            self.initialize_tweakey_differences()
        self.create_objective_function()
        self.constraint()
        self.variable_binary()
    
    def get_state_values_at_round(self, s, r, m):
        v_names = ["%s_%d_%d" % (s, r, nibble_number)
                           for nibble_number in range(16)]
        v_names.reverse()
        temp = map(m.getVarByName, v_names)                
        v_values = "0x" + "".join([str(int(e.X)) for e in temp])
        return v_values
    
    def get_state_values_output_of_mixing(self, r, m):
        v_names1 = self.create_variables_after_mc(r, "y", "x")
        v_names1.reverse()
        temp1 = map(m.getVarByName, v_names1)                    
        v_values1 = "0x" + "".join([str(int(e.X)) for e in temp1])
        return v_values1
    
    def get_tweak_values(self, m):
        v_names = self.tweak
        v_names.reverse()
        temp = map(m.getVarByName, v_names)
        v_values = "0x" + "".join([str(int(e.X)) for e in temp])
        return v_values

    def solve_model(self):
        """
        Solve the MILP model to search impossible linear trails
        """
        time_start = time.time()
        m = read(self.filename_model)
        #m.setParam(GRB.Param.OutputFlag, 0)
        m.setParam(GRB.Param.Threads, 32)
        #m.setParam(GRB.Param.Presolve, 0)
        m.optimize()
        # Gurobi syntax: m.Status == 2 represents the model is feasible.
        if m.Status == 2:
            status = 2
            obj = m.getObjective()
            for r in range(self.starting_round, self.rounds + 1 + self.starting_round):
                state1 = self.get_state_values_at_round("x", r, m)
                if (r < self.rounds + self.starting_round):
                    state2 = self.get_state_values_output_of_mixing(r, m)
                    #print("x%d: %s\t\t\ty%d: %s" %
                    #      (r, state1, r, state2))
                    print(state1[2:])
                else:
                    #print("x%d: %s" % (r, state1))
                    print(state1[2:])
            if (self.related_tweak == 1):
                tweak_values = self.get_tweak_values(m)
                print("t: %s" % tweak_values)
        # Gurobi syntax: m.Status == 3 represents the model is infeasible.
        elif m.Status == 3:
            status = 3
            print("The model is infeasible!")
        else:
            print("Unknown error!")
        time_end = time.time()
        print(("Time used = " + str(time_end - time_start)))
        return status
