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

from multiprocessing import Pool, current_process, Process
import time
from craft import Craft

def go_search_for_zc(rounds, related_tweak,  slice_number):    
    pid = current_process().name
    print(f"\nProcess {pid} started, part {slice_number} out of {16}")
    craft = Craft(rounds, related_tweak, slice_number)
    if (related_tweak == 1):
        craft.search_masks_with_hamming_weight_of_one_rtk()
    else:
        craft.search_masks_with_hamming_weight_of_one_stk()
    print(f"Process {pid} finished, part {slice_number} out of {16}\n")

if __name__ == "__main__":
    rounds = 14
    related_tweak = 1
    start_time = time.time()
    with Pool() as pool:
        arguments = [(rounds, related_tweak, slice_number) for slice_number in range(2)]
        results = pool.starmap(go_search_for_zc, arguments)
    # processes = [Process(target = go_search_for_zc, args = (rounds, related_tweak, slice_number))\
    #     for slice_number in range(16)]
    # # Start processes
    # for pr in processes:
    #     pr.start()
    # # Exit the completed processes
    # for pr in processes:
    #     pr.join()
    elapsed_time = time.time() - start_time
    print(f"\nProcesses completed after {elapsed_time} seconds")
