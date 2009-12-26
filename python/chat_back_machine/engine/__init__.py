#!/usr/bin/env python
import sys,  os,  stat
from xml.etree.ElementTree import parse
from datetime import datetime

def walktree (top = ".", depthfirst = True):
    names = os.listdir(top)
    if not depthfirst:
        yield top, names
    for name in names:
        try:
            st = os.lstat(os.path.join(top, name))
        except os.error:
            continue
        if stat.S_ISDIR(st.st_mode):
            for (newtop, children) in walktree (os.path.join(top, name), depthfirst):
                yield newtop, children
    if depthfirst:
       yield top, names


class kopeteLog():
    masslog = []
    def __init__(self, directory = os.path.join(os.path.expanduser("~"), ".kde/share/apps/kopete/logs")):
        self.requestLogList(directory)
        
    def searchLogs(self,  dir):
        logfiles = []
        for (basepath, children) in walktree(dir):
            for child in children:
                if child[-4:] == ".xml":
                    logfiles.append(os.path.join(basepath, child))
        return logfiles
        
    def requestLogList(self,  directory):
        for file in self.searchLogs(directory):
            print "File: %s" % file
            xmllog = parse(file)
            for head in xmllog.getiterator('head'):
                for date in head.getiterator('date'):
                    month=date.attrib['month']
                    year=date.attrib['year']
                for contact in head.getiterator('contact'):
                    if contact.attrib.has_key('type'):
                        if contact.attrib['type'] == 'myself':
                            contactfrom = contact.attrib['contactId']
                    else:
                        contactto = contact.attrib['contactId']
            for msg in xmllog.getiterator('msg'):
                nick = msg.attrib['nick']
                time = msg.attrib['time']
                inbound = msg.attrib['in']
                message = msg.text
                sender = msg.attrib['from']
                date = datetime.strptime("%s;%s;%s" % (year,  month,  msg.attrib['time']) , "%Y;%m;%d %H:%M:%S")
                self.masslog.append ( {'date' : date.strftime("%Y%m%d"), 'time' : date.strftime("%H:%M:%S"),  'from' : contactfrom,  'to' : contactto,  'sender' : sender,  'inbound' : inbound,  'nick' : nick,  'message' : message} )

if __name__ == "__main__":
    teste = kopeteLog()
    print teste.masslog[30]
    sys.exit(1)
