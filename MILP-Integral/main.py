'''
Applying the MILP-based method to find integral distinguishers based on division property for CRAFT
Copyright (C) May 30, 2019  Hosein Hadipour

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

9 Khordad, 1398
'''

from craft import Craft

if __name__ == "__main__":
    rounds = int(input("Input the number of rounds: "))
    while not (rounds > 0):
        print("Input a round number greater than 0.")
        rounds = int(input("Input round number again: "))    
    craft = Craft(rounds)
    brute_force_flag = input("Brute force : 1    Probing an especial case : 0 ?\n")
    while (brute_force_flag not in ['0', '1']):
        print("Enter 0 or 1!")
        brute_force_flag = input("Brute force : 1    Probing an especial case : 0 ?\n")
    craft.set_brute_force_flag(brute_force_flag)
    if brute_force_flag == '0':
        temp = input("Enter the list of constant bits separated by spaces:\n")
        temp = temp.split()
        constant_bits = []
        for element in temp:
            constant_bits.append(int(element))
        craft.set_constant_bits(constant_bits)
        craft.make_model()
        craft.solve_model()
    else:
        number_of_total_states = 64
        for i in range(0, 64):
            print("%d / %d" % (i, number_of_total_states))
            constant_bits = [i]
            craft.set_constant_bits(constant_bits)
            craft.make_model()
            craft.solve_model()
