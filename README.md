![Open Colibri](http://i40.tinypic.com/sfhufa.png)
===========
Open Colibri is a free and open source community-driven data portal software.
It was developed by the Decision Support Systems Laboratory (http://www.epu.ntua.gr) for the research data infrastructure project ENGAGE FP7(http://www.engagedata.eu).

Updated: 13/05/2013

colibri Portal - Mac OS.X Installation Instructions for localhost development environment
******************************************************************************
The installation process has been tested under Mac OS X 10.8.3 (Mountain Lion)
+*****************************************************************************

1.	First of all make sure you run a Python 2.7.x version by running "python --version". f you have a previous version or a version >2.7.x, then go and install Python 2.7 (Python is available at http://www.python.org/download/releases/2.7/
2.	Download GIT from http://git-scm.com/download/mac
3.	If you don't have Xcode installed, download and install it from Mac App Store
4.	Open Xcode and then go to Preferences and install the "Command Line Tools" so that the gcc compiler is installed
5.	Open a terminal window, run "sudo easy_install pip" to install the pip installer.
6.	Clone the colibri git repository to a directory of your likings and browse to this directory from the terminal window.
7.	Once you are in the colibri directory, run "sudo pip install -r requirements.txt" in order to get all dependencies downloaded.
8.	To sync the DB, run "python manage.py syncdb" followed by "python manage.py migrate --fake"
9.	At the end run "python manage.py runserver" to bring up the local server and with a browser go to http://127.0.0.1:8000 to view the colibri portal


Periodically, as new modules are added to the git repo of colibri, you should run steps 7-8 in order to download these new additions.



colibri Portal - MS Windows Installation Instructions for localhost development environment
*************************************************************
The installation process has been tested under Windows XP 32
*************************************************************

1.	Download and install GIT from http://git-scm.com/download/win . Choose the second option so that GIT is added to your PATH.
2.	Download and install Python 2.7.x from http://www.python.org/download/releases/2.7/
3.	Add C:\Python27\;C:\Python27\Scripts; to you PATH and REBOOT
4.	Download and install the SetupTools for PY 2.7 from https://pypi.python.org/pypi/setuptools#downloads
5.	Download the last PIP version from http://pypi.python.org/pypi/pip#downloads . Uncompress it and then copy the uncompressed pip folder content into C:\Python27\folder (don't copy the whole folder into it, just the content), because the python command doesn't work outside C:\Python2x folder and then run "python setup.py install"
6.	Download and install PIL from http://www.pythonware.com/products/pil/
7.	Download and install Psycopg2-v2.4.6 from http://www.stickpeople.com/projects/python/win-psycopg/
8.	Download and install VC++2008 Express from http://www.google.com/url?sa=t&rct=j&q=visual%20c++%202008%20express&source=web&cd=1&cad=rja&ved=0CDEQFjAA&url=http://go.microsoft.com/?linkid=7729279&ei=tCgzUbKBHeqS4AS6-IAg&usg=AFQjCNEulTGchEeozkLGRH8LZELiTKlC5A&bvm=bv.43148975,d.bGE (note: this step is needed because you have to have the same compiler which was used for PIL etc).
9.	Enter /colibri from your command prompt and run "pip install -r requirements.txt". The installation should finish without problems.
10.	Copy the "application.id" file that is accompanying this guidelines to your "/colibri/configs" folder\
11.	In the /colibri folder run "python manage.py runserver"
12.	Open up your browser and visit http://127.0.0.1:8000/


Periodically, as new modules are added to the git repo of colibri, you should run step 9 in order to download these new additions.


