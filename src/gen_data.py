import numpy
import argparse
import sys

parser = argparse.ArgumentParser(description="""
Generate a data file containing 2 data series in it.

By default, the set of time values for which the 2 data series are
defined will be the same.
""")
parser.add_argument('--format', dest='format', choices=['mwfview', 'vcd', 'ascii'],
                    help="""
                    Format of output file(s).  'ascii' is the ASCII
                    file format expected by the program gaw.  'vcd' is
                    Value Change Dump, a de facto industry standard
                    used by many wavevorm viewers.  'mwfview' is
                    simply one analog value per line, with separate
                    files for each data series, for the mwfview.py
                    program.
                    """)
parser.add_argument('--different-times', dest='different_times',
                    action='store_true',
                    help="""
                    Without this option, all data series will be
                    defined for the same values of time.  With this
                    option, different data series will be defined for
                    different sets of time values.
                    """)
args = parser.parse_known_args()[0]

if args.format is None:
    print("Must specify value for the --format option")
    sys.exit(1)

same_times = True
if args.different_times:
    print("chan1, chan2 data series will be defined"
          " for different sets of time values.")
    same_times = False

def chan1_defined(t):
    return same_times or (t < 0.03)

def chan2_defined(t):
    return same_times or (t > 0.02)


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

# save data as file(s)

if args.format == 'mwfview':
    # "%.5f": total places expand (but leading 0 is not dropped); 5 is
    # decimal places limit.
    # These two commands may take some 25 sec each to execute.
    numpy.savetxt("chan1.py.dat", chan1, fmt="%.5f")
    numpy.savetxt("chan2.py.dat", chan2, fmt="%.5f")

    # These commands should generate two ASCII files of around 8MB each:

    # % du -h *.dat
    # 8.1M	chan1.py.dat
    # 8.1M	chan2.py.dat

elif args.format == 'vcd':

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
        # Print initial values without a '#' line for the time,
        # followed by changes in values at later times.
        for i in range(0, len(t)):
            now = t[i]
            if i != 0:
                print('#%d' % (int(now * 1000000000.0)), file=f)
            if chan1_defined(now):
                print('r%.16g <0' % (chan1[i]), file=f)
            if chan2_defined(now):
                print('r%.16g <1' % (chan2[i]), file=f)

elif args.format == 'ascii':

    print('Writing data to files chan1.asc chan2.asc ...')
    with open('chan1.asc','w') as f:
        print("#time chan1", file=f)
        for i in range(0, len(t)):
            now = t[i]
            if chan1_defined(now):
                print('%.16g' % (now), file=f, end='')
                print(' %.16g' % (chan1[i]), file=f, end='')
                print('', file=f)
    with open('chan2.asc','w') as f:
        print("#time chan2", file=f)
        for i in range(0, len(t)):
            now = t[i]
            if chan2_defined(now):
                print('%.16g' % (now), file=f, end='')
                print(' %.16g' % (chan2[i]), file=f, end='')
                print('', file=f)
