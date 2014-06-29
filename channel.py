"""
channel.py
Channel object for GALFACTS transient search
02 June 2014 - Trey Wenger - creation
25 June 2014 - Modified by jkania to better handle missing fluxtimexxxx.dat files fit calgary's file stucture
28 June Modified by jkania to improve missing file handling 
"""
import os
import sys
import numpy as np

class Channel(object):
    """Channel object for GALFACTS transient search"""
    def __init__(self, chan_num, beam_num, **options):
        """Initialize the channel object"""
        if options["format"] == "ascii":
           #Added band0/run1/ to fit calgary's file structure
           self.chan_file = "{0}/{1}/band0/run1/{2}/beam{3}/fluxtime{4:04d}.dat".\
             format(options["data_filepath"],
                    options["field"],
                    options["date"],
                    beam_num,
                    chan_num)
           self.error = (not os.path.isfile(self.chan_file))
           k=0
           try: #handles missing channels
               ra,dec,ast,I,Q,U,V = np.loadtxt(self.chan_file,unpack=True)
               self.num_points = len(ra)
           except IOError:
               if options["verbose"] == True:
                   print "Log: fluxtime{0}.dat not found".\
                         format(chan_num)
                   
    def average(self):
        """Return the average Stokes for this channel"""
        ra,dec,ast,I,Q,U,V = np.loadtxt(self.chan_file,unpack=True)
        self.num_points = len(ra)
        return (np.mean(I), np.mean(Q), np.mean(U), np.mean(V))

    def add_points(self, Iarr, Qarr, Uarr, Varr):
        """Add these channel's points to the running I, Q, U, V total
           for each timestamp"""
        ra,dec,ast,I,Q,U,V = np.loadtxt(self.chan_file,unpack=True)
        return (Iarr + I, Qarr + Q, Uarr + U, Varr + V)

    def get_coordinates(self):
        """Get the AST, RA, and DEC for this channel"""
        ra,dec,ast,I,Q,U,V = np.loadtxt(self.chan_file,unpack=True)
        return ra, dec, ast

if __name__ == "__main__":
    sys.exit("Error: module not meant to be run at top level.")
