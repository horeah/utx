#
# Makefile for building the Extended Unix Tools executables
#
# Requires:
# 	* MinGW in the path (rm, cp, make etc.)
#	* zip in the path
#	* Python >= 3.10 with the pyinstaller package
#
# Author: Horea Haitonic
#
RM = rm -f
CP = cp
MV = mv
ZIP = zip

SRC = globx.py lsx.py cpx.py rmx.py actions.py console.py util.py

dist_single: $(SRC)
	$(PYTHONHOME)/scripts/pyinstaller.exe --onefile lsx.py
	$(PYTHONHOME)/scripts/pyinstaller.exe --onefile cpx.py
	$(PYTHONHOME)/scripts/pyinstaller.exe --onefile rmx.py
	cd dist && $(RM) utx.zip && $(ZIP) utx.zip lsx.exe cpx.exe rmx.exe

.PHONY: clean
clean:
	$(RM) $(SRC:%.py=%.pyc)
	$(RM) -r build dist

