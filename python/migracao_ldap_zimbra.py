#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ldap
import sys
import re

####################
# Server Variables #
####################

server = '150.164.42.10'
domainName = 'dees.ufmg.br'
retrieveAttributes = None

bindrootdn = "cn=Directory Manager"
bindrootpw = "8231502!"

scriptName = 'scriptZimbra.sh'

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

	def write(self, message):
		self.terminal.write(message)
		self.log.write(message)
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
sys.stdout = Logger()

# Regular expression to validate users from LDAP results
validUserRW = re.compile ('^(\w|[@.$-]){5,31}?[$]$')

# Open ldap connection

ldapQuery = ldapSearch(server, bindrootdn, bindrootpw, domainName)

#################################################################################
# First process group names.                                                    #
# Queue all user gidNumbers from LDAP and get group name from servers users[i][1]'s. #
#################################################################################

groups = {}

groupSearchFilter='(&(objectclass=groupOfUniqueNames)(gidNumber=*)(cn=*))'

for data in ldapQuery.search(groupSearchFilter, ['gidNumber', 'cn']):
	groups[int(data[1]['gidNumber'][0])] = data[1]['cn'][0]


##########################
# Now user processing... #
##########################

users = {}

userSearchFilter = "(sambaAcctFlags=[U*])"

for data in ldapQuery.search(userSearchFilter, ['uid', 'userPassword', 'gidNumber']):
	try:
		# Format: users['username'] = ('username', 'passwdhash', 'gidNumber')
		users[data[1]['uid'][0]] = (data[1]['uid'][0], data[1]['userPassword'][0], data[1]['gidNumber'][0])
	except KeyError:
		pass

for i in users:
	print 'Usuario %s' % users[i][0]

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

		# Print the result on screen...
		print ("zmprov ca %s@dees.ufmg.br temppasswordQAZXSW displayName %s" % (users[i][0], users[i][0]))
		# TODO: Make Windows domain operations HERE!
		print ("zmprov ma %s@dees.ufmg.br userPassword '%s'" % (users[i][0], users[i][1]))
		
		# ... And append the output of command line to create the user with password within the database.
		createScript.append ("zmprov ca %s@dees.ufmg.br temppasswordQAZXSW displayName %s" % (users[i][0], users[i][0]))
		createScript.append ("zmprov ma %s@dees.ufmg.br userPassword '%s'" % (users[i][0], users[i][1]))
		print ("\n")
	except SenhaInvalida, error: # Parses Invalid Password
		print "Erro ao incluir senha: %s. Pulando...\n" % (error.erro)
	except UsuarioInvalido, error: # Parses Invalid User
		print "Erro ao incluir usuario: %s. Pulando...\n" % (error.erro)

createScript.__del__() # Delete and close script files
sys.stdout.__del__() # Delete and close log files
