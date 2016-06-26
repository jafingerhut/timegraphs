# timegraphs
Experiments in code for creating interactive time-based graphs of numerical data


# Purpose

I want to be able to find a way, preferably with open source and/or
free as dollars software to easily create graphs of multiple time
series graphs, and zoom in/out on various subsets of time, with all
graphs locked together in what subset of the time range they show.

A waveform viewer like `gtkwave` is at least close to what I want, or
maybe even exactly what I want, but that remains to be seen.  It
appears that gtkview might have difficulties with analog values, and I
definitely want many or most of the time series of data in the graphs
to have arbitrary ranges of real numerical values, and to control the
min/max value on the Y axis for each one, and ideally to take multiple
graphs and overlay them to share the same Y axis, while at the same
time have other independent Y axes above and below each other.


# References

An article where someone else wrote about their experience trying to
get something similar, and tried out many open source software
packages to achieve it, including `gtkwave`:

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
