.. riddler documentation master file, created by
   sphinx-quickstart on Mon Jan 16 12:29:01 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Riddler's documentation!
===================================

This project hold the :ref:`fsm` (Finite State Machine) and the Broker of the Riddler project, it can be considered the Back-end of riddler.

It also serves a very simple dummy [Front-end](riddler/back/riddler/apps/broker/templates/chat/index.html) just as an example of a WS connection to the backend from a custom widget.

Prerequisites
#############

You could either run this project from Docker or install it locally. Depending on your choice you will need different prerequisites.

- :ref:`Docker Prerequisites`
- :ref:`Local Prerequisites`


Installation
############

As mentioned before run this project from Docker or install it locally.

- :ref:`Docker Installation`
- :ref:`Local Installation`

.. toctree::
   :maxdepth: 2
   :caption: Contents:


   modules/prerequisites_docker.rst
   modules/prerequisites_local.rst
   modules/installation_docker.rst
   modules/installation_local.rst
   modules/env_example.rst
   modules/fsm.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
