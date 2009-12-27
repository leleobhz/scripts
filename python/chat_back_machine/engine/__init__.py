#!/usr/bin/env python
import sys
import os
import stat

from xml.etree.ElementTree import parse
from datetime import datetime
from PyDbLite import Base

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
            for (newtop, children) in walktree (os.path.join(top, name), 
                                                depthfirst):
                yield newtop, children
    if depthfirst:
       yield top, names


class kopeteLog():
    def __init__(self, directory=os.path.join(os.path.expanduser("~"), 
                        ".kde/share/apps/kopete/logs")):

        self.messages = Base('kopete.db')  # Database stuff - Initializing...
        self.messages.create('protocol', 'date', 'time', 'msgfrom', 'msgto',  'sender',  'inbound',  'nick',  'message',  mode='override')
        
        for file in self.searchLogs(directory):
            self.feedDatabase(file)
        
    def searchLogs(self,  dir):
        logfiles = []
        for (basepath, children) in walktree(dir):
            for child in children:
                if child.endswith (".xml"):
                    logfiles.append(os.path.join(basepath, child))
        return logfiles
        
    def feedDatabase(self,  file):
        if file.find('WlmProtocol'):
            protocol = 'wlm'
        elif file.find('ICQProtocol'):
            protocol = 'icq'
        elif file.find('JabberProtocol'):
            protocol = 'jabber'
        else:
            protocol = ''
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
            date = datetime.strptime("%s;%s;%s" % 
                                     (year,  month,  msg.attrib['time']) , 
                                     "%Y;%m;%d %H:%M:%S")
            self.messages.insert(
                                 protocol=protocol, 
                                 date=date.strftime("%Y%m%d"), 
                                 time=date.strftime("%H:%M:%S"),  
                                 msgfrom=contactfrom,  msgto=contactto,
                                 sender=sender,  inbound=inbound,  nick=nick,
                                 message=message)
    
    def locate(self):
        return self.messages(date='20091217')
    
if __name__ == "__main__":
    teste = kopeteLog()
    print "%s\n\n" % teste.locate()[0]
    sys.exit(1)
