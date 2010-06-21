#
# Makefile for building the Extended Unix Tools executables
#
# Requires:
# 	* MinGW in the path (rm, cp, make etc.)
#	* Python 2.5 with py2exe installed
#
# Author: Horea Haitonic
#
RM = rm -f
CP = cp
MV = mv
ZIP = zip

SRC = globx.py lsx.py rmx.py

dist_single: $(SRC)
	python setup.py py2exe

.PHONY: clean
clean:
	$(RM) $(SRC:%.py=%.pyc)
	$(RM) -r build dist

