// #include <cassert>

// #include <stdio.h>
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>

#include <unistd.h>
#include <fcntl.h>

#include <iostream>
#include <fstream>
#include <iomanip>

#include <algorithm>
#include <math.h>
#include <cmath>
#include <complex>
// #include <fftwf3.h>

#include "c.h"
#include "impulse.h"


#include <chrono>
#include <sys/stat.h>
#include <fftw3.h>

#include <limits>

#include <thread>


using namespace std::chrono;

// #define BLOCK_LENGTH 8
// #define BLOCK_LENGTH 1024
// #define BLOCK_LENGTH 256*8
// #define BLOCK_LENGTH 8192
#define REAL 0
#define IMAG 1

// using namespace std::complex_literals;
 


class MatrixD
{
	size_t nrows, ncols;
	float* data_;
	
public:
	MatrixD(){;}
	
	~MatrixD()
	{
		delete[] data_ ;
		std::cout << "MatrixD: 'data_' destroyed! \n";
	}
	
	void shape(size_t nrows, size_t ncols)
	{
		this->nrows = nrows;
		this->ncols = ncols;
		data_ = new float[nrows*ncols];
	}
	
	float& operator()(size_t rw, size_t cl)
	{
		return data_[ (nrows * cl) + rw ];
	}
	
	float operator()(size_t rw, size_t cl) const
	{
		return data_[ (nrows * cl) + rw ];
	}
	
	void columnMean(float* arr)
	{
		float tmp=0.0;
		for(size_t cl=0; cl<ncols; cl++){
			for(size_t rw=0; rw<nrows; rw++){
				tmp += data_[(nrows * cl) + rw ];
			}
			arr[cl] = tmp/nrows;
			tmp = 0.0;
		}
	}
	
	void rowMean(float* arr)
	{
		float tmp=0.0;
		for(size_t rw=0; rw<nrows; rw++){
			for(size_t cl=0; cl<ncols; cl++){
				tmp += data_[  (nrows * cl) + rw ];
			}
			arr[rw] = tmp/ncols;
			tmp = 0.0;
		}
	}

	void fillCount()
	{
		for(size_t i=0; i<(nrows*ncols); i++){
			data_[i] = i;
		}
	}
	
	size_t maxrws()
	{
		return nrows;
	}
	
	size_t maxcls()
	{
		return ncols;
	}
	
	void resize(size_t nrows, size_t ncols)
	{
		delete[] data_;
		this->nrows = nrows;
		this->ncols = ncols;
		data_ = new float[nrows*ncols];
	}
	
	void show()
	{
		for(size_t rw=0; rw<nrows; rw++){
			for(size_t cl=0; cl<ncols; cl++){
				// 				std::cout << std::setfill('-') << std::setw(6) << std::fixed << std::setprecision(3) << " : " << *(data_ + rw * ncols + cl);
// 				std::cout << " : " << *(data_ + rw * ncols + cl)<<"\t";
				std::cout << " : " << data_[ (nrows * cl) + rw ] <<"\t";
			}
			std::cout << "\n";
		}
		std::cout << "\n";
	}
	
	void showAddress()
	{
		for(size_t rw=0; rw<nrows; rw++){
			// 			std::cout << "row: " << rw <<"...\n";
			for(size_t cl=0; cl<ncols; cl++){
				std::cout << " : " << data_[ (nrows * cl) + rw ] <<" ";
				std::cout << " @: " << data_[ (nrows * cl) + rw ] <<"\n";
			}
			std::cout <<"\n";
		}
		std::cout <<"\n\n";
	}
	
};


class JackSampler
{
    // Wraps impulse.c /.h

    
	float nyquist = 0;
    uint32_t sample_rate = 0;
    float block_duration = 0;
    size_t block_length;
    
public:
    
    JackSampler (size_t block_length)
	{
//     JackSampler(){
        setupJackSampler(block_length);
        this->block_length = block_length;
        this->sample_rate = getJackSampleRate();
        nyquist = (float)sample_rate/2;
        block_duration = block_length/(float)sample_rate;
    }
    
    
    ~JackSampler()
	{
        std::cout<<"JackSampler destroyed\n";
    }
    
    void closeClient()
	{
		desruct();
	}

  
    void setBlockLength(int new_block_length)
	{
        block_length = new_block_length;
        block_duration = block_length/(float)sample_rate;
		setJackBlockLength(new_block_length);
    }

    void setBlockSkip(int skip_n)
	{
		setJackBlockSkip(skip_n);
	}
  
  
    void getRawSamplesFloat(float *sig_samples, float *ref_samples)
	{
        getJackSamplesFloat(sig_samples, ref_samples);
    }
  
  
    void getRawSamplesDouble(double *sig_samples, double *ref_samples)
	{
        getJackSamplesDouble(sig_samples, ref_samples);
// 		std::cout<<"### Got samples ###"<<"\n";
    }
  
  
    uint32_t getSampleRate()
	{
        return sample_rate;
    }
    
    
    float getBlockDuration()
	{
        return block_duration;
    }
    
    
    
};
 

class Spectrum
{
    JackSampler js;

    size_t block_length;
    size_t spctrm_length;
    fftwf_complex* sig_cmplx;
    fftwf_complex* ref_cmplx;
    float* sig_raw_samples;
    float* ref_raw_samples;
    
	float* test_raw_samples;
  
	float* baked_wf_window;
    fftwf_plan sig_plan;
    fftwf_plan ref_plan;
	
    float* sig_amplitude;
    float* ref_amplitude;
    float* sig_phase;
    float* ref_phase;
    float* freq_axis;
	float* sig_exp_ave_mem;
	float* ref_exp_ave_mem;
	float* sig_peak_mem;
	float* ref_peak_mem;
	MatrixD sig_mov_ave_mem;
	MatrixD ref_mov_ave_mem;
	float* sig_forever_ave_mem;
	float* ref_forever_ave_mem;
	float num_averages ;
	size_t sig_ave_index=0;
	size_t ref_ave_index=0;
    std::string window;
	float min_freq = 10.0;
	int min_freq_bin = 1;
	float freq_resolution=0;
	bool pause = 0;
	unsigned int forever_ave_count = 0;





	
    void bakeWindow(float *baked_window, size_t sz, std::string window)
	{
		this->window = window;
        if(window == "Hanning" || window == "hanning" || window == "Han" || window == "han"){
            for(size_t i=0; i<sz; i++){
                baked_window[i] = 1*(0.5 - 0.5*(float) cos((2*M_PI*i)/(sz-1)));
            }
        }else if(window == "Hamming" || window == "hamming" || window == "Ham" || window == "ham"){
            for(size_t i=0; i<sz; i++){
                baked_window[i] = 1*(0.54 - 0.46*(float)cos((2*M_PI*i)/(sz-1)));
            }
        }else if(window.find("Blackman") != std::string::npos){
            float a0=1,a1=1,a2=1,a3=1;
            if(window.find("Nuttal") != std::string::npos){
                a0 = 0.3125, a1 = 0.46875, a2 = 0.1875, a3 = 0.03125;
            }else{ // Blackman-Min
                a0 = 0.355768, a1 = 0.487396, a2 = 0.144232, a3 = 0.012604;
            }
            for(size_t i=0; i<sz; i++){
                baked_window[i] = a0 - a1 * cos(2*M_PI*i / (sz-1) ) +
                a2 * cos(4*M_PI*i /(sz-1) ) - a3 * cos(6*M_PI*i / (sz-1) );
            }
        }else{
            for(size_t i=0; i<sz; i++){ baked_window[i] = 1; }
        }
    }

    void applyBakedWFWindow (float* samples, size_t sz)
	{
		for(size_t i =0; i<sz;i++){
			samples[i] = (samples[i] * baked_wf_window[i]);
		}
	}
	
    void generateXAxis()
	{
        float sr = (float)js.getSampleRate();
        freq_resolution =  ( (sr /2) / (spctrm_length) );
		float nyquist = spctrm_length*freq_resolution;
		
		std::cout << "sr: " << std::setprecision(6) << sr <<"\n";
		std::cout << "FFT (block) Length: " << block_length <<"\n";
		std::cout << "FFT freq_Resolution: " << freq_resolution <<"\n";
		std::cout << "WFM freq_Resolution: " << std::setprecision(6) << (1.0/(spctrm_length/sr)) <<"\n";
		std::cout << "Nyquist freq: " << std::setprecision(6) << nyquist <<"\n";
		std::cout << "Sampling time: " << std::setprecision(6) << (spctrm_length/sr)*2 <<"\n\n";
	
        // freq_axis = new float[spctrm_length]; // Done in constuctor or reset()

        for(size_t i=0; i<spctrm_length; i++){
            freq_axis[i] = (i * freq_resolution);
			if(freq_axis[i] <= min_freq){min_freq_bin = i;}
        }
    } 
     
	void extractAmplitudes(fftwf_complex* cx_fft, float* amplitudes)
	{
        for(size_t i=0; i<spctrm_length; i++){
            // amplitudes[i] = std::sqrt( pow(cx_fft[i][REAL],2) + (pow(cx_fft[i][IMAG],2) ) )  ;
            amplitudes[i] = ( pow(cx_fft[i][REAL],2) + (pow(cx_fft[i][IMAG],2) ) )  ;
        }
	} 

    void applyPeakHold ( float* spectrum, float* peak_mem ) // FIXME
    {

        static unsigned int reset = 0;
        float sp;

        if ( reset > 100 ) {
            for ( size_t i=0; i<spctrm_length; i++ ) {
                peak_mem[i] = -200.0;
                reset = 0;
            }
        }

        for ( size_t i=0; i<spctrm_length; i++ ) {

            sp = spectrum[i];

            // if( abs(peak_mem[i])  >  abs(spectrum[i]) ){

            if ( ( peak_mem[i] )  > ( spectrum[i] ) ) {
                spectrum[i] = peak_mem[i] ;
            } else {
                peak_mem[i] = sp;
            }


        }
        reset++;

    }

    int applyExpSmoothing ( float* spectrum, float* exp_ave_mem )
    {
// 		st = αxt+(1 – α)st-1= st-1+ α(xt – st-1)
// 		st = smoothed statistic
// 		st-1 = previous smoothed statistic
// 		α = smoothing factor of data; 0 < α < 1

        float ave;
        float mem;
        float yf;

		if( reset_averaging ){
			for ( size_t i=0; i<spctrm_length; i++ ) {
					exp_ave_mem[i] = spectrum[i];
			}
		}

        for ( size_t i=0; i<spctrm_length; i++ ) {

            yf = spectrum[i];
            mem = exp_ave_mem[i];

            ave =  exp_alpha * yf + ( 1 - exp_alpha ) * mem ;

            if ( isnan ( ave ) ) {
                ave=spectrum[i];
            }
            spectrum[i] = ave;
            exp_ave_mem[i] = ave;
        }
        return 0 ;
    }

    void applyForeverAverage ( float* spectrum, float* mem )
    {
        float ave;
		float fac;

		if( forever_ave_count == 0 || reset_averaging ){
			for ( size_t i=0; i<spctrm_length; i++ ) {
				mem[i] = spectrum[i] ;
			}
			forever_ave_count = 0;
		}

		forever_ave_count ++;


		fac = 1.0 / forever_ave_count;

        for ( size_t i=0; i<spctrm_length; i++ ) {

            mem[i] += spectrum[i];

            ave =  ( mem[i] ) * fac ;
            // ave =  ( mov_ave_mem[i] / forever_ave_count )  ;

            if ( isnan ( ave ) ) { ave = spectrum[i]; }

            spectrum[i] = ave;

        }

    }

	void resetAveraging(){
		static unsigned int ctr;
		ctr++;
		forever_ave_count = 0;
		if( ctr > ( 2 ) ){
			reset_averaging = 0;
			ctr = 0;
		}
	}

    void applyMovingAverage ( MatrixD& m, float* spectrum, size_t& index )
    {
        if ( reset_averaging ) {
			for(int j=0; j<num_averages; j++){
				for ( size_t i=0; i<spctrm_length; i++ ) {
					m ( j, i ) = spectrum[i] ;
				}
			}
        }

        if ( index >= num_averages ) {
            index = 0;
        }
        for ( size_t i=0; i<spctrm_length; i++ ) {
            m ( index, i ) = spectrum[i];
        }
        m.columnMean ( spectrum );
        index++;
    }

    float findPeak ( float* amplitudes )
    {
        float peak=0;
        for ( size_t i=0; i<spctrm_length; i++ ) {
            if ( std::abs ( amplitudes[i] ) >peak ) {
                peak = std::abs ( amplitudes[i] );
            }
        }
        return peak;
    }

    float findMean ( float* amplitudes )
    {
        float tot=0, mean;
        unsigned int inc=1, n=0;
        for ( size_t i=0; i<spctrm_length; i+=inc ) {
            tot += amplitudes[i];
            inc++;
            n++;
        }
        mean = ( tot/n );
        return mean;
    }

    void logify ( float* amplitudes, float reference )
    {

        // reference = 174.0;
        // std::cout<< "\n:"<< reference;


        for ( size_t i=0; i<spctrm_length; i++ ) {
            if ( amplitudes[i] == 0 ) {
                ;
            } else {
                amplitudes[i] = 10 * log10 ( ( amplitudes[i] ) / ( reference + 100 ) );
            }
        }
    }

    void showDifference ( float* sig_amplitudes, float* ref_amplitudes, int mode ) // TODO improve/add controls
    {
        if ( mode == 1 ) {
            for ( size_t i=0; i< ( spctrm_length ); i++ ) {
                sig_amplitudes[i] = ( ( sig_amplitudes[i] ) - ( ref_amplitudes[i] ) );
            }
        } else if ( mode == 2 ) {
            for ( size_t i=0; i< ( spctrm_length ); i++ ) {
                sig_amplitudes[i] = ( ( ref_amplitudes[i] ) - ( sig_amplitudes[i] )  );
            }
        }
    }

    void renderTimeSeries ( float* samples )
    {
        uint n = 0;
        for ( size_t i=0; i<block_length; i++ ) {
            if ( ! ( i%2==0 ) ) {
                test_raw_samples[n] = samples[i];
                n++;
            }
        }
    }

    void threshold ( float* arr, size_t sz ) // FIXME
    {
        float thshld=0;
        thshld = std::abs ( findPeak ( arr ) /100.0f );
        for ( size_t i=0; i<sz; i++ ) {

            if ( std::abs ( arr[i] ) < thshld ) {
                arr[i]=0;
            }
// 			std::cout<<" : "<< arr[i] <<",\t";

        }
    }

    void NEW_smoothBasic ( float* amplitudes, unsigned int max_span )
    {
        unsigned int n=0;
        float first_span=1 ;
        static float last_span ;
        static unsigned int* spans = new unsigned int[spctrm_length];
        float* am = new float[spctrm_length];

        if ( ! ( last_span == max_span ) ) { // Bake some spans. (once per size change)
            last_span= ( float ) max_span ;
            float  sp = first_span ;
            float step = ( ( last_span - first_span ) / spctrm_length );
            for ( size_t i=0; i< ( spctrm_length-0 ); i++ ) {
                spans[i] = sp;
                sp += step;
                // std::cout<<i<<", smoothBasic: "<<spans[i]<<", "<<", "<<((last_span - first_span)/2)<<"\n";
            }
        }

        unsigned int span_start=0, span_end=0 ;
        float span_ave=0.0;
        n=0 ;
        for ( size_t i=0; i< ( spctrm_length ); i++ ) {
            if ( n >= 1 ) {
                span_start = ( unsigned int ) ( n - spans[n] );
                span_end = ( unsigned int ) ( n + spans[n] );
                if ( span_end > spctrm_length ) {
                    span_end = spctrm_length;
                }

                // int span_mid = (int)( (span_end - span_start)/2 ) ;

                for ( size_t j=span_start; j<span_end; j++ ) {
                    span_ave += amplitudes[j];
                    // std::cout<<i<<", span: "<< j ;
                }
                // std::cout<<"\n";

                span_ave = ( span_ave / ( ( span_end - span_start )+1 ) );
                am[i] =  span_ave;
            }
            n++;
        }

        // std::copy_n(am, spctrm_length, smoothed_amplitudes);
        std::copy_n ( am, spctrm_length, amplitudes );

        delete[] am;
    }

    void smoothBasic ( float* amplitudes, unsigned int max_span )
    {
        unsigned int n=0;
        float first_span=3 ;
        static float last_span ;
        static unsigned int* spans = new unsigned int[spctrm_length];
        float* am = new float[spctrm_length];

        if ( ! ( last_span == max_span ) ) { // Bake some spans. (once per size change)
            last_span= ( float ) max_span ;
            float  sp = first_span ;
            float step = ( ( last_span - first_span ) / spctrm_length );
            for ( size_t i=0; i< ( spctrm_length-0 ); i++ ) {
                spans[i] = sp;
                sp += step;
                // std::cout<<i<<", smoothBasic: "<<spans[i]<<", "<<", "<<((last_span - first_span)/2)<<"\n";
            }
        }

        unsigned int span_start=0, span_end=0 ;
        float span_ave=0.0;
        n=0 ;
        for ( size_t i=0; i< ( spctrm_length ); i++ ) {
            if ( n >= 1 ) {
                span_start = ( unsigned int ) ( n - spans[n] );
                span_end = ( unsigned int ) ( n + spans[n] );
                if ( span_end > spctrm_length ) {
                    span_end = spctrm_length;
                }

                // int span_mid = (int)( (span_end - span_start)/2 ) ;

                for ( size_t j=span_start; j<span_end; j++ ) {
                    span_ave += amplitudes[j];
                    // std::cout<<i<<", span: "<< j ;
                }
                // std::cout<<"\n";

                span_ave = ( span_ave / ( ( span_end - span_start )+1 ) );
                am[i] =  span_ave;
            }
            n++;
        }

        // std::copy_n(am, spctrm_length, smoothed_amplitudes);
        std::copy_n ( am, spctrm_length, amplitudes );

        delete[] am;
    }

    void applySlope ( float* amplitudes )
    {
        for ( size_t i=0; i< ( spctrm_length ); i++ ) {
            amplitudes[i] = ( ( amplitudes[i] ) + ( slope * 10*log10(i*0.005) ) );
            // amplitudes[i] = ( ( amplitudes[i] ) + ( slope * 10*log10(i) ) );
        }
    }
	
    void reset(int block_length, std::string window=" ")
	{

		this->block_length = block_length;
		// this->spctrm_length = (block_length/2U+1U);
		this->spctrm_length = (block_length/2U);

		delete[] sig_cmplx;
		delete[] ref_cmplx;
        sig_cmplx = new fftwf_complex[block_length];
        ref_cmplx = new fftwf_complex[block_length];

		delete[] sig_raw_samples;
		delete[] ref_raw_samples;
		delete[] test_raw_samples;
        sig_raw_samples = new float[block_length];
        ref_raw_samples = new float[block_length];
        test_raw_samples = new float[block_length];

		delete[] baked_wf_window;
        baked_wf_window = new float[block_length];
        bakeWindow(baked_wf_window, block_length, window);

		delete[] sig_amplitude;
		delete[] ref_amplitude;
		sig_amplitude = new float[spctrm_length];
        ref_amplitude = new float[spctrm_length];

		delete[] freq_axis;
        freq_axis = new float[spctrm_length];
        generateXAxis();

		delete[] sig_exp_ave_mem;
		delete[] ref_exp_ave_mem;
		sig_exp_ave_mem = new float[spctrm_length];
		ref_exp_ave_mem = new float[spctrm_length];

				// fftwf_destroy_plan(sig_plan);
				// fftwf_destroy_plan(ref_plan);
		fftwf_free(sig_plan);
		fftwf_free(ref_plan);
        sig_plan = fftwf_plan_dft_r2c_1d(block_length, sig_raw_samples, sig_cmplx, FFTW_MEASURE);
        ref_plan = fftwf_plan_dft_r2c_1d(block_length, ref_raw_samples, ref_cmplx, FFTW_MEASURE);

		// sig_mov_ave_mem.resize(num_averages, spctrm_length);
		// ref_mov_ave_mem.resize(num_averages, spctrm_length);

		std::cout << "\n\n\n @@@### !! GOT HERE !! ###@@@ \n\n\n";

		sig_mov_ave_mem.shape(num_averages, spctrm_length);
		ref_mov_ave_mem.shape(num_averages, spctrm_length);

		delete[] sig_forever_ave_mem;
		delete[] ref_forever_ave_mem;
		sig_forever_ave_mem = new float[spctrm_length];
		ref_forever_ave_mem = new float[spctrm_length];


		delete[] sig_peak_mem;
		delete[] ref_peak_mem;
		sig_peak_mem = new float[spctrm_length];
		sig_peak_mem = new float[spctrm_length];

	}


	

public:

	bool reset_averaging = 0; // TODO  impliment this.
	unsigned int render_time_series_mode = 1;
	unsigned int log_mode = 1;
	unsigned int difference_mode = 0;
	unsigned int peak_hold_mode=0;
	unsigned int smoothing_max_span = 0;
	float slope = 0.0;
	float exp_alpha = 1.0;

    Spectrum(int block_length, std::string window=" "):js(block_length)
	{
		this->block_length = block_length;
		this->spctrm_length = (block_length/2U+1U);
        sig_cmplx = new fftwf_complex[block_length];
        ref_cmplx = new fftwf_complex[block_length];
        sig_raw_samples = new float[block_length];
        ref_raw_samples = new float[block_length];
		
		test_raw_samples = new float[block_length];
		
        baked_wf_window = new float[block_length];
		
        sig_plan = fftwf_plan_dft_r2c_1d(block_length, sig_raw_samples, sig_cmplx, FFTW_ESTIMATE);
        ref_plan = fftwf_plan_dft_r2c_1d(block_length, ref_raw_samples, ref_cmplx, FFTW_ESTIMATE);

		sig_amplitude = new float[spctrm_length];
        ref_amplitude = new float[spctrm_length];

        freq_axis = new float[spctrm_length];       
        
        bakeWindow(baked_wf_window, block_length, window);
        generateXAxis();
		
		sig_exp_ave_mem = new float[spctrm_length];
		ref_exp_ave_mem = new float[spctrm_length];  
		
		sig_mov_ave_mem.shape(num_averages, spctrm_length);
		ref_mov_ave_mem.shape(num_averages, spctrm_length);

		sig_forever_ave_mem = new float[spctrm_length];
		ref_forever_ave_mem = new float[spctrm_length];

		sig_peak_mem = new float[spctrm_length];
		sig_peak_mem = new float[spctrm_length];
	}

    ~Spectrum()
	{
        delete[] sig_cmplx;
		delete[] ref_cmplx;
        delete[] sig_raw_samples;
		delete[] ref_raw_samples;
		delete[] baked_wf_window;
		delete[] sig_amplitude;
		delete[] ref_amplitude;
		delete[] freq_axis;
		delete[] sig_exp_ave_mem;
		delete[] ref_exp_ave_mem;
// 		fftwf_destroy_plan(sig_plan);
// 		fftwf_destroy_plan(ref_plan);
		fftwf_free(sig_plan); 
		fftwf_free(ref_plan);
    }

    void runFFT()
	{
		if(pause){return;}

		js.getRawSamplesFloat(sig_raw_samples, ref_raw_samples);
//		std::cout << "Acquired FFT, of length: " << block_length <<"\n";
		applyBakedWFWindow (sig_raw_samples, block_length);
		applyBakedWFWindow (ref_raw_samples, block_length);
		
		if(render_time_series_mode){
			renderTimeSeries(sig_raw_samples);
		}
		
        fftwf_execute(sig_plan);
        fftwf_execute(ref_plan);
        extractAmplitudes(sig_cmplx, sig_amplitude);
        extractAmplitudes(ref_cmplx, ref_amplitude);


		if(num_averages && (num_averages <= 100) ){
			applyMovingAverage(sig_mov_ave_mem, sig_amplitude, sig_ave_index);
			applyMovingAverage(ref_mov_ave_mem, ref_amplitude, ref_ave_index);
		}

		if(num_averages  > 100){
			applyForeverAverage( sig_amplitude, sig_forever_ave_mem );
			applyForeverAverage( ref_amplitude, ref_forever_ave_mem );
		}


		if( exp_alpha ){
			applyExpSmoothing(sig_amplitude, sig_exp_ave_mem);
			applyExpSmoothing(ref_amplitude, ref_exp_ave_mem);
		}

		if(smoothing_max_span){
			smoothBasic(sig_amplitude, smoothing_max_span );
			smoothBasic(ref_amplitude, smoothing_max_span );
		}

		if( log_mode ){
			logify(sig_amplitude, 0.0);
			logify(ref_amplitude, 0.0);
		}

		if( difference_mode == 1 ){
			showDifference(sig_amplitude, ref_amplitude, difference_mode);
		}

		if( peak_hold_mode ){
			applyPeakHold( sig_amplitude, sig_peak_mem );
		}

		if( slope ){
			applySlope(sig_amplitude);
			applySlope(ref_amplitude);
		}

		if( reset_averaging ){
			resetAveraging();
		}



    }
    
    void closeJackClient()
	{
		js.closeClient();
	}
        
    void setBlockLength(size_t block_length)
	{
		pause = 1 ;
		usleep(1000);
		this->block_length = block_length;
		this->spctrm_length = (block_length/2U+1U);
		this->reset(block_length, window);
		usleep(1000);
		this->js.setBlockLength(block_length);
		usleep(1000);
		pause = 0;
		return;
	}

	void setBlockSkip(int blocks)
	{
		js.setBlockSkip( blocks );
	}

	void setWindow( int type )
	{
		if( type == 0 ){ bakeWindow(baked_wf_window, block_length, "None"); }
		if( type == 1 ){ bakeWindow(baked_wf_window, block_length, "Blackman min"); }
		if( type == 2 ){ bakeWindow(baked_wf_window, block_length, "Blackman Nuttal"); }
		if( type == 3 ){ bakeWindow(baked_wf_window, block_length, "Hamming"); }
		if( type == 4 ){ bakeWindow(baked_wf_window, block_length, "Hanning"); }
		// if( type == 5 ){ bakeWindow(baked_wf_window, block_length, "Flat top"); }
	}

    void setNumAverages ( int num_averages )
    {
        sig_mov_ave_mem.resize ( num_averages, spctrm_length );
        ref_mov_ave_mem.resize ( num_averages, spctrm_length );
        this->num_averages = num_averages;
		// mov_ave_count = 0;
    }

    const float* getFreqAxis() const
    {
        return freq_axis;
    }

    const float* getSigAmplitude() const
    {
        return sig_amplitude;
    }

    const float* getRefAmplitude() const
    {
        return ref_amplitude;
    }

    const float* getTestSamples() const
    {
        return test_raw_samples;
    }

    void setMinFreq ( float min_freq )
    {
        this->min_freq = min_freq;
    }

    int getMinFreqBin() const
    {
        return min_freq_bin;
    }

    const float* getSigPhase() const
    {
        return sig_phase;
    }

    const float* getRefPhase() const
    {
        return ref_phase;
    }
    
};

const char *spectrum_data_fifo_name = "./spectrum_data.fifo";
const char *spectrum_params_fifo_name = "./spectrum_params.fifo";
bool new_param_flag=1;
bool spectrum_run_flag=0;
bool got_param_msg=0;
uint fft_blk_length=32768;
bool pause_data = 0;

Spectrum spm(fft_blk_length, "Blackman min");
int render_time_series=1;
bool param_message_enable = 1;

int read_parameter_fifo();
std::thread param_io;
std::string param_line;
// void change_param(std::string);
void change_param();

// int test = 0;

void runner()
{
	spm.setNumAverages(6);
	spm.smoothing_max_span = 0;
	spm.exp_alpha = 1.0;
	usleep(10000);

	got_param_msg=0;
	 
	std::string c_line;
	spectrum_run_flag=1;
	while(spectrum_run_flag){


		// if(test>10){break;}
		// test++;

		if(! got_param_msg ){

			// std::ofstream ostrm( spectrum_data_fifo_name, std::ios_base::out);
			std::ofstream ostrm( spectrum_data_fifo_name, std::ios::out);

				spm.runFFT();
				c_line.clear();

				for(size_t i=0; i<( (fft_blk_length+0)/2 ); i++){
					c_line.append( std::to_string(spm.getFreqAxis()[i]) );
					c_line.append(",");
					c_line.append( std::to_string(spm.getSigAmplitude()[i]) );
					c_line.append(",");
					c_line.append( std::to_string(spm.getRefAmplitude()[i]) );
					if(render_time_series){
						c_line.append(",");
						c_line.append( std::to_string(spm.getTestSamples()[i]) );
					}
					c_line.append("\n");
				}

				ostrm << c_line;
				// ostrm.close();
		}else{
				// change_param();
		}
		usleep(10000);
		// param_io.join();

	}
	param_message_enable = 0;
	spm.closeJackClient();
}

// fifo.open("/home/fedor/projects/fifo2/in",ios::out);

// void change_param(std::string param_line)
void change_param()
{

	if ( param_line.substr(0, 1) == "E" ){
		std::cout << "[c++] Match! (E)\n";
		int ex = stoi( param_line.substr(1,-1) );
		spm.exp_alpha = ( 1.0 / ex );
	}

	if ( param_line.substr(0, 1) == "A" ){
		std::cout << "[c++] Match! (A)\n";
		int num_averages = stoi( param_line.substr(1,-1) );
		spm.setNumAverages(num_averages);
	}

	if ( param_line.substr(0, 1) == "B" ){
		std::cout << "[c++] Match! (B)\n";
		fft_blk_length = stoi( param_line.substr(1,-1) );
		spm.setBlockLength(fft_blk_length);
	}

	if ( param_line.substr(0, 1) == "D" ){
		std::cout << "[c++] Match! (D)\n";
		int dif = stoi( param_line.substr(1,-1) );
		spm.difference_mode = dif;
	}

	if ( param_line.substr(0, 1) == "l" ){
		std::cout << "[c++] Match! (l)\n";
		int mode = stoi( param_line.substr(1,-1) );
		spm.log_mode = mode;
	}

	if ( param_line.substr(0, 1) == "P" ){
		std::cout << "[c++] Match! (D)\n";
		int mode = stoi( param_line.substr(1,-1) );
		spm.peak_hold_mode = mode;
	}

	if ( param_line.substr(0, 1) == "R" ){
		std::cout << "[c++] Match! (R)\n";
		spm.reset_averaging = 1;
	}

	if ( param_line.substr(0, 1) == "S" ){
		std::cout << "[c++] Match! (S)\n";
		int span = stoi( param_line.substr(1,-1) );
		spm.smoothing_max_span = span;
	}

	if ( param_line.substr(0, 1) == "s" ){
		std::cout << "[c++] Match! (S)\n";
		float slope = stof( param_line.substr(1,-1) );
		float d = 1.0/3.0;
		spm.slope = slope * d;
	}

	if ( param_line.substr(0, 1) == "T" ){
		std::cout << "[c++] Match! (T)\n";
		int mode = stoi( param_line.substr(1,-1) )  ;
		spm.render_time_series_mode = mode;
		render_time_series = mode;
	}

	if ( param_line.substr(0, 1) == "W" ){
		int win_index = stoi( param_line.substr(1,-1) )  ;
		std::cout << "[c++] Match! (W", win_index, "\n";
		spm.setWindow( win_index );
	}

	if ( param_line.substr(0, 1) == "x" ){
		int val = stoi( param_line.substr(1,-1) )  ;
		std::cout << "[c++] Match! (x", val, "\n";
		spm.setBlockSkip( val );
	}
}

int read_parameter_fifo()
{
	std::ifstream f;

	while( param_message_enable ){

		for(;;) {
			f.open(spectrum_params_fifo_name, std::ios_base::in);
			if(f.is_open()){
				std::cout << "[c++] Looping, no fifo file found yet...\n";
				break;
			}
			sleep(2);
		}

		std::cout << "** fifo file found **\n";

		while( std::getline(f, param_line ) ){
			got_param_msg = 1;
			std::cout << " : " << param_line << "\n";
			usleep(400000);
			change_param();
			usleep(400000);
			got_param_msg = 0;
			if( ! param_message_enable ){ break; }
		}
		f.close();
	}
	return 0;
}

int main(int argc, char *argv[])
{

//	char *a = argv[1];
//	int num = atoi(a);
//	printf ("num =  %d ", num);
	// fft_blk_length = num;

 //    int opt;
 //    while ((opt = getopt(argc, argv, "ilw")) != -1) {
 //        switch (opt) {
 //        case 'i': std::cout << " -i \n"; break;
 //        case 'l': std::cout << " -l \n"; break;
 //        case 'w': std::cout << " -w \n"; break;
 //        default:
 //            fprintf(stderr, "Usage: %s [-ilw] [file...]\n", argv[0]);
 //            exit(EXIT_FAILURE);
 //        }
	// }

	std::cout << "[c++]Start**\n\n";	
	mkfifo(spectrum_data_fifo_name, 0666);
	mkfifo(spectrum_params_fifo_name, 0666);
	


	std::thread param_io( read_parameter_fifo );
	runner();

	// param_io.join();

	std::cout << "\n[c++]Finish\n";
    return 0;
}







