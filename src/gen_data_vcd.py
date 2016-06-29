import sys
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
t = t * (1 / 25e6)

# printout first and last element - should be '0.000000, 0.040000'
print("%f, %f" % (t[0], t[len(t) - 1]))

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

print('Writing data to file data.vcd ...')
with open('data.vcd','w') as f:
    # Print VCD header and variable definitions
    print("""$comment
File created using gen_data_vcd.py using the following command:
%s
$end
$date
%s
$end
$version
%s
$end
$timescale
1ns
$end
$scope module all $end
$var real 64 <0 chan1 $end
$var real 64 <1 chan2 $end
$upscope $end
$enddefinitions $end
$dumpvars
    """ % (' '.join(sys.argv),
           'tbd - call some function to produce date & time as str',
           'version 1.0'),
          file=f)
    # Print initial values without a '#' line for the time, followed
    # by changes in values at later times.
    for i in range(0, len(t)):
        now = t[i]
        if i != 0:
            print('#%d' % (int(now * 1000000000.0)), file=f)
        print('r%.16g <0' % (chan1[i]), file=f)
        print('r%.16g <1' % (chan2[i]), file=f)
