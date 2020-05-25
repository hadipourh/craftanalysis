/*
Experimental verification of theoretical results obtained in differential cryptanalysis of CRAFT
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
Modified version of designer's implementation
*/
// CRAFT Cipher 

#include "stdio.h"
#include "stdlib.h"
#include "stdint.h"
#include <time.h>
#include <string.h>
#include <math.h>
#include <omp.h>
#include <iostream>
using namespace std;
#define Nthreads 8
typedef unsigned long long int UINT64;

					//	0x0, 0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7, 0x8, 0x9, 0xA, 0xB, 0xC, 0xD, 0xE, 0xF,
const uint8_t S[16] = { 0xc, 0xa, 0xd, 0x3, 0xe, 0xb, 0xf, 0x7, 0x8, 0x9, 0x1, 0x5, 0x0, 0x2, 0x4, 0x6 };
const uint8_t P[16] = { 0xF, 0xC, 0xD, 0xE, 0xA, 0x9, 0x8, 0xB, 0x6, 0x5, 0x4, 0x7, 0x1, 0x2, 0x3, 0x0 };
const uint8_t Q[16] = { 0xC, 0xA, 0xF, 0x5, 0xE, 0x8, 0x9, 0x2, 0xB, 0x3, 0x7, 0x4, 0x6, 0x0, 0x1, 0xD };
const uint8_t RC3[32] = { 0x1, 0x4, 0x2, 0x5, 0x6, 0x7, 0x3, 0x1, 0x4, 0x2, 0x5, 0x6, 0x7, 0x3, 0x1, 0x4, 0x2, 0x5, 0x6, 0x7, 0x3, 0x1, 0x4, 0x2, 0x5, 0x6, 0x7, 0x3, 0x1, 0x4, 0x2, 0x5 };
const uint8_t RC4[32] = { 0x1, 0x8, 0x4, 0x2, 0x9, 0xc, 0x6, 0xb, 0x5, 0xa, 0xd, 0xe, 0xf, 0x7, 0x3, 0x1, 0x8, 0x4, 0x2, 0x9, 0xc, 0x6, 0xb, 0x5, 0xa, 0xd, 0xe, 0xf, 0x7, 0x3, 0x1, 0x8 };


void Initialize(uint8_t TK_enc[][16], uint8_t TK_dec[][16], uint8_t key_0[16], uint8_t key_1[16], uint8_t Tweak[16], int r) {    
	for (uint8_t i = 0; i < 16; i++)
		TK_enc[0][i] = (key_0[i] & 0xf);
	for (uint8_t i = 0; i < 16; i++)
		TK_enc[1][i] = (key_1[i] & 0xf);
	for (uint8_t i = 0; i < 16; i++)
		TK_enc[2][i] = TK_enc[0][i];
	for (uint8_t i = 0; i < 16; i++)
		TK_enc[3][i] = TK_enc[1][i];

	for (uint8_t i = 0; i < 16; i++)
		TK_enc[0][i] ^= (Tweak[i] & 0xf);
	for (uint8_t i = 0; i < 16; i++)
		TK_enc[1][i] ^= (Tweak[i] & 0xf);
	for (uint8_t i = 0; i < 16; i++)
		TK_enc[2][i] ^= (Tweak[Q[i]] & 0xf);
	for (uint8_t i = 0; i < 16; i++)
		TK_enc[3][i] ^= (Tweak[Q[i]] & 0xf);
    
    for (uint8_t j = 0; j < 4; j++)
        for (uint8_t i = 0; i < 4; i++) {                        
            TK_dec[j][i] = TK_enc[j][i] ^ TK_enc[j][i + 8] ^ TK_enc[j][i + 12];
			TK_dec[j][i + 4] = TK_enc[j][i + 4] ^ TK_enc[j][i + 12];
            TK_dec[j][i + 8] = TK_enc[j][i + 8];
            TK_dec[j][i + 12] = TK_enc[j][i + 12];
        }    
}

void RandomSubkeys(uint8_t TK_enc[][16], uint8_t TK_dec[][16]) {    
	for (uint8_t r = 0; r < 9; r++) {
		for (uint8_t i = 0; i < 16; i++){
			TK_enc[r][i] = rand() & 0xf;
			TK_dec[9-r-1][i] = TK_enc[r][i];
		}
        // printf("\nR%02d : ", r);
        // for (uint8_t i = 0; i < 16; i++){
        //     printf("%.1X", TK_enc[r][i]);
        // }
        // printf("\nEnd!\n");
    }
}

void Enc(uint8_t R, uint8_t plaintext[16], uint8_t ciphertext[16], uint8_t TK_enc[][16]) {
    for (uint8_t i = 0; i < 16; i++) {
        ciphertext[i] = plaintext[i] & 0xf;
    }    
    for (uint8_t r = 0; r < R; r++) {
        //MixColumn
        for (uint8_t i = 0; i < 4; i++) {
            ciphertext[i] ^= (ciphertext[i + 8] ^ ciphertext[i + 12]);
            ciphertext[i + 4] ^= ciphertext[i + 12];
        }

        //AddConstant
        ciphertext[4] ^= RC4[r];
        ciphertext[5] ^= RC3[r];

        //AddTweakey
        for (uint8_t i = 0; i < 16; i++) {            
            //ciphertext[i] ^= TK_enc[r][i];            
            ciphertext[i] ^= TK_enc[r % 4][i];            
        }
        //Permutation
            uint8_t Temp[16];
            for (uint8_t i = 0; i < 16; i++)
                Temp[P[i]] = ciphertext[i];                                            
        // SBox
        for (uint8_t i = 0; i < 16; i++)
            ciphertext[i] = S[Temp[i]];        
        // Next State
        // printf("\nR%02d : ", r + 1);
        // for (uint8_t i = 0; i < 16; i++)
        //     printf("%X", ciphertext[i]);
    }
}

int differentialQuery(uint8_t* dp, uint8_t* dc, int r, uint8_t TK_enc[][16], uint8_t TK_dec[][16], int N)
{
    int i, j, t, num = 0;
    for(i = 0; i < 16; i++) dp[i] = dp[i] & 0xf;
    for(i = 0; i < 16; i++) dc[i] = dc[i] & 0xf;	
	uint8_t p1[16],p2[16];    
    uint8_t c1[16],c2[16];	
	bool flag;

	for (t = 0; t < N; t++){        
		// randomly choose p1
		for(i = 0; i < 16; i++) p1[i] = rand() & 0xf;
		// derive p2
		for(i = 0; i < 16; i++) p2[i] = p1[i]^dp[i];
        Enc(r, p1, c1, TK_enc);
        Enc(r, p2, c2, TK_enc);
		flag = 1;
		for(i = 0; i < 16; i++)
			if ((c1[i]^c2[i]) != dc[i])
				flag = 0;
		if (flag) {num ++;}
	}
	return num;
}

double verify(int R, int N1, int N2, int N3) {
    uint8_t Key_0[16];// = {0x1, 0x5, 0x7, 0x7, 0x8, 0x9, 0xA, 0xD, 0xF, 0xC, 0xE, 0xD, 0x7, 0x8, 0xB, 0xD}; // Key 0
    uint8_t Key_1[16];// = {0xD, 0x9, 0xE, 0x0, 0xE, 0x3, 0x8, 0x1, 0xF, 0xE, 0x6, 0xA, 0x9, 0x4, 0xC, 0x5}; // Key 1            
    // uint8_t TK_enc[R][16];
    // uint8_t TK_dec[R][16];
    // RandomSubkeys(TK_enc, TK_dec);
    for(int i = 0; i < 16; i++) Key_0[i] = rand() & 0xf;
    for(int i = 0; i < 16; i++) Key_1[i] = rand() & 0xf;    

    //Parallel execution
    int NUM[N1];
	int counter;
    printf("#Rounds: %d rounds\n", R);
    //printf("#Queries: 2^(%f)\n", log(N1*N2*N3)/log(2));
	printf("#Total Queries = (#Parallel threads) * (#Bunches per thread) * (#Queries per bunch) = %d * %d * %d = 2^(%f)\n", N1, N2, N3, log(N1*N2*N3)/log(2));
    clock_t clock_timer;
    double wall_timer;
	clock_timer = clock();
	wall_timer = omp_get_wtime();
	omp_set_num_threads(N1);
	#pragma omp parallel for
	for(counter = 0; counter < N1; counter++)
	{
        uint8_t Tweak[16];// = {0xD, 0xa, 0xA, 0x0, 0xA, 0xA, 0x0, 0xA, 0x6, 0x5, 0xC, 0x0, 0x0, 0x1, 0x1, 0x1}; // Tweak
        uint8_t TK_enc[4][16];
        uint8_t TK_dec[4][16];
        //0x00A0A00A00A000AA
        uint8_t dp[16] = {0xA, 0xA, 0x0, 0x0, 0x0, 0xA, 0x0, 0x0, 0xA, 0x0, 0x0, 0xA, 0x0, 0xA, 0x0, 0x0};
        //0x00A0A00A0000A000
        uint8_t dc[16] = {0x0, 0x0, 0x0, 0xA, 0x0, 0x0, 0x0, 0x0, 0xA, 0x0, 0x0, 0xA, 0x0, 0xA, 0x0, 0x0};
		int j;
		int num = 0;
		for(j=0; j < N2; j++) {
            for(int i = 0; i < 16; i++) Tweak[i] = rand() & 0xf;
            Initialize(TK_enc, TK_dec, Key_0, Key_1, Tweak, R);
			num += differentialQuery(dp, dc, R, TK_enc, TK_dec, N3);
        }
		int ID = omp_get_thread_num();
		NUM[ID] = num;
	}
    cout << " time on clock(): " <<(double) (clock() - clock_timer) / CLOCKS_PER_SEC<<endl;
    cout << " time on wall: " <<  omp_get_wtime() - wall_timer << "\n";		
	double sum = 0;
    double sum_temp = 0;
	for(int i = 0; i < N1; i++)
		sum += NUM[i];	
	printf("sum = %f\n", sum);
	sum_temp = double(N1*N2*N3)/sum;
	
	printf("2^(-%f)\n\n", log(sum_temp)/log(2));
    printf("##########################\n");
    return sum;
}

int main() {
    srand(time(NULL));   // Initialization, should only be called once. int r = rand();
    const int n = 10; //number of indipendent experiments
    int R = 6; //Number of rounds
    //##########################    
    int N1 = Nthreads;//Number of paralle threads
    int deg = 10;
	int N2 = 1 << deg;//2^(deg) : Number of bunches per threads
	int N3 = 1024;// Number of queries per bunches
    //##########################
    double sum = 0;
    for(int i = 0; i < n; i ++) {
        sum += verify(R, N1, N2, N3);
    }    
    sum = double(n*N1*N2*N3)/sum;    
    printf("\nAverage = 2^(-%f)\n", log(sum)/log(2));
}
