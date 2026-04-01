Configuring DRIVE to use the plugins
====================================

After the plugin is created, DRIVE still has to be configured to use the plugin. This configuration is done through a JSON file. This file by default is placed within the source code directory for DRIVE. This file by default looks like this:

.. code:: json

    {
        "plugins":["drive.plugins.pvalues", "drive.plugins.network_writer"],
        "modules": [
            {
                "name":"pvalues"
            },
            {
                "name":"network_writer"
            }
        ]
    }

There are two parts to this JSON file:

* **plugins:** This section lists the path to the file for the plugin. It uses the Python module syntax. This path should start with the DRIVE base module and then the plugin module and then the name of the plugin file. This file name does not need the file extension.

* **modules:** This section consists of a dictionary for each plugin. The dictionary has a key called name and then the value is the name that was given to the plugin in the initialize function.
