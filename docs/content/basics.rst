About
=====

Sugar Server combines `Sugar ODM <https://sugar-odm.docs.sugarush.io>`_,
`Sugar API <https://sugar-api.docs.sugarush.io>`_ and
`Sanic <https://github.com/huge-success/sanic>`_ into a fast, asynchronous
API building environment.

Installation
------------

This git repository is a template to be cloned, modified and reused.

``git clone https://github.com/sugarush/sugar-server.git api-server``

Change directories to the cloned repository.

``cd api-server``

Next, install all dependencies.

``pip install -r .requirements``

Now we need to uninstall `ujson`.

``pip uninstall ujson``

Usage
-----

To run the server, make sure you are in the cloned repository and run:

``python server``
