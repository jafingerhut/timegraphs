import numpy

# generate time axis - increasing steps of period
# use arrange - from min to max using step
# up to 1000001 so we match scilab example
t = numpy.arange(0,1000001,1)

# printout size - should be 1000001
print(len(t))

# printout first and last element - should be '0, 1000000'
print("%d, %d" % (t[0], t[len(t)-1]))

# scale this array with the period duration of fs=25MHz
t=t*(1/25e6)

# printout first and last element - should be '0.000000, 0.040000'
print("%f, %f" % (t[0], t[len(t)-1]))

# generate data according to equations
# no need to be careful for element-by-element vector multiplication (.*) here;
# here we work with 'arrays', not mathematical 'vector' concepts
# (so, only element-by-element multiplication is possible by default) :
fa1 = 3e3;
fb1 = 50;
fa2 = 4e3;
fb2 = 60;
pi = numpy.pi;
chan1 = (100 * t *
         numpy.sin(2 * pi * fb1 * t) *
         numpy.sin(2 * pi * fa1 * t * numpy.sin(2 * pi * fb1 * t)));
chan2 = (100 * t *
         numpy.sin(2 * pi * fb2 * t) *
         numpy.sin(2 * pi * fa2 * t * numpy.sin(2 * pi * fb2 * t)));

# printout size - same as t
print(len(chan1))

# save data as files 
# format specifier - C
# "%.5f": total places expand (but leading 0 is not dropped); 5 is decimal places limit
# these two commands may take some 25 sec each to execute.. 
numpy.savetxt("chan1.py.dat", chan1, fmt="%.5f")
numpy.savetxt("chan2.py.dat", chan2, fmt="%.5f")

# These commands should generate two ASCII files of around 8MB each:

# % du -h *.dat
# 8.1M	chan1.py.dat
# 8.1M	chan2.py.dat
