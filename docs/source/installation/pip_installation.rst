Installing DRIVE using Pip
==========================

DRIVE has been officially released on `PYPI <https://pypi.org/project/drive-ibd/>`_! This installation method is recommended for those who wish to use the software without any internal modification. PIP will install all of the necessary dependencies of DRIVE so that the user doesn't have to worry about dependency management. 

.. important:: 

   DRIVE supports Python version >=3.9 and not 3.11.0 (other versions of 3.11 work fine) for compatibility between packages. It is expected that your python version falls within this range when attempting to install the software. You can read more about this version requirement and how to check if you have the right python version :doc:`here </faq>` under the dropdown section 'What versions of Python is DRIVE compatible with?'


DRIVE can be installed using the following command:

.. code::

    pip install drive-ibd


If the install is successful, then you can run the following command and you should see a help message:

.. code::

    drive --help

.. note::

    The recommend way to install DRIVE using pip would be to either create a virtual environment using `Anaconda <https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html>`_ or `venv <https://docs.python.org/3/library/venv.html>`_. Once you activate the virtual environment then you can use the above pip command to install DRIVE into an isolated environment.


