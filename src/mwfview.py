# mfview.py
# author: sdaau
# license: GPL
#
#~ Navigation instructions:
#~ * Mouse wheel - zoom in/out
#~ * Ctrl+Mouse wheel - pan
#~ * Shift+LeftClick - place cursor 1
#~ * RightClick - place cursor 2
#~ You can type in GOTO_XC textfield, and press Enter to update:
#~ * c0 - set cursors to 0,0 and don't redraw
#~ * c1 - go to cursor 1 position
#~ * c2 - go to cursor 2 position
#~ * bX - go to Xth marker in self.found[] of Top analysis
#~ * any real number - go to that location in timebase (scientific notation '2e-6' ok)
#~ You can also type an integer in ZOOMX field and press Enter to update.

# started from: http://www.daniweb.com/code/snippet217059.html:
# "explore the mouse wheel with the Tkinter GUI toolkit"...

import tkinter as tk
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from matplotlib.backend_bases import MouseEvent
import matplotlib.patches as patches
import re
import math
import sys
import threading
import queue
import pylab
import time
import pprint
from matplotlib.cbook import CallbackRegistry


# globals
startxlim = [0.0, 5.0]  # starting x range in data coordinates
zcount = 0              # zoom level counter
lastevtime = None       # last event time(stamp)
first_delta_time = 1000 # deltatime that should be calculated for first event
# Create regular expression for x,y parsing in wheel_scroll_zoomx.
xy_parsing_regex = re.compile('[ =]+')
first_update_time = None
num_xlim_changed_events = 0



def set_xlim_all(xlim_min, xlim_max):
    # modified in this function
    global ax_sub1
    global ax_sub2

    debug_set_xlim_all = False

    if debug_set_xlim_all:
        print('set_xlim_all: [%10.8f, %10.8f]' % (xlim_min, xlim_max), end='')
    for ax in [ax_sub1, ax_sub2]:
        # This is probably a bit too much of a hack, and there is a
        # better way to structure the GUI code than I have done here,
        # but if we unconditionally call set_xlim here, then there is
        # an infinite recursion of calls between
        # do_axes_xlim_changed() and this function when either one of
        # them is called.

        # This can be avoided by only calling set_xlim here only if it
        # actually causes a change to the axes in question.
        cur_viewlim_points = ax.viewLim.get_points()
        cur_xmin = cur_viewlim_points[0][0]
        cur_xmax = cur_viewlim_points[1][0]
        if cur_xmin == xlim_min and cur_xmax == xlim_max:
            if debug_set_xlim_all:
                print(' %s skip' % (ax.rowNum), end='')
        else:
            if debug_set_xlim_all:
                print(' %s call' % (ax.rowNum), end='')
            ax.set_xlim(xlim_min, xlim_max)
    if debug_set_xlim_all:
        print('')


def mouse_wheel_up(event):
    return event.num == 5 or event.delta == -120


def mouse_wheel_down(event):
    return event.num == 4 or event.delta == 120


def wheel_scroll_zoomx(event, deltatime):
    # modified in this function
    global zcount
    # read only in this function
    global ax_sub1
    global startxlim

    debug_wheel_scroll_zoomx = False
    if debug_wheel_scroll_zoomx:
        print('wheel_scroll_zoomx:', end='')

    # Use deltatime to calculate a change in zcount from
    # min_zcount_change to max_zcount_change.  Faster moves give
    # larger changes.
    max_zcount_change = 5
    min_zcount_change = 1
    speedfact = max_zcount_change * (100.0 - deltatime) / 100.0
    if debug_wheel_scroll_zoomx:
        print(' speedfact 1: %s' % (speedfact), end='')
    if speedfact < min_zcount_change:
        speedfact = min_zcount_change
    speedfact = int(math.ceil(speedfact))
    if debug_wheel_scroll_zoomx:
        print(' final: %s' % (speedfact), end='')
    
    # respond to Linux or Windows wheel event
    if mouse_wheel_up(event):
        zcount -= speedfact
    elif mouse_wheel_down(event):
        zcount += speedfact
    if debug_wheel_scroll_zoomx:
        print(' zcount=%s' % (zcount), end='')
        print('')
    xmin_datac, xmax_datac = ax_sub1.get_xlim()

    # Get the mouse x,y pos from x,y string written in toolbar.
    # It is in proper data coords
    tmsgcoords = toolbar.message.get()
    if tmsgcoords == "":
        return
    tmsgcs = xy_parsing_regex.split(tmsgcoords)
#    if debug_wheel_scroll_zoomx:
#        print('tmsgcoords=%s' % (tmsgcoords))
#        print('tmsgcs=%s' % (tmsgcs))

    # Skip past any other strings before the "x" for the x coord, e.g.
    # "pan/zoom".
    idx = 0
    while idx < len(tmsgcs) and tmsgcs[idx] != 'x':
        idx += 1
    tmsgcs = tmsgcs[idx:]
#    if debug_wheel_scroll_zoomx:
#        print('tmsgcs[1]=%s tmsgcs[3]=%s' % (tmsgcs[1], tmsgcs[3]))
    mous_xloc_datac = float(tmsgcs[1])
    mous_yloc_datac = float(tmsgcs[3])
    
    oxrange = xmax_datac - xmin_datac
    odxright = xmax_datac - mous_xloc_datac
    odxleft = mous_xloc_datac - xmin_datac
    
    # We need to refer to some constant starting range, then scaling
    # works fine.
    newxrange = (startxlim[1] - startxlim[0]) / (1.1 ** zcount)
    nrxfact = newxrange / oxrange
    
    set_xlim_all(mous_xloc_datac - odxleft * nrxfact,
                 mous_xloc_datac + odxright * nrxfact)
    
    client.queue.put("update")


def wheel_scroll_panx(event, deltatime):
    # read only in this function
    global ax_sub1

    debug_wheel_scroll_panx = False
    if debug_wheel_scroll_panx:
        print('wheel_scroll_panx:', end='')

    movedir = 0
    # respond to Linux or Windows wheel event
    if mouse_wheel_up(event):
        movedir = -1
    elif mouse_wheel_down(event):
        movedir = 1
    
    xmin_datac, xmax_datac = ax_sub1.get_xlim()
    xrange = xmax_datac - xmin_datac
    
    # Use deltatime to calculate a change in zcount from
    # min_zcount_change to max_zcount_change.  Faster moves give
    # larger changes.
    min_move = 0.05
    max_move = 0.35
    speedfact = max_move * (100.0 - deltatime) / 100.0
    if speedfact < min_move:
        speedfact = min_move
    if debug_wheel_scroll_panx:
        print(' movedir=%s speedfact=%s' % (movedir, speedfact), end='')
        print('')
    
    xmoveammount = speedfact * movedir * xrange
    set_xlim_all(xmin_datac + xmoveammount, xmax_datac + xmoveammount)
    
    client.queue.put("update")


def updateWindow():
    # modified in this function
    global first_update_time
    # read only in this function
    global ax_sub1
    global zcount

    debug_updateWindow = False
    if debug_updateWindow:
        now = time.time()
        if first_update_time is None:
            first_update_time = now
        print('updateWindow: time=%s' % (now - first_update_time))

    #~ abmT.redraw() # should go fist, as they may delete the cursor ellipse
    #~ abmB.redraw()
    cursorT1.redraw()
    cursorB1.redraw()
    cursorT2.redraw()
    cursorB2.redraw()
    scrbarT.redraw()
    try:
        canvas.show() # http://old.nabble.com/Tkinter-problems-td22164234.html
    except:
        print("canvas 'crashed', not redrawing.. ")
    root.update_idletasks()
    canvas.get_tk_widget().update_idletasks()
    toolbar.push_current() # to keep the zoom history!
    # show central x value in textfield
    xmin_datac, xmax_datac = ax_sub1.get_xlim()
    xrange = xmax_datac - xmin_datac
    gototf.delete(0, tk.END)
    gototf.insert(0, xmin_datac + 0.5 * xrange)
    zoomtf.delete(0, tk.END)
    zoomtf.insert(0, zcount)
    dxtf.delete(0, tk.END)
    dxtf.insert(0, "%.2e|%.2e" % (cursorT2.xpos - cursorT1.xpos,
                                  cursorT2.ypos - cursorT1.ypos))
    dytf.delete(0, tk.END)
    dytf.insert(0, "%.2e|%.2e" % (cursorB2.xpos - cursorB1.xpos,
                                  cursorB2.ypos - cursorB1.ypos))


def mouse_wheel(event):
    # modified in this function
    global lastevtime
    # read only in this function
    global first_delta_time

    # See if any modifier keys are pressed.
    debug_mouse_wheel = False

    # calc delta event time
    if lastevtime is None:
        lastevtime = event.time - first_delta_time
    deltatime = event.time - lastevtime
    lastevtime = event.time

    if debug_mouse_wheel:
        print('\nmouse_wheel: event.state=%s .num=%s .delta=%s deltatime=%s'
              '' % (event.state, event.num, event.delta, deltatime))
    if event.state == 0: # no modifier keys pressed
        wheel_scroll_zoomx(event, deltatime)
    elif event.state == 1: # shift key held down
        pass
    elif event.state == 4: # ctrl key held down
        wheel_scroll_panx(event, deltatime)
    elif event.state == 8: # alt key held down
        pass


def do_axes_xlim_changed(event):
    # modified in this function
    global num_xlim_changed_events

    debug_do_axes_xlim_changed = False

    num_xlim_changed_events += 1
#    if num_xlim_changed_events == 10:
#        print('do_axes_xlim_changed: event=%s event.__dict__='
#              '' % (event))
#        pprint.pprint(event.__dict__)
#        print('    event.xaxis.__dict__=')
#        pprint.pprint(event.xaxis.__dict__)
#        print('    event.yaxis.__dict__=')
#        pprint.pprint(event.yaxis.__dict__)
#    print('do_axes_xlim_changed: #%d numCols=%s numRows=%s rowNum=%s colNum=%s'
#          '' % (num_xlim_changed_events,
#                event.numCols, event.numRows, event.rowNum, event.colNum))
#    print('    transAxes=%s' % (event.transAxes))
#    print('    transLimits=%s' % (event.transLimits))
#    print('    viewLim=%s' % (event.viewLim))
#    print('ax_sub1.__dict__=')
#    pprint.pprint(ax_sub1.__dict__)

    if debug_do_axes_xlim_changed:
        viewLim_points = ax_sub1.viewLim.get_points()
        xmin = viewLim_points[0][0]
        ymin = viewLim_points[0][1]
        xmax = viewLim_points[1][0]
        ymax = viewLim_points[1][1]

        print('event.rowNum=%s' % (event.rowNum))
        print('    event.viewLim   x [%10.8f, %10.8f]'
              '' % (event.viewLim.x0, event.viewLim.x1))
        print('    ax_sub1.viewLim x [%10.8f, %10.8f]'
              '' % (xmin, xmax))
        print('    event.viewLim   y [%10.8f, %10.8f]'
              '' % (event.viewLim.y0, event.viewLim.y1))
        print('    ax_sub1.viewLim y [%10.8f, %10.8f]'
              '' % (ymin, ymax))

    set_xlim_all(event.viewLim.x0, event.viewLim.x1)
    client.queue.put("update")


def gototf_Return(self):
    # read only in this function
    global ax_sub1

    debug_gototf_Return = False

    gotoval = 0.0
    gototfs = gototf.get()
    if debug_gototf_Return:
        print('gototfs=%s' % (gototfs))
    if gototfs[0] == "c":
        try:
            if gototfs[1] == "0": # send back cursors
                cursorT1.xpos = 0
                cursorT1.ypos = 0
                cursorB1.xpos = 0
                cursorB1.ypos = 0
                cursorT2.xpos = 0
                cursorT2.ypos = 0
                cursorB2.xpos = 0
                cursorB2.ypos = 0
                return # don't redraw
            if gototfs[1] == "1":
                # just grab any of the cursor 1's xpos  into gotoval
                gotoval = cursorT1.xpos
            if gototfs[1] == "2":
                # just grab any of the cursor 1's xpos  into gotoval
                gotoval = cursorT2.xpos
        except:
            return

    elif gototfs[0] == "b":
        # ONLY for analysis with .found present!
        # and only in respect to first channel (Top)..
        # parse number after bXX, and go to that marker...
        # 1-based type b1 to go to first (zeroth index) marker
        try:
            gotoval = t[abmT.found[int(gototfs[1:]) - 1]]
        except:
            print("Error, not going anywhere: ",
                  sys.exc_info()[1], sys.exc_info()[0])
            return
    else:
        try:
            gotoval = float(gototf.get())
        except:
            print("Error, not going anywhere: ",
                  sys.exc_info()[1], sys.exc_info()[0])
            return
    # here we are fine,
    # center current zoom level around requested x value
    xmin_datac, xmax_datac = ax_sub1.get_xlim()
    xrange = xmax_datac - xmin_datac
    set_xlim_all(gotoval - 0.5 * xrange,
                 gotoval + 0.5 * xrange)
    
    client.queue.put("update")


def zoomtf_Return(self):
    # modified in this function
    global zcount
    # read only in this function
    global ax_sub1
    global startxlim

    zoomval = 0.0
    try:
        zoomval = int(zoomtf.get())
    except:
        print("Error, not going anywhere: ",
              sys.exc_info()[1], sys.exc_info()[0])
        return

    zcount = zoomval
    
    # recalculate zoom in respect to midpoint
    xmin_datac, xmax_datac = ax_sub1.get_xlim()
    
    oxrange = xmax_datac - xmin_datac
    mous_xloc_datac = xmin_datac + 0.5*oxrange
    odxright = xmax_datac - mous_xloc_datac
    odxleft = mous_xloc_datac - xmin_datac
    
    # We need to refer to some constant starting range, then scaling
    # works fine.
    newxrange = (startxlim[1] - startxlim[0]) / (1.1 ** zcount)
    nrxfact = newxrange / oxrange
    
    set_xlim_all(mous_xloc_datac - odxleft * nrxfact,
                 mous_xloc_datac + odxright * nrxfact)
    
    client.queue.put("update")



# http://code.activestate.com/recipes/82965-threads-tkinter-and-asynchronous-io/download/1/
class ThreadedClient:
    """
    Launch the main part of the GUI and the worker thread. periodicCall and
    endApplication could reside in the GUI part, but putting them here
    means that you have all the thread controls in a single place.
    """
    def __init__(self, master):
        """
        Start the GUI and the asynchronous threads. We are in the main
        (original) thread of the application, which will later be used by
        the GUI. We spawn a new thread for the worker.
        """
        self.master = master

        # Create the queue
        self.queue = queue.Queue()

        self.running = 1

        # Start the periodic call to check if the queue contains
        # anything
        self.periodicCall()

    def periodicCall(self):
        """
        Check every 100 ms if there is something new in the queue.
        Handle all the messages currently in the queue (if any).
        """
        doUpdate = 0
        #~ print("self.queue.qsize", self.queue.qsize())
        while self.queue.qsize():
            try:
                msg = self.queue.get(0)
                # There were some messages, so do update
                doUpdate = 1
            except queue.Empty:
                doUpdate = 0 # don't do updates
        if not self.running:
            # This is the brutal stop of the system. You may want to do
            # some cleanup before actually shutting it down.
            import sys
            sys.exit(1)
        #~ print(doUpdate, self.queue.qsize())
        if (doUpdate):
            updateWindow()
        # 66 ms for cca 15 fps
        self.master.after(66, self.periodicCall)
    
    def endApplication(self):
        self.running = 0



class ScrollBarVis:
    """
    Not actual Scrollbar, just visualisation in a thin line of bottom of graph
    # there are no standalone scrollbars in tkInter: http://www.janitorprogrammer.com/PythonIDE.html
    # they must be attached to something via callback mechanisms ;
    # hence 'xscrollbar = tk.Scrollbar(root, orient=tk.HORIZONTAL)' one will not have any width...
    # easier to draw manually
    """
    def __init__(self, ax, t):
        self.wh=0.05
        self.bar = \
            patches.Rectangle((0.0, 0.0), width=1.0, height=self.wh, alpha=0.5,
                              axes=ax, transform=ax.transAxes,
                              facecolor='#aaaaaa')
        self.head = \
            patches.Rectangle((0.5, 0.0), width=0.1, height=self.wh, alpha=0.8,
                              axes=ax, transform=ax.transAxes,
                              facecolor='#aaaaaa')
        self.ax = ax
        self.ax.add_artist(self.bar)
        self.ax.add_artist(self.head)
        self.t = t

    def redraw(self):
        mint = self.t[0]
        maxt = self.t[len(self.t) - 1]
        xmin_datac, xmax_datac = self.ax.get_xlim()
        l_rel = (xmin_datac - mint) / (maxt - mint)
        r_rel = (xmax_datac - mint) / (maxt - mint)
        self.head.remove()
        self.head = \
            patches.Rectangle((l_rel, 0.0), width=r_rel - l_rel, height=self.wh,
                              alpha=0.8, axes=self.ax,
                              transform=self.ax.transAxes, facecolor='#aaaaaa')
        self.ax.add_artist(self.head)



debug_SnaptoCursor = False

# http://matplotlib.sourceforge.net/examples/pylab_examples/cursor_demo.html
class SnaptoCursor:
    """
    Like Cursor but the crosshair snaps to the nearest x,y point
    For simplicity, I'm assuming x is sorted
    """
    def __init__(self, ax, x, y, id):
        # http://matplotlib.sourceforge.net/examples/axes_grid/simple_anchored_artists.html
        # Just an init here. Eelse we should use an Ellipse to render
        # a proper circle.
        if debug_SnaptoCursor:
            print('SnaptoCursor.__init__(self, ax=%s (%s), x=%s, y=%s, id=%s)'
                  '' % (ax, type(ax), x, y, id))
        markrect = patches.Circle((0.2, 0.2), radius=0.2, alpha=0.5,
                                  axes=ax, transform=ax.transData)
        ax.add_artist(markrect)

        self.ax = ax
        self.id = id
        if id == 1:
            self.color = '#00ff00'
        if id == 2:
            self.color = '#ee00ee'
        self.markrect = markrect
        self.lx = ax.axhline(color=self.color)  # the horiz line
        self.ly = ax.axvline(color=self.color)  # the vert line
        self.x = x
        self.y = y
        self.xpos = 0.0
        self.ypos = 0.0
        # text location in axes coords
        self.txt = ax.text(0.7, 0.9, '', transform=ax.transAxes)

    def updatePress(self, event):
        if debug_SnaptoCursor:
            not_inaxes = not event.inaxes
            print('SnaptoCursor.updatePress() not .inaxes=%s'
                  ' .key=%s .button=%s .dblclick=%s self.id=%s'
                  '' % (not_inaxes,
                        event.key, event.button, event.dblclick, self.id))
        if not event.inaxes:
            return
        
        # Make sure the main window is in focus, else event.key will
        # be NULL, even if clicks are registered!
        
        cursor_set_event = False
        if self.id == 1:
            # Cursor 1 is moved by this kind of event
            if event.button == 1 and event.key == "shift":
                cursor_set_event = True
        elif self.id == 2:
            # Was originally: event.key == "control"
            if event.button == 3:
                cursor_set_event = True
        if not cursor_set_event:
            return
        
        x, y = event.xdata, event.ydata

        indx = pylab.searchsorted(self.x, [x])[0]
        self.xpos = self.x[indx]
        self.ypos = self.y[indx]
        
        client.queue.put("update")
        
    def redraw(self):

        # update the line positions
        self.lx.set_ydata(self.ypos)
        self.ly.set_xdata(self.xpos)
        
        # find xpos, ypos, which are data coords - expressed in axes-coords
        tp = self.ax.transAxes.inverted().transform_point( self.ax.transData.transform_point( (self.xpos, self.ypos) ) )
        otx, oty = self.txt.get_position()
        self.txt.set_position( (tp[0], oty) )

        # Find how big is a length of 1 in axes-coords in x and y
        # direction, expessed in data coords (with current zoom).
        # Find the lengths as difference between axes-coords points
        # (2,2) - (1,1)
        tps = self.ax.transData.inverted().transform_point( (1, 1) )
        tpsb = self.ax.transData.inverted().transform_point( (2, 2) )
        dpts = tpsb - tps
        
        # MUST USE ELLIPSE TO RENDER A CIRCLE, since here our x and y
        # scales are not equal!

        # If I draw in transAxes, I'll get a circle, but it will not
        # stay put where it is.  If I draw in transData, circle stays
        # put (i.e. moves with data), but zoom will mess up its scale.
        # Also, must remove then add - since "patches.Ellipse" has no
        # method to change position.
        relCircleSize = 15
        self.markrect.remove()
        self.markrect = \
            patches.Ellipse((self.xpos, self.ypos),
                            width=relCircleSize * dpts[0],
                            height=relCircleSize * dpts[1],
                            alpha=0.6, axes=self.ax,
                            transform=self.ax.transData, facecolor=self.color)
        self.markrect.set_zorder(100) # bring to foreground
        self.ax.add_artist(self.markrect)

        self.txt.set_text('x=%1.2f, y=%1.2f' % (self.xpos, self.ypos))



class AnalysisTransitions:
    """
    attempt to analyze data,
    identify each positive crossing over 1
    and select only those representing certain length
    
    In this example, results are drawn in getStats,
    as they are expected to be few, and so can remain
    on graph at all times
    
    However, if analysis results with thousands of items,
    then it is better to calculate how many results
    are visible in given range in 'shouldIRender', and
    then 'clearMarks' and 'redraw' accordingly -
      here skeletons are given just for reference.
    """
    def __init__(self, ax, xt, yt):
        print("Analysin' transitions.. ")
        self.ax = ax
        self.xt = xt
        self.yt = yt
        self.marks=[]
        prevval=0.0
        nowval=0.0
        index=0
        self.found=[]
        self.torender=[]
        started = 0
        while index < len(xt):
            nowval=yt[index]
            if nowval >= threshold and prevval < threshold:
                    self.found.append(index)
            prevval = nowval
            index += 1
        print("found +1 transitions: ", len(self.found))
        self.getStats()
        
    def getStats(self):
        print("Transition delta stats:")
        stats=[]
        self.torender=[]
        nowval = prevval = found = 0
        for nowval in self.found:
            delta = nowval-prevval
            if len(stats) == 0:
                stats.append([delta, nowval, self.xt[nowval], 1])
            else:
                found = 0
                for tarr in stats:
                    if tarr[0] == delta:
                        tarr[3] += 1
                        found = 1
                        break
                if not found:
                    stats.append([delta, nowval, self.xt[nowval], 1])
                    if delta >= 10000 and delta <= 40000:
                        self.torender.append([nowval, delta])
            prevval = nowval
        # end for
        print(len(stats), ":: ")
        print(len(self.torender))
        #~ for item in stats:
            #~ print("%d times for delta=%d, first at %e" % (item[3], item[0], item[2]))
        # these items not need be redrawn, they are few - so draw them now
        ind=0
        while ind < len(self.torender):
            nd=self.torender[ind]
            prevind = nd[0]-nd[1]
            avl = self.ax.axvspan(self.xt[prevind], self.xt[nd[0]], color='#00ffee')
            self.marks.append(avl)
            antorder = self.ax.annotate("%d: DELAY %d ticks" % (ind+1, nd[1]),
                xy=(self.xt[prevind], threshold),
                xytext=(self.xt[prevind], -4),
                bbox=dict(boxstyle="round", fc="0.8"), )
            antorder.set_font_properties(":size=8")
            antorder.set_fontname("Arial")
            self.marks.append(antorder)
            ind += 1


    def shouldIRender(self):
        #~ xmin_datac, xmax_datac = self.ax.get_xlim()
        #~ xrange = xmax_datac - xmin_datac
        #~ # see how many transitions are present in this range
        #~ xminind = int(xmin_datac / dt)
        #~ xmaxind = int(xmax_datac / dt)
        #~ # and update torender
        #~ self.torender=[]
        return 0
        
    def clearMarks(self):
        #~ .remove() doesn't seem to work here, so:
        while len(self.ax.texts): # this deletes annotations (text)
            self.ax.texts.pop()
        while len(self.ax.patches): # this deletes patches - ellipses etc - also the cursor ellipse!
            self.ax.patches.pop()
        self.marks = []
        
    def redraw(self):
        #~ numbiv = self.shouldIRender() #number of transitions in view
        #~ if numbiv <= 0:
            #~ return
        #~ # clear marks first if not clear already
        #~ ## if len(self.marks) > 0: self.clearMarks()
        #~ # if not in rendering range, return
        #~ # render
        #~ # apparently drawing kills the axis range, re-set it!
        #~ ## self.ax.set_xlim(txlim)
        return




######################################################################
# MAIN
######################################################################

debug_main = False

# instantiate Tkinter
root = tk.Tk()
root.title('MouseWheel Waveform Viewer')
root['bg'] = 'darkgreen'

########################################
# GENERATE bottom frame
########################################

# bottom(er) frame - for additional textfields etc.
# This section should be *first*; then in window, the bottomer is
# *below* the navigation toolbar ?!  Use Frame to be able to align
# bottoms next to each other, on bottom of window.
bottomer = tk.Frame(root)
bottomer.pack(side=tk.BOTTOM)

bottomfont = ('courier', 10, 'bold')

# In order of appearance, left to right:
label2 = tk.Label(bottomer, font=bottomfont, width=7)
label2.pack(side=tk.LEFT,padx=5,pady=5)
label2['text']="GOTO_XC"

gototf = tk.Entry(bottomer, width=10)
gototf.pack(side=tk.LEFT,padx=5,pady=5)
gototf.insert(0, "[]")

label = tk.Label(bottomer, font=bottomfont, width=5)
label.pack(side=tk.LEFT)
label['text']="ZOOMX"

zoomtf = tk.Entry(bottomer, width=8)
zoomtf.pack(side=tk.LEFT,padx=5,pady=5)
zoomtf.insert(0, "0")

labeldx = tk.Label(bottomer, font=bottomfont, width=5)
labeldx.pack(side=tk.LEFT)
labeldx['text']="d|xyT"

dxtf = tk.Entry(bottomer, width=18)
dxtf.pack(side=tk.LEFT,padx=5,pady=5)
dxtf.insert(0, "0")

labeldy = tk.Label(bottomer, font=bottomfont, width=5)
labeldy.pack(side=tk.LEFT)
labeldy['text']="d|xyB"

dytf = tk.Entry(bottomer, width=18)
dytf.pack(side=tk.LEFT,padx=5,pady=5)
dytf.insert(0, "0")


########################################
# GET DATA
########################################

# load files - numpy.loadtxt, numpy.genfromtxt both work
# may take a while for large files..
# we assume len(chan1)=len(chan2) without checking here

print("Loading chan1...")
chan1 = np.loadtxt("chan1.py.dat")
print("Loading chan2...")
chan2 = np.loadtxt("chan2.py.dat")
if debug_main:
    print("type(chan1)=%s len(chan1)=%s" % (type(chan1), len(chan1)))

# for testing, use:
#~ chan1=np.arange(0, 5, 0.05)
#~ chan2=np.arange(0, 6, 0.06)


########################################
# GENERATE TIMEBASE
########################################

# delta t - based on sampling freq, 25MHz
frq = 25e6
dt = 1.0 / frq
# endtime is not included due open interval,
# so can use len() instead of len()-1
endtime = len(chan1) * dt
if debug_main:
    print("dt, endtime:", dt, endtime)
t = np.arange(0, endtime, dt)
if debug_main:
    print("type(t)=%s len(t)=%s" % (type(t), len(t)))

# ##### END GENERATE TIMEBASE


# at start, view starting 10% of loaded data
startxlim = [t[0], t[int(0.1 * len(chan1))]]
if debug_main:
    print('startxlim=%s' % (startxlim))


########################################
# GENERATE Figure, plots
########################################

f = Figure(figsize=(7,3), dpi=100)

ax_sub1 = f.add_subplot(2, 1, 1)
ax_sub1.plot(t, chan1, 'b-')
if debug_main:
    print('type(ax_sub1)=%s ax_sub1=%s' % (type(ax_sub1), ax_sub1))

ax_sub1.set_xlim(startxlim[0], startxlim[1])
ax_sub1.set_xlabel('time')
ax_sub1.set_ylabel('chan1')
ax_sub1.grid(True)

ax_sub2 = f.add_subplot(2, 1, 2)
ax_sub2.plot(t, chan2, 'r-')

ax_sub2.set_xlim(startxlim[0], startxlim[1])
ax_sub2.set_xlabel('time')
ax_sub2.set_ylabel('chan2')
ax_sub2.grid(True)

# In xlim_changed or ylim_changed callback events on the axes, ax_sub1
# should have rowNum=0, colNum=0.  ax_sub2 will have rowNum=1 colNum=0.
axis = [ [ax_sub1],
         [ax_sub2] ]

# I want panning of one graph in the X direction to cause the other
# graph(s) to move with them.  One way to do that is to register a
# callback function for the event that the limits of a graph's X axis
# have changed, and update other axes if necessary.

# Inspired by example code found here:
# http://matplotlib.org/examples/event_handling/viewlims.html
for ax in [ax_sub1, ax_sub2]:
    ax.callbacks.connect('xlim_changed', do_axes_xlim_changed)


########################################
# SETUP canvas, toolbar;
########################################

# So that the plot is in the main Tk window, and not in a separate
# window!  it is a tk.DrawingArea
canvas = FigureCanvasTkAgg(f, master=root)
canvas.show()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

toolbar = NavigationToolbar2TkAgg(canvas, root)
toolbar.update()
canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)


########################################
# ADD additional widgets - cursors, etc
########################################

# cursors
cursorT1 = SnaptoCursor(ax_sub1, t, chan1, 1)
cursorB1 = SnaptoCursor(ax_sub2, t, chan2, 1)
cursorT2 = SnaptoCursor(ax_sub1, t, chan1, 2)
cursorB2 = SnaptoCursor(ax_sub2, t, chan2, 2)

# "scrollbar"
scrbarT = ScrollBarVis(ax_sub1, t)


# ##### 'global' consts, for AnalysisTransitions:
threshold = 1.0
# ##### END 'global' consts:

# analysis
#~ abmT = AnalysisTransitions(ax_sub1, t, chan1)
#~ abmB = AnalysisTransitions(ax_sub2, t, chan2)

########################################
# END ADD additional widgets - cursors, etc
########################################


########################################
# SETUP UI interaction bindings
########################################

# root.bind is OK; toolbar.bind passes, but no reaction
# f.,a.bind don't work - tk_widget or not; canvas.get_tk_widget() is OK
#
# with Windows OS
canvas.get_tk_widget().bind("<MouseWheel>", mouse_wheel)
# with Linux OS
canvas.get_tk_widget().bind("<Button-4>", mouse_wheel)
canvas.get_tk_widget().bind("<Button-5>", mouse_wheel)

gototf.bind("<Return>", gototf_Return)
zoomtf.bind("<Return>", zoomtf_Return)

#~ connect('motion_notify_event', cursorT1.mouse_move)
cidT1 = canvas.mpl_connect('button_press_event', cursorT1.updatePress)
cidB1 = canvas.mpl_connect('button_press_event', cursorB1.updatePress)
cidT2 = canvas.mpl_connect('button_press_event', cursorT2.updatePress)
cidB2 = canvas.mpl_connect('button_press_event', cursorB2.updatePress)

########################################
# END SETUP UI interaction bindings
########################################


# reset init bounds once more
set_xlim_all(startxlim[0], startxlim[1])

# init all once - well, not running update here saves
#   a long time wait for plot redraw at start...
#updateWindow()

# start the graphics update thread
client = ThreadedClient(root)

# start main loop
root.mainloop()
