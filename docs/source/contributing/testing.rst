Testing (For Contributors only)
===============================

DRIVE uses the `Pytest framework <https://docs.pytest.org/en/stable/index.html#>`_ to ensure that code is maintaining backwards compatibility and performing as expected. Currently, only integration tests have been created. These tests are automatically run using GitHub actions when a proposed change is pushed to GitHub so anyone contributing doesn't have to feel compelled to run the tests before any pushes (although it is probably a good idea to run the tests locally). Since PDM is the required framework for anyone contributing, this section will only cover how to run the tests using PDM

Running Tests:
--------------
The following commands for running tests assume that you are running them from the DRIVE parent directory after cloning the repository and that you used "pdm install" to install all runtime dependencies. The following command will use PDM to run all the tests

.. code::

   pdm run pytest -v test/test_integration.py


Adding Tests:
-------------

DRIVE is not fully covered by unit tests so a very helpful way to contribute would be to add unit tests. All we ask is that you use the pytest mark "unit" if you are adding a unit test or "integtest" if you are adding an integration test. The following section of the Pytest documentation can explain this process in more detail: `How to create tests <https://docs.pytest.org/en/stable/getting-started.html>`_.


