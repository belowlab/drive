Testing
============

DRIVE uses the `Pytest framework <https://docs.pytest.org/en/stable/index.html#>`_ to ensure that code is maintaining backward's compatibility and performing as expected. Currently, only integration test have been created. These test are automatically run using Github actions when a proposed change is pushed to Github so anyone contributing doesn't have to feel compelled to run the test before any pushes. That being said, if you wish to run the tests you can. You first need to switch directories to the parent drive directory. After that you can use either of the following commands:

.. code::

    pytest -v -m integtest

    or 
    
    pytest -v ./tests/test_integration.py

.. note::
    (Only if you are using the PDM build system) If you receive an error saying that the pytest command is not found or "pytest is not installed" then you need to prefix the above commands with "pdm run" and then they should work.


Adding Tests:
----------------

DRIVE is not fully covered by unit test so a very helpful way to contribute to drive would be to add unit test. All we ask is that you use the pytest mark "unit" if you are adding a unit test or "integtest" if you are adding an integration test. The following section of the Pytest documentation can explain this process in more detail: `How to create tests <https://docs.pytest.org/en/stable/getting-started.html>`_ .


