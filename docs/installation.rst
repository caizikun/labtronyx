Installation
============

Windows
-------

Installing Python
^^^^^^^^^^^^^^^^^

1. Download the latest version of Python 2.7 from the
   `official Python website <http://python.org>`_ . The Python installer for
   Windows is an MSI package. 

2. To run the installer, double-click on the downloaded file.

   .. image:: media/install_win_step1.png
      :width: 500px

3. Check the option for `Install for all users` and click `Next`.

4. Select a destination directory to install Python. The default location at 
   `C:\\Python27\\` is sufficient. Click `Next`.

   .. image:: media/install_win_step2.png
      :width: 500px

5. Install all features by clicking on the icon next to **Python** and selecting
   **Entire feature will be installed on the local hard drive**. Click `Next`.

6. Wait while the installer finished. You may be prompted by Windows UAC to
   allow the installer Administrator access. Click `Yes` to this prompt.

Additional instructions and help can be found at http://python.org

Installing Labtronyx
^^^^^^^^^^^^^^^^^^^^

For Windows computers, Labtronyx is installed by running the setup file included in the downloaded zip archive.

Mac OSX
-------

Installing Python
^^^^^^^^^^^^^^^^^

1. Download the latest version of Python 2.7 from the
   `official Python website <http://python.org>`_ . The Python installer for
   Mac is a .pkg file. 

2. To run the installer, double-click on the downloaded file.

   .. image:: media/install_mac_step1.png
      :width: 500px

3. The Python installer windows will appear. Click `Continue`.

4. Read the information and warnings, then click `Continue`. 

5. Accept the licensing agreement by clicking `Continue` and then `Agree`.

   .. image:: media/install_mac_step2.png
      :width: 500px

6. Select a destination to install Python, then click `Continue`

7. Click `Install`. You will be prompted to enter your password.

Installing Labtronyx
^^^^^^^^^^^^^^^^^^^^

1. Unzip the archive file.

2. Open a terminal window and browse to the location of the extracted files.

3. Execute the following command:

.. code-block:: console

   python setup.py install

Ubuntu Linux
------------

Python is included with Ubuntu Linux. To install manually, open a terminal
window and execute the following:

.. code-block:: console

   sudo apt-get install python

Installing Labtronyx
^^^^^^^^^^^^^^^^^^^^

Labtronyx is installed using Python setuptools:

1. Open a terminal window and browse to the location of the zip archive.

2. Take note of the filename of the zip archive

3. Execute the following commands

.. code-block:: console

   unzip <filename of zip archive>
   python setup.py install

Installing Dependencies
-----------------------

NI-VISA
^^^^^^^

The latest version of NI-VISA can be downloaded at 
`www.ni.com/visa <http://www.ni.com/visa>`_ . At the time of writing, the latest
version of NI-VISA was `14.0.2 <http://www.ni.com/download/ni-visa-14.0.2/5075/en/>`_ .

Install NI-VISA using the instructions and ReadMe file included with the
installer. NI-VISA is compatible with Windows, Mac and Linux.

Numpy
^^^^^

Numpy is a mathematics library for Python that provides optimized math functions used
by many of the drivers in Labtronyx. Numpy is normally installed with the Labtronyx
setup, but on Windows, it may be necessary to download and install the pre-compiled
binary distribution.

1. Download the Numpy windows superpack distribution for your version of Python from
   the Numpy SourceForge page `here <http://sourceforge.net/projects/numpy/>`_.

   e.g. numpy-1.9.2-win32-superpack-python2.7.exe

2. Install the superpack

Python Libraries
^^^^^^^^^^^^^^^^

Labtronyx requires a number of libraries in order to function properly:

   * PyVISA
   * PySerial
   * Numpy

These libraries should be installed automatically when Labtronyx is installed.
If an error occurs during startup of the Labtronyx application, you can install 
these libraries by opening a terminal window (`Command Prompt` in Windows) and 
typing:

.. code-block:: console

   pip install pyvisa
   pip install pyserial
   pip install numpy