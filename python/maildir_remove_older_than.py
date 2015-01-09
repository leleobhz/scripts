#!/usr/bin/env python2
# -*- coding: UTF-8 -*-

# GPLv3

from __future__ import print_function

class moveMail:
	def __init__(self, oldBoxDir, newBoxDir, daystoremove):
		from sys import stdout
		from mailbox import Maildir,MaildirMessage,NoSuchMailboxError
		from os.path import expanduser
		from time import time, strftime, gmtime


		self.logfile=strftime(expanduser("~/")+"mail-remove-log-%Y%m%d%H%M", gmtime())
		# DeltaT is epoch now - 60(s)*m*d*nm where n is number of months - here set for 4 months
		self.deltaT=int(round(time()-(60*60*24*int(daystoremove)))) 
		self.newBox = Maildir(newBoxDir, create=True, factory=MaildirMessage)

		try: 
			self.oldBox = Maildir(oldBoxDir, create=False, factory=MaildirMessage)
		except NoSuchMailboxError:
			print ("[E] Invalid mail dir. Aborting")
			return(1)

	
	def moveByLabel (self):
		from email.utils import parsedate_tz,mktime_tz
		from mailbox import NoSuchMailboxError

		for folder in self.oldBox.list_folders():
			_c_moved=0
			_c_rej=0
			_c_total=self.oldBox.get_folder(folder).__len__()
			print("\n[I] Folder " + folder + "", end="")
			for key, msg in self.oldBox.get_folder(folder).iteritems():
				_date=msg['Date']
				if _date:
					if (mktime_tz(parsedate_tz(_date)) - self.deltaT) < 0:
						if _c_moved == 0:
							#To detect if no thing is moved, so this can be a new folder
							try:
								self.newBox.get_folder(folder)
							except NoSuchMailboxError:
								print("[I]\tCreating in new: %s" % folder)
								self.newBox.add_folder(folder)
						# Mooooooooooooo'ving!
						self.newBox.get_folder(folder).add(msg)
						self.oldBox.get_folder(folder).remove(key)
						_c_moved += 1
						print("\r[I]\tStats: Not moved (Bad Mail): %d/%d // Moved: %d/%d" % (_c_rej,_c_total,_c_moved,_c_total), end="")
				else:
					_c_rej += 1
			if _c_moved >= _c_total:
				print("\n[W]\tRemoving folder %s" % folder, end="")
		print("")

def main():
	from optparse import OptionParser

	lParser = OptionParser()
	lParser.add_option('-s','--source', help='Source Maildir.', dest='source')
	lParser.add_option('-d','--dest', help='Destination Maildir. Usually a clean folder', dest='dest')
	lParser.add_option('-t','--time', help='Time (In days) to keep emails. Before this time, all mails will be moved', dest='time')

	(options, arguments) = lParser.parse_args()

	# Mandatory options
	for mand in ('source', 'dest', 'time'):
		if not options.__dict__[mand]:
			print("Mandatory option is missing\n")
			lParser.print_help()
			exit(-1)

	boxHandler = moveMail(options.source, options.dest, options.time)
	boxHandler.moveByLabel()
	

if __name__ == "__main__":
	main()
