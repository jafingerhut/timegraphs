# timegraphs
Experiments in code for creating interactive time-based graphs of numerical data


# Purpose

I want to be able to find a way, preferably with open source and/or
free as in dollars software, to easily create interactive charts of
multiple `data series` over a selected range of time, and easily zoom
in/out or pan forward/back on different ranges of time, with all
graphs always showing the same range of time as each other.

I will use the term `data series` for a single measurement/value that
varies over time.  This is roughly consistent with how Microsoft Excel
uses the term data series.  In my case, the "X value" is always time,
but the "Y value" for each data series may have different ranges and
even different units from each other.

In general, there will be several data series, from 3 or 4 up to
dozens (perhaps growing to hundreds in the future).  Two different
data series might have measurements for the same set of time values,
or completely different (even disjoint) sets of time values.  It
should be possible to plot a data series only at the time values for
which it has measurements in the recorded data.  Interpolation with
straight lines or a smoothed curve may be nice, but not necessary.

A waveform viewer like `gtkwave` is at least close to what I want.

One feature that `gwave` and `gaw` seem to have, but perhaps `gtkwave`
does not, is the ability to display multiple data series sharing a
single Y axis.  `gtkwave` appears to require each data series to have
a separate Y axis from each other, so they cannot be overlaid on top
of each other.  [Here](http://gwave.sourceforge.net/gwave.png) is a
link with a screenshot of `gwave`, where you can see multiple data
series sharing a single Y axis.


# Software package home pages

* `gtkwave` [http://gtkwave.sourceforge.net/](http://gtkwave.sourceforge.net/)
* `gwave` [http://gwave.sourceforge.net](http://gwave.sourceforge.net)
* `gaw` [http://gaw.tuxfamily.org](http://gaw.tuxfamily.org)
* `matplotlib` [http://matplotlib.org](http://matplotlib.org)


# Installation steps

These steps have last been tried in July 2016, with whatever versions
were available via the respective package managers on public servers.

OS X install steps have been tried on a Mac running OSX 10.10.5 with
MacPorts 2.3.4 installed.

Linux install steps have been tried on a virtual machine running
Ubuntu 14.04 LTS.

| Software | OS X | Linux |
| -------- | ---- | ----- |
| gtkwave | `sudo port install gtkwave` installed version 3.3.48 | `sudo apt-get install gtkwave` installed version 3.3.58 (package version 3.3.58-1) |
| gaw | [1] | [1] |
| gwave | | `sudo apt-get install gwave` installed (non-functioning [2]) package version 20090213-4 |
| matplotlib | `sudo port install py34-matplotlib` installed incomplete [3] version 1.5.1 (package version 1.5.1_3) | `sudo apt-get install python3-matplotlib` installed version 1.3.1 (package version 1.3.1-1ubuntu5) |


[1] `gaw` installation steps

I could not find `gaw` available as an Ubuntu package, so build it
from source code instead.  Ubuntu 14.04 has GTK+ binaries installed by
default already, but to build `gaw` from source also requires the
following package, which contains header and development files needed
for building GTK+ applications.

    sudo apt-get install libgtk-3-dev

Downloaded the most recent version of `gaw` available as of July 2,
2016, which was this:

* [http://download.tuxfamily.org/gaw/download/gaw3-20160305.tar.gz](http://download.tuxfamily.org/gaw/download/gaw3-20160305.tar.gz)

Use `tar` to uncompress and untar it, then follow instructions in file
`INSTALL`, i.e. `./configure`, `make`.  Binary built as `src/gaw`.

There was a MacPorts package named `gaw`, but the version number
looked a bit older than the most recent one.  Downloading the source
and following the `INSTALL` steps above worked on my OS X machine.  It
may have required that I had previously installed the `gtk3` MacPorts
package.


[2] Notes on `gwave` being non-functional

gwave (package version 20090213-4)

Install command: sudo apt-get install gwave

Always fails with `Segmentation fault (core dumped)` every time I run
it, even with a command line like `gwave -h` or `gwave --version`.

I found this Ubuntu bugs page with an issue filed for this.  It
appears to have been around for several versions of Ubuntu starting
about 14.04 and continuing onwards.

* https://bugs.launchpad.net/ubuntu/+source/gwave/+bug/1311839

I tried installing gwave on an Ubuntu 16.04 virtual machine.  It was
package version 20090213-6, and also gave seg fault when attempting to
run it.

Two of the comments on that issue mention `gaw` as an alternative for
`gwave`, so I tried that out, too.


[3] Notes on how OS X `matplotlib` 1.5.1_3 is incomplete

TBD: Is there a bug open for this issue?

matplotlib 1.5.1 (package version 1.5.1_3)

Install command: sudo port install py34-matplotlib

Note: Some native binary needed by `import` statments in the program
mwfview.py are not present, as demonstrated by this attempt.

    >>> from matplotlib.backends.backend_tkagg import NavigationToolbar2TkAgg
    >>> Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "/opt/local/Library/Frameworks/Python.framework/Versions/3.4/lib/python3.4/site-packages/matplotlib/backends/backend_tkagg.py", line 13, in <module>
        import matplotlib.backends.tkagg as tkagg
      File "/opt/local/Library/Frameworks/Python.framework/Versions/3.4/lib/python3.4/site-packages/matplotlib/backends/tkagg.py", line 9, in <module>
        from matplotlib.backends import _tkagg
    ImportError: cannot import name '_tkagg'

Investigating slightly deeper, I found the following differences in
files containing `tkagg` as part of their names on my Mac, vs. the
Ubuntu VM where the import statement above worked fine.

First I did this command to find out where the files were, on the Mac:

    % find /opt/local/ | grep tkagg

From the output, I found that all of the files were in the directory
below:

    % cd /opt/local/Library/Frameworks/Python.framework/Versions/3.4/lib/python3.4/site-packages/matplotlib/backends
    % find . | grep tkagg
    ./__pycache__/backend_gtkagg.cpython-34.pyc
    ./__pycache__/backend_tkagg.cpython-34.pyc
    ./__pycache__/tkagg.cpython-34.pyc
    ./backend_gtkagg.py
    ./backend_tkagg.py
    ./tkagg.py

Here are the corresponding files from the Ubuntu VM:

    $ find /usr | grep tkagg

Again, from the output, all of the files were in the directory below:

    $ cd /usr/lib/python3/dist-packages/matplotlib/backends
    $ find . | grep tkagg
    ./_tkagg.cpython-34m-x86_64-linux-gnu.so
    ./__pycache__/backend_gtkagg.cpython-34.pyc
    ./__pycache__/backend_tkagg.cpython-34.pyc
    ./__pycache__/tkagg.cpython-34.pyc
    ./backend_gtkagg.py
    ./backend_tkagg.py
    ./tkagg.py



# References

An article where someone else wrote about their experience trying to
get something similar, and tried out many open source software
packages to achieve it, including `gtkwave`, `gwave`, and
`matplotlib`:

* https://wiki.ubuntu.com/Waveform_Viewers-Plotting_Large_Analog_Data

It appears that the author of that article (I could only find their
user name `sdaau`, not their full name) also wrote some Python code
that uses the `matplotlib` Python library that might do what I want,
but will probably need some modifications to suit my purposes.

* `mwfview.py` - https://sourceforge.net/p/sdaaubckp/code/HEAD/tree/single-scripts/mwfview.py
* `mwfview-ser.py` - https://sourceforge.net/p/sdaaubckp/code/HEAD/tree/single-scripts/mwfview-ser.py

As of June 26, 2016, the files at the links above were dated Sep 25,
2010.  I have put copies of the original versions into the directory
`src/orig` of this repository, for reference.
