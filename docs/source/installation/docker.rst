Using DRIVE with Docker
=======================
DRIVE is available in a container on DockerHub. This image was built for Linux/arm64 and Linux/amd64. If users need to run DRIVE on a Windows machine then it is recommended to use pip to install into a virtual environment. The image can be pulled from DockerHub with the following command:

.. code::

    docker pull jtb114/drive

If you are working on an HPC cluster it may be better to use a singularity image. Singularity can pull the docker container and build a singularity image with the following command:

.. code::

    singularity pull singularity-image-name.sif docker://jtb114/drive:latest
