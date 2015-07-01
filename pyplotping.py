##pyplotping.py
##python ping data RTT plotting to learn matplotlib
##Usage: python pyplotping.py infile
##Thanks for peakdet() go to Eli Billauer

import matplotlib.pyplot as plt
import numpy as np
import sys
import re
import argparse



parser = argparse.ArgumentParser(description = 'pyplotping.py - Makes a pretty set of graphs from standard ping output.')

parser.add_argument('--input', '-i', dest = "infile", action = "store", help = 'The file from which to read the ping data. Should contain data from exactly one ping run.')

if len(sys.argv)==1:
    parser.print_help()
    sys.exit(1)

arguments = parser.parse_args()

HOST_REGEX = "(PING .* \(?([0-9]{1,3}\.){3}([0-9]{1,3})\))?"
ADDR_REGEX = "([0-9]{1,3}\.){3}([0-9]{1,3})"
DATA_REGEX = "([0-9]{1,3} byte(s)?)"
RTT_REGEX = "(time=[0-9][0-9](\.)?[0-9])"
 
def peakdet(v, delta, x = None):
    """
    Converted from MATLAB script at http://billauer.co.il/peakdet.html
    
    Returns two arrays
    
    function [maxtab, mintab]=peakdet(v, delta, x)
    %PEAKDET Detect peaks in a vector
    %        [MAXTAB, MINTAB] = PEAKDET(V, DELTA) finds the local
    %        maxima and minima ("peaks") in the vector V.
    %        MAXTAB and MINTAB consists of two columns. Column 1
    %        contains indices in V, and column 2 the found values.
    %      
    %        With [MAXTAB, MINTAB] = PEAKDET(V, DELTA, X) the indices
    %        in MAXTAB and MINTAB are replaced with the corresponding
    %        X-values.
    %
    %        A point is considered a maximum peak if it has the maximal
    %        value, and was preceded (to the left) by a value lower by
    %        DELTA.
    
    % Eli Billauer, 3.4.05 (Explicitly not copyrighted).
    % This function is released to the public domain; Any use is allowed.
    
    """
    from numpy import NaN, Inf, arange, isscalar, asarray, array
    maxtab = []
    mintab = []
       
    if x is None:
        x = arange(len(v))
    
    v = asarray(v)
    
    if len(v) != len(x):
        sys.exit('Input vectors v and x must have same length')
    
    if not isscalar(delta):
        sys.exit('Input argument delta must be a scalar')
    
    if delta <= 0:
        sys.exit('Input argument delta must be positive')
    
    mn, mx = Inf, -Inf
    mnpos, mxpos = NaN, NaN
    
    lookformax = True
    
    for i in arange(len(v)):
        this = v[i]
        if this > mx:
            mx = this
            mxpos = x[i]
        if this < mn:
            mn = this
            mnpos = x[i]
        
        if lookformax:
            if this < mx-delta:
                maxtab.append((mxpos, mx))
                mn = this
                mnpos = x[i]
                lookformax = False
        else:
            if this > mn+delta:
                mintab.append((mnpos, mn))
                mx = this
                mxpos = x[i]
                lookformax = True
 
    return array(maxtab), array(mintab)

def build_graph_for_ping_file(filepath):
  """
  Builds a graph for RTT and TTL from a file output from ping. Currently supports only one host per file.
  """
  content = open(filepath, 'r').read() #Grab the file
  rtt_list = []
  #Now find out which host we were pinging
  hostline = re.search(HOST_REGEX, content).group()
  hostlineparts = hostline.split()
  host = hostlineparts[1] #Would be, for example, google.com
  hostaddr = re.search(ADDR_REGEX, hostlineparts[2]).group() #Would be, for example, 216.58.216.46
  print("File is for " + host + " a.k.a " + hostaddr + ". Parsing in data.")
  index = 0
  for line in content.splitlines():
    #Go through each line. If it is a valid line (starts with nn(n)? byte(s)?) then parse it for data, else see if it's the end and quit, else skip it and warn.
    if re.search(DATA_REGEX, line):
      index += 1
      #The line contains the correct magic, so parse
      print("Index: " + str(index) + " for line \n" + line)
      rttblob = re.search(RTT_REGEX, line).group()
      rtt = float(rttblob.split('=')[1])
      rtt_list.append(rtt)
  
  #Generate our graphs - Round Trip Time first
  plt.figure(1)
  plt.title("Ping times to " + host + " (" + hostaddr + "), " + str(index) + " samples.")
  plt.ylim(0, 120) #Set Y limits
  plt.xlim(0,index)    
  plt.ylabel("Round Trip Time (ms)")
  plt.xlabel("ICMP Sequence Number")
  plt.grid(True)
  plt.plot(np.array([n for n in range (index)]), np.array(rtt_list), linestyle = '-', marker = '', color = 'r')
  #Now, find minima and maxima
  rtt_maxima, rtt_minima = peakdet(np.array(rtt_list), 1)
  rtt_maxima_xpos = []
  rtt_maxima_ypos = []
  rtt_minima_xpos = []
  rtt_minima_ypos = []
  for (x,y) in rtt_maxima: #Cycle through the maxima, seperating them into two lists, x and y
    rtt_maxima_xpos.append(x)
    rtt_maxima_ypos.append(y)
  for (x,y) in rtt_minima: #Cycle through the minima, seperating them into two lists, x and y
    rtt_minima_xpos.append(x)
    rtt_minima_ypos.append(y)
  plt.plot(rtt_maxima_xpos, rtt_maxima_ypos, marker = '.', linestyle = '', color = 'g')
  plt.plot(rtt_minima_xpos, rtt_minima_ypos, marker = '.', linestyle = '', color = 'b')
  plt.show()
  
  
#end build_graph_for_ping_file()

build_graph_for_ping_file(arguments.infile)
