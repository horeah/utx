1. Introduction
---------------
utx is a package of command line tools for Windows, meant as an improvement over
the standard Windows command line tools (copy, del, move, xcopy) and the MinGW
ports of the UNIX tools (ls, cp, rm).


2. Features
-----------
 - Recursive wildcards (ant-style)
 - Exclude files based on pattern
 - Progress report for individual files
 - Selectable level of interactivity (0..3)
 - Customizable behavior when no file matches
 - Verbose flag


3. Missing features
-------------------
 - Confirm file overwriting, read-only files etc.
 - Force mode
 - Colors


4. Download/build/installation
------------------------
 a. Download the binary distribution (created with pyinstaller) from:
          https://github.com/horeah/utx/releases
    No installation is necessary.

 b. Fetch the Python sources from the repository at
           https://github.com/horeah/utx.git
    Run 'make' to create the standalone executables.
    You will need:
        - Python 3.10+
        - pyinstaller
        - MinGW


---------------------------------------------------
Horea Haitonic (h o r e a h _at_ g m a i l . c o m)
