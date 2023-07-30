// Trying multiprocess plotting/calculation Chris McDonell, Oct 2022
#include "impulse.h"
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <unistd.h>
#include <stdlib.h>
#include <math.h>
#include <getopt.h>
#include <jack/jack.h>


static jack_port_t *sig_in_port;
static jack_port_t *ref_in_port;
static float *sig_ring_buffer;
static float *ref_ring_buffer;
static float *sig_chunk;
static float *ref_chunk;
static unsigned int ring_buffer_length;
static unsigned int chunk_length;
static unsigned int ring_write_ptr;
static uint32_t sample_rate;
static int oversize = 2;
static int pause_stream = 1 ;

// res = array[(i + 1) % len];
// res = array[(i + 1 == len) ? 0 : i + 1];
// sig_chunk[n] = sig_ring_buffer[ (n + ring_write_ptr) % ring_buffer_length ];
// ref_chunk[n] = ref_ring_buffer[ (n + ring_write_ptr) % ring_buffer_length ];
// pA = ( _inputA >= 0 ) ? ( float * ) ( jack_port_get_buffer ( _jack_in [_inputA], nframes ) ) : 0;
// pB = ( _inputB >= 0 ) ? ( float * ) ( jack_port_get_buffer ( _jack_in [_inputB], nframes ) ) : 0;


static int skips = 0;
static int skip = 0;
static int lock = 1;

static int process_samples_callback (jack_nframes_t nframes, void *arg)
{
	if(pause_stream){ return 0; }

	// jack_default_audio_sample_t *sig_in = (jack_default_audio_sample_t *) jack_port_get_buffer (sig_in_port, nframes);
	// jack_default_audio_sample_t *ref_in = (jack_default_audio_sample_t *) jack_port_get_buffer (ref_in_port, nframes);
	float* sig_in = ( float * ) ( jack_port_get_buffer ( sig_in_port, nframes ) ) ;
	float* ref_in = ( float * ) ( jack_port_get_buffer ( ref_in_port, nframes ) ) ;


	for(jack_nframes_t i=0; i<nframes; i++){
		sig_ring_buffer[ring_write_ptr] = sig_in[i];
		ref_ring_buffer[ring_write_ptr] = ref_in[i];
		// ring_write_ptr = (ring_write_ptr + 1) % ring_buffer_length;
		ring_write_ptr = (ring_write_ptr + 1 == ring_buffer_length) ? 0 : ring_write_ptr + 1;
	}


	if( (skip >= skips || lock) ){
		unsigned int i = (ring_write_ptr);
		lock = 1;
		for( unsigned int n=0; n<(chunk_length); n++ ) {
			sig_chunk[n] = sig_ring_buffer[i];
			ref_chunk[n] = ref_ring_buffer[i];
			i = ( i + 1 == ring_buffer_length ) ? 0 : i + 1 ;
		}
		lock = 0;
		skip = 0;
	}
	skip++;

	// unsigned int i = ring_write_ptr;
	// for( unsigned int n=0; n<(chunk_length); n++ ) {
	// 	i = ( i + 1 == ring_buffer_length ) ? 0 : i + 1 ;
	// 	sig_chunk[n] = sig_ring_buffer[i];
	// 	ref_chunk[n] = ref_ring_buffer[i];
	// }


	return 0;
}

static void jack_shutdown_callback (void *arg)
{
	desruct();
	exit (1);
}

jack_client_t *client;
int setupJackSampler (unsigned long num_samples)
{
	const char **ports;
	float fs;		// The sample rate
	ring_buffer_length = num_samples*oversize;
	chunk_length = num_samples;
	sig_chunk = malloc((num_samples) * sizeof(float));
	ref_chunk = malloc((num_samples) * sizeof(float));

	if (num_samples <= 0) {
		fprintf(stderr, "impulse.c: usage: jack_impulse_grab -d duration [-f (C|gnuplot)]\n");
		return 1;
	}

	if ((client = jack_client_open("impulse_grabber", JackNullOption, NULL)) == 0) {
		fprintf (stderr, "jack server not running?\n");
		return 1;
	}

	jack_set_process_callback (client, process_samples_callback, 0);
	ring_write_ptr = 0;

	jack_on_shutdown (client, jack_shutdown_callback, 0);

	sample_rate = jack_get_sample_rate(client);

	sig_ring_buffer = malloc(ring_buffer_length * sizeof(float));
	ref_ring_buffer = malloc(ring_buffer_length * sizeof(float));


	sig_in_port = jack_port_register (client, "Sig-input", JACK_DEFAULT_AUDIO_TYPE, JackPortIsInput, 0);
	ref_in_port = jack_port_register (client, "Ref-input", JACK_DEFAULT_AUDIO_TYPE, JackPortIsInput, 0);

	if (jack_activate (client)) {
		fprintf (stderr, "cannot activate jack client");
		return 1;
	}
	pause_stream = 0;
	return 0;
}

void getJackSamplesFloat (float *sig_samples, float *ref_samples)
{
	if( pause_stream || lock ){ return ; }
	lock = 1;
    memcpy(sig_samples, sig_chunk, sizeof(float) * chunk_length);
    memcpy(ref_samples, ref_chunk, sizeof(float) * chunk_length);
	lock = 0;
}

uint32_t getJackSampleRate()
{
	return sample_rate;
}

void setJackBlockLength (int num_samples)
{
	pause_stream = 1;
	lock = 1;

	printf("Num = %d \n", num_samples);
	fflush( stdout );

	usleep(1000);

	chunk_length = num_samples;
	ring_buffer_length = num_samples*oversize;

	free(sig_ring_buffer);
	sig_ring_buffer = malloc((ring_buffer_length) * sizeof(float));

	free(ref_ring_buffer);
	ref_ring_buffer = malloc((ring_buffer_length) * sizeof(float));

	free(sig_chunk);
	sig_chunk = malloc((num_samples) * sizeof(float));

	free(ref_chunk);
	ref_chunk = malloc((num_samples) * sizeof(float));

	ring_write_ptr = 0;

	usleep(1000);
	pause_stream = 0;
	lock = 0;

}

void setJackBlockSkip(int skip_n)
{
	skips = skip_n;
}

void desruct()
{
	if(jack_client_close(client)){
		fprintf (stderr, "cannot close jack client");
	}
	free(sig_ring_buffer);
	free(ref_ring_buffer);
}

void getJackSamplesDouble (double *sig_samples, double *ref_samples)
{
    if( pause_stream ){ return ; }
    if( lock ){ return ; }

    memcpy(sig_samples, sig_chunk, sizeof(double) * chunk_length);
    memcpy(ref_samples, ref_chunk, sizeof(double) * chunk_length);
}
