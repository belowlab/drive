How is DRIVE extensible
=======================

DRIVE is designed with user extensibility in mind and it accomplishes this through a plugin architecture. This design allows users to dynamically load their own code at runtime (as long as the code conforms to the specified plugin interface). You can read more about this design strategy at this site `Plugin Architecture <https://dotcms.com/blog/post/plugin-achitecture>`_. The only component of DRIVE that can be changed is the clustering algorithm. Everything else, such as the statistics and how the program writes to an output file are completely customizable to the user.

At its core, the cluster subcommand of DRIVE is just a network identification software. Users can then extend this functionality by bringing their own extensions to customize it to fit their needs. That being said, DRIVE offers two plugins out of the box. One plugin uses a binomial test to calculate phenotypic enrichment within each network and the other plugin writes the network information to a file. These plugins are described in more detail in this section:

- :doc:`factory_plugins`

.. note::

    This plugin architecture is only used in the cluster subcommand of DRIVE and not the dendrogram subcommand


