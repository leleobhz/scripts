#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2009 by Leonardo Amaral <contato@leonardoamaral.com.br>
#
# GNU General Public License (GPL)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

import imaplib
from offlineimap import imapserver, repository, folder, mbnames, threadutil, version, syncmaster, accounts
from offlineimap.localeval import LocalEval
from offlineimap.threadutil import InstanceLimitedThread, ExitNotifyThread
from offlineimap.ui import UIBase
import re, os, os.path, offlineimap, sys, ldap
from offlineimap.CustomConfig import CustomConfigParser
from threading import *
from shutil import rmtree
import threading, socket
import signal
import tempfile
import paramiko

####################
# Server Variables #
####################

server = '150.164.42.10'
domainName = 'dees.ufmg.br'
newdomainName = 'zimbra.astolfonet'
newsambadomain = 'ASTOLFONET'
newsambasid = 'S-1-5-21-3538384966-1849037480-1431206198'
retrieveAttributes = None

bindrootdn = "cn=Directory Manager"
bindrootpw = "8231502!"

scriptName = 'scriptZimbra.sh'

srcimapadmmask = '*zimbra'
srcimapadmpass = '!321phj!'

newserveraddr = '192.168.1.3'
# Zimbra private user ssh key - w/o pass
newserversshkey = 'zimbra_key'

#########################
# Functions and classes #
#########################

class SenhaInvalida(Exception):
	'''Invalid password exception class

	Receives one argument. 0 indicates empty password, 1 indicated MD5 password and 2 indicates invalid hash.'''
	def __init__(self, type):
		Exception.__init__(self)
		if type == 0:
			self.erro = "Senha vazia"
		if type == 1:
			self.erro = "Senha em MD5"
		if type == 2:
			self.erro = "Senha com HASH invalido"

class UsuarioInvalido(Exception):
	'''Invalid user exception class

	Receives one argument. 0 indicates a Samba machine account.'''
	def __init__(self, tipo):
		Exception.__init__(self)
		if tipo == 0:
			self.erro = "Usuário é uma máquina do domínio."

class Logger(object):
	'''Class to duplicate input between logfile and stdout.'''
	def __init__(self):
		self.terminal = sys.stdout
		self.log = open("log.txt", "a")
	def isatty(self):
		return False
	def write(self, message):
		self.terminal.write(message)
		self.log.write(message)
	def flush(self):
		self.terminal.flush()
		self.log.flush()
	def __del__(self):
		self.log.close()

class createScripts:
	'''Attempts to create Zimbra scripts'''
	def __init__(self, scriptName):
		self.script = open(scriptName, 'w')
		self.script.write ('#!/bin/bash\n\n')
	def append(self, line):
		self.script.write (line + '\n')
	def __del__(self):
		self.script.close()

class ldapSearch:
	'''Instances ldap searches'''

	def domainToDC (self, domain):
		# Thanks to http://www.skymind.com/~ocrow/python_string/ and http://amix.dk/blog/viewEntry/19291
		#return ''.join([ ('dc=%s' % string if not ',' in string else string) for string in re.split ('(,)', re.sub('[.]', ',', domain))])
		# Thanks to nosklo@freenode
		return ','.join('dc=' + x for x in domain.split('.'))

	def __init__(self, server, bindrootdn, bindrootpw, domain):
		# Open connection
		try:
			self.con = ldap.initialize("ldap://" + server)
		except ldap.LDAPError, e:
			print ("Connection error: %s" % (e[0]['desc']))
			sys.exit(1)
		# Attempt to bind with simple bind autentication
		try:
			self.con.simple_bind_s(bindrootdn, bindrootpw)
		except ldap.LDAPError, e:
			print ("Authentication error: %s" % (e[0]['desc']))
			sys.exit(1)
		self.domain = self.domainToDC(domain)
	
	def search(self, filter, attrib):
		# Try make the search.
		try:
			return self.con.search_s(self.domain, ldap.SCOPE_SUBTREE, filter, attrib)
		except ldap.LDAPError, e:
			print ("Search error: %s" % (e[0]['desc']))
			sys.exit(1)

class OfflineImapWrapper():

	def __init__(self, srcusername, srcpasswd, dstusername, dstpasswd):

		try:
			import fcntl
			hasfcntl = 1
		except:
			hasfcntl = 0
	
		lockfd = None

		def lock(config, ui):
			if not hasfcntl:
				return
			lockfd = open(self.configuration.getmetadatadir() + "/lock", "w")
			try:
				fcntl.flock(lockfd, fcntl.LOCK_EX | fcntl.LOCK_NB)
			except IOError:
				ui.locked()
				ui.terminate(1)

		self.configuration = CustomConfigParser()
		
		self.configuration.add_section('general')
		self.configuration.set('general','accounts', dstusername)
		self.configuration.add_section('Account ' + dstusername)

		self.configuration.set('Account ' + dstusername, 'localrepository', dstusername+'_local')
		self.configuration.set('Account ' + dstusername, 'remoterepository', dstusername+'_remote')
		
		self.configuration.add_section('Repository ' + dstusername + '_local')
		self.configuration.add_section('Repository ' + dstusername + '_remote')

		self.configuration.set('Repository ' + dstusername + '_local', 'type', 'IMAP')
		self.configuration.set('Repository ' + dstusername + '_local', 'remotehost', newserveraddr)
		self.configuration.set('Repository ' + dstusername + '_local', 'remoteuser', dstusername)
		self.configuration.set('Repository ' + dstusername + '_local', 'remotepass', dstpasswd)

		self.configuration.set('Repository ' + dstusername + '_remote', 'type', 'IMAP')
		self.configuration.set('Repository ' + dstusername + '_remote', 'remotehost', server)
		self.configuration.set('Repository ' + dstusername + '_remote', 'remoteuser', srcusername)
		self.configuration.set('Repository ' + dstusername + '_remote', 'remotepass', srcpasswd)
		
		self.monothread = 0
		# Setup a interface

		ui = offlineimap.ui.detector.findUI(self.configuration, 'TTY.TTYUI')
		UIBase.setglobalui(ui)
#		ui.add_debug('imap')
#		ui.add_debug('thread')
#		imaplib.Debug = 5
#		threading._VERBOSE = 1

		lock(self.configuration, ui)
	
		def sigterm_handler(signum, frame):
			# die immediately
			ui.terminate(errormsg="terminating...")
		signal.signal(signal.SIGTERM,sigterm_handler)

		try:
			pidfd = open(config.getmetadatadir() + "/pid", "w")
			pidfd.write(str(os.getpid()) + "\n")
			pidfd.close()
		except:
			pass
		
		try:
			activeaccounts = self.configuration.get("general", "accounts")
			activeaccounts = activeaccounts.replace(" ", "")
			activeaccounts = activeaccounts.split(",")
			allaccounts = accounts.AccountHashGenerator(self.configuration)

			if self.monothread:
				threadutil.initInstanceLimit("ACCOUNTLIMIT", 1)
			else:
				threadutil.initInstanceLimit("ACCOUNTLIMIT", self.configuration.getdefaultint("general", "maxsyncaccounts", 1))

			for reposname in self.configuration.getsectionlist('Repository'):
				for instancename in ["FOLDER_" + reposname, "MSGCOPY_" + reposname]:
					if self.monothread:
						threadutil.initInstanceLimit(instancename, 1)
					else:
						threadutil.initInstanceLimit(instancename, self.configuration.getdefaultint('Repository ' + reposname, "maxconnections", 1))
	
			syncaccounts = []
			for account in activeaccounts:
				if account not in syncaccounts:
					syncaccounts.append(account)
	
			siglisteners = []
			def sig_handler(signum, frame):
				if signum == signal.SIGUSR1:
					# tell each account to do a full sync asap
					signum = (1,)
				elif signum == signal.SIGHUP:
					# tell each account to die asap
					signum = (2,)
				elif signum == signal.SIGUSR2:
					# tell each account to do a full sync asap, then die
					signum = (1, 2)
				# one listener per account thread (up to maxsyncaccounts)
				for listener in siglisteners:
					for sig in signum:
						listener.put_nowait(sig)
			signal.signal(signal.SIGHUP,sig_handler)
			signal.signal(signal.SIGUSR1,sig_handler)
			signal.signal(signal.SIGUSR2,sig_handler)
	
			threadutil.initexitnotify()
			t = ExitNotifyThread(target=syncmaster.syncitall,
						name='Sync Runner',
						kwargs = {'accounts': syncaccounts,
						'config': self.configuration,
						'siglisteners': siglisteners})
			t.setDaemon(1)
			t.start()
		
		except:
			ui.mainException()

		try:
			threadutil.exitnotifymonitorloop(threadutil.threadexited)
		except SystemExit:
			raise
		except:
			ui.mainException()				  # Also expected to terminate.

		rmtree(self.configuration.getmetadatadir())

##############
# Code Begin #
##############

# Test if "any" statement exists. For Python 2.5<

try:
	any
except NameError:
	def any(iteravel):
		for item in iteravel:
			if item:
				return True
 
# Initialize script file
createScript = createScripts(scriptName)

# Redirect output to Logger funcion
#sys.stdout = Logger()

# Regular expression to validate users from LDAP results
validUserRW = re.compile ('^(\w|[@.$-]){5,31}?[$]$')

# Open ldap connection

ldapQuery = ldapSearch(server, bindrootdn, bindrootpw, domainName)

# Instancing SSH Connection

remoteshell = paramiko.SSHClient()
try:
	remoteshell.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	remoteshell.connect(newserveraddr, username='zimbra', key_filename=newserversshkey)
except paramiko.PasswordRequiredException:
	print 'Senha de chave ainda não suportada'
	sys.exit(1)

###########################################################################
# First process group names.                                              #
# Queue all user gidNumbers from LDAP and get group name from ldap server #
###########################################################################

groups = {}
groupSearchFilter='(&(&(gidNumber=*)(cn=*))(|(|(objectClass=groupOfUniqueNames)(objectClass=posixGroup))(objectClass=sambaGroupMapping)))'

for data in ldapQuery.search(groupSearchFilter, ['gidNumber', 'cn']):
	groups[int(data[1]['gidNumber'][0])] = data[1]['cn'][0]

##########################
# Now user processing... #
##########################

users = {}
userSearchFilter = "(&(&(&(&(&(sambaAcctFlags=[U*])(gidNumber=*))(cn=*))(uidNumber=*))(userPassword=*))(uid=*))"

for data in ldapQuery.search(userSearchFilter, ['uid', 'userPassword', 'gidNumber', 'uidNumber']):
	# Format: users['username'] = ('username', 'passwdhash', 'gidNumber', 'uidNumber')
	users[data[1]['uid'][0]] = (data[1]['uid'][0], data[1]['userPassword'][0], int(data[1]['gidNumber'][0]), int(data[1]['uidNumber'][0]))

for i in users:
	print 'Usuario %s, Grupo %s (%s)' % (users[i][0], groups[users[i][2]], users[i][2])

	try:
#		validUser = re.search ('^[^$]+$ | ^[a-zA-Z][@_\\-\\.\\$\\w]{5,31}$', uid) # Implemented by validUserRW. *DEPRECATED*
		validUser = validUserRW.match (users[i][0])
		if validUser:
			raise UsuarioInvalido(0)
		try:
			users[i][1] = users[i][1]
			print "userPassword Shadow: %s" % (users[i][1])
		except:
			pass
		# Block to check if password is a encrypted password or not. Currently we work only with chypered passwords
		if "{crypt}!!" in users[i][1].lower() or "{crypt}*" in users[i][1].lower() or users[i][1] == None:
			raise SenhaInvalida(0)
		if not any ( users[i][1].lower().startswith(s) for s in ["{crypt}$", '{md5}', '{ssha}']):
			raise SenhaInvalida(2)
		try:

			# Now is the time to run everything
			try:
				stdin, stdout, stderr = remoteshell.exec_command ("zmprov ca %s@%s temppasswordQAZXSW displayName %s objectClass sambaSamAccount objectClass posixAccount uidNumber %s gidNumber %s homeDirectory /home/users/%s/%s loginShell /bin/false sambaSID %s sambaDomainName %s sambaAcctFlags [UX]" % (users[i][0], newdomainName, users[i][0], users[i][3], users[i][2], groups[users[i][2]], users[i][0], newsambasid, newsambadomain ))
				print stderr.read()
				print stdout.read()
			except paramiko.SSHException:
				print 'Impossível executar zmprov em host remoto. Abortando'
				sys.exit(1)
			OfflineImapWrapper(users[i][0] + srcimapadmmask, srcimapadmpass, users[i][0], 'temppasswordQAZXSW')
			try:
				stdin, stdout, stderr = remoteshell.exec_command ("zmprov ma %s@%s userPassword '%s'" % (users[i][0], newdomainName, users[i][1]))
			except paramiko.SSHException:
				print 'Impossível executar zmprov em host remoto. Abortando'
				sys.exit(1)

		except KeyError, err:
			print 'GID %s vinculado a usuário, porém não registrado no LDAP. Conferir /etc/shadow ou outro mecanismo em conjunto. Pulando usuário...' % err
		print ("\n")
	except SenhaInvalida, error: # Parses Invalid Password
		print "Erro ao incluir senha: %s. Pulando...\n" % (error.erro)
	except UsuarioInvalido, error: # Parses Invalid User
		print "Erro ao incluir usuario: %s. Pulando...\n" % (error.erro)

createScript.__del__() # Delete and close script files
sys.stdout.__del__() # Delete and close log files


