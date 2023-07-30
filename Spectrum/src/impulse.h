// Trying multiprocess plotting/calculation
#ifndef MAIN_H_INCLUDED
#define MAIN_H_INCLUDED


#include <stdio.h>
#include <errno.h>
#include <unistd.h>
#include <stdlib.h>
#include <math.h>
#include <getopt.h>
#include <jack/jack.h>

static int process_samples_callback (jack_nframes_t, void*);

static void jack_shutdown_callback (void*);

int setupJackSampler (unsigned long);

void getJackSamplesFloat(float*, float*);

void getJackSamplesDouble(double*, double*);

void setJackBlockLength (int); // 	TODO FIXME

void setJackBlockSkip (int);

uint32_t getJackSampleRate();

void desruct();






#endif // MAIN_H_INCLUDED
