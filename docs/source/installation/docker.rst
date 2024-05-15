Using DRIVE with Docker
=======================
DRIVE now has a working docker image as of v2.7.1. This image is available on DockerHub and can be pulled with the following command:

.. code::

    docker pull jtb114/drive

If you are working on an HPC cluster it may be better to use a singularity image. Singularity can pull the docker container and build a singularity image with the following command:

.. code::

    singularity pull singularity-image-name.sif docker://jtb114/drive:latest
