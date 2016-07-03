#ifndef GAWDRAW_H
#define GAWDRAW_H

/*
 * gawdraw.h -  functions to draw the waveform in drawingarea.
 *
 * include LICENSE
 */

typedef struct _WaveDrawMethod WaveDrawMethod;
//typedef void (*WaveDraw_FP) (VisibleWave *vw, WavePanel *wp);

struct _WaveDrawMethod {
	WaveDraw_FP func;
	char *desc;
};

extern WaveDrawMethod wavedraw_method_tab[];

/*
 * prototypes
 */
void gawdraw_ppixel(VisibleWave *vw, WavePanel *wp);
void gawdraw_lineclip(VisibleWave *vw, WavePanel *wp);

#endif /* GAWDRAW_H */
