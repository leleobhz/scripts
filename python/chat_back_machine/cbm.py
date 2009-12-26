#!/usr/bin/env python

import sys
from PyQt4 import uic

if __name__ == "__main__":
    widget = uic.loadUi("main.ui")
    widget.show()
    app.exec_()
