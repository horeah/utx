#
# Makefile for building the Extended Unix Tools executables
#
# Requires:
# 	* MinGW in the path (rm, cp, make etc.)
#	* zip in the path
#	* Python 2.7 with py2exe installed
#
# Author: Horea Haitonic
#
RM = rm -f
CP = cp
MV = mv
ZIP = zip

SRC = globx.py lsx.py cpx.py rmx.py actions.py console.py util.py

dist_single: $(SRC)
	python setup.py py2exe
	$(RM) utx.zip
	cd dist && $(ZIP) utx.zip lsx.exe cpx.exe rmx.exe

.PHONY: clean
clean:
	$(RM) $(SRC:%.py=%.pyc)
	$(RM) -r build dist

