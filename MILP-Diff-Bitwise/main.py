'''
Applying the MILP-based method to find zero-correlation distinguishers of CRAFT
Copyright (C) July 9, 2019  Hosein Hadipour

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

18 Tir, 1398
'''

from craft import Craft

if __name__ == "__main__":

    rounds = int(input("Input round number: "))
    while not (rounds > 0):
        print("Input a round number (greater than 0):")
        rounds = int(input("Input round number again: "))
    related_tweak = int(
        input("Choose one out of two :\nrelated-tweak model (1)\t single-tweak model (0): "))
    craft = Craft(rounds, related_tweak)
    craft.make_model()
    craft.solve_model()
