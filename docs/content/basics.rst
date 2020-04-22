About
=====

Sugar Server combines `Sugar ODM <https://sugar-odm.docs.sugarush.io>`_,
`Sugar API <https://sugar-api.docs.sugarush.io>`_ and
`Sanic <https://github.com/huge-success/sanic>`_ into a fast, asynchronous
API building environment.

Installation
------------

This git repository is a template to be cloned, modified and reused.

``git clone https://github.com/sugarush/sugar-server.git project``

Change directories to the cloned repository.

``cd project``

Next, install all dependencies.

``pip install -r .requirements``

Now we need to uninstall `ujson`.

``pip uninstall ujson``

Usage
-----

To run the server, make sure you are in the `project` directory and run:

``python server``

After starting the server, you can obtain a `token` by running:

.. code-block:: shell

  curl 'http://localhost:8001/v1/authentication' \
    --request 'POST' \
    --header 'Content-Type: application/vnd.api+json' \
    --header 'Accept: application/vnd.api+json' \
    --data '{ "data": { "attributes": { "username": "administrator", "password": "password" } } }' \

To use the token to get the first 100 users:

.. code-block:: shell

  curl 'http://localhost:8001/v1/users' \
    --request 'GET' \
    --header 'Content-Type: application/vnd.api+json' \
    --header 'Accept: application/vnd.api+json' \
    --header 'Authorization: Bearer <your token>'
