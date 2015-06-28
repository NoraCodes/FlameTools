##pyplotping.py
##python3 ping data RTT plotting to learn matplotlib

import matplotlib.pyplot as plt
import numpy as np
import sys
import re

HOST_REGEX = "(PING .* \(?([0-9]{1,3}\.){3}([0-9]{1,3})\))?"
ADDR_REGEX = "([0-9]{1,3}\.){3}([0-9]{1,3})"
DATA_REGEX = "([0-9]{1,3} byte(s)?)"
RTT_REGEX = "(time=[0-9][0-9]\.[0-9])"
TTL_REGEX = "(ttl=[0-9]{1,})"

def build_graph_for_ping_file(filepath):
  """
  Builds a graph for RTT and TTL from a file output from ping. Currently supports only one host per file.
  """
  content = open(filepath, 'r').read() #Grab the file
  rtt_list = []
  ttl_list = []
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
      rttblob = re.search(RTT_REGEX, line).group()
      rtt = float(rttblob.split('=')[1])
      rtt_list.append(rtt)
  
  plt.title("Ping times to " + host + " (" + hostaddr + ")")
  #plt.ylim(0, 120) #Set Y limits    
  plt.ylabel("Round Trip Time (ms)")
  plt.xlabel("ICMP Sequence Number")
  plt.grid(True)
  plt.plot(np.array([n for n in range (index)]), np.array(rtt_list), linestyle = '-', marker = '', color = 'r')
  plt.show()
  
#end build_graph_for_ping_file()

build_graph_for_ping_file(sys.argv[1])
