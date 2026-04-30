Using DRIVE with Docker
=======================
DRIVE is available in a container on DockerHub. This image was built for linux/arm64 and linux/amd64. If users need to run DRIVE on a Windows machine then the user will have to use a different method than Docker (it is recommended to use PIP to install into a virtual environment for these individuals). The image can be pulled from DockerHub with the following command:

.. code::

    docker pull jtb114/drive

If you are working on an HPC cluster it may be better to use a singularity image. Singularity can pull the docker container and build a singularity image with the following command:

.. code::

    singularity pull singularity-image-name.sif docker://jtb114/drive:latest
