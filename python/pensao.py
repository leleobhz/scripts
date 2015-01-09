#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import print_function
import re, urllib
from bs4 import BeautifulSoup

mte = BeautifulSoup(urllib.urlopen("http://portal.mte.gov.br/sal_min/").read())
smin = float(re.findall(r'\d+(?:[\d,.]*\d)', mte.find_all("p")[2].get_text())[0].replace(',', '.'))
pensao = round(smin * 0.3,2)

print("Salário Mínimo: %.2f" % smin)
print("Pensão a pagar: %.2f" % pensao)
