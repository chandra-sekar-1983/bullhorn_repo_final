#!/usr/bin/python

import socket
import sys
import time

host = sys.argv[1]
port = int(sys.argv[2])
MAX_RETRY = 20
retry = 0

while True:
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  result = sock.connect_ex((host, port))
  if result == 0:
      print(f"{host}:{port} is open! Bye!")
      break
  else:
      print(f"{host}:{port} is not open! I'll check it soon!")
      time.sleep(3)

  retry += 1
