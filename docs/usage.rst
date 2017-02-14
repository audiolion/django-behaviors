=====
Usage
=====

To use Django Behaviors in a project, add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'behaviors.apps.BehaviorsConfig',
        ...
    )

Add Django Behaviors's URL patterns:

.. code-block:: python

    from behaviors import urls as behaviors_urls


    urlpatterns = [
        ...
        url(r'^', include(behaviors_urls)),
        ...
    ]
