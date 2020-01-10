'''
Applying the MILP-based method to find an optimum differential activity pattern for CRAFT
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

from craft import Craft                  

if __name__ == "__main__":

    rounds = 18
    related_tweak = 0
    starting_round = 0
    craft = Craft(rounds, related_tweak, starting_round)
    craft.make_model()
    craft.solve_model()
       
