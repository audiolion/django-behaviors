=============================
Django Behaviors
=============================

.. image:: https://badge.fury.io/py/django-behaviors.svg
    :target: https://badge.fury.io/py/django-behaviors

.. image:: https://travis-ci.org/audiolion/django-behaviors.svg?branch=master
    :target: https://travis-ci.org/audiolion/django-behaviors

.. image:: https://codecov.io/gh/audiolion/django-behaviors/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/audiolion/django-behaviors


Common behaviors for Django Models, e.g. Timestamps, Publishing, Authoring/Editing and more.

Inspired by Kevin Stone's `Django Model Behaviors`_.

Documentation
=============

Quickstart
----------

Install Django Behaviors::

    pip install django-behaviors
    # Or, if you are going to use the Slugged behaviour
    pip install django-behaviors[slugged]

Add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'behaviors.apps.BehaviorsConfig',
        ...
    )

Features
--------

``behaviors`` makes it easy to integrate common behaviors into your django models:

- **Documented**, **tested**, and **easy to use**
- **Timestamped** to add ``created`` and ``modified`` attributes to your models
- **StoreDeleted** to add ``deleted`` attribute to your models, avoiding the record to be deleted and allow to restore it
- **Authored** to add an ``author`` to your models
- **Editored** to add an ``editor`` to your models
- **Published** to add a ``publication_status`` (draft or published) to your models
- **Released** to add a ``release_date`` to your models
- **Slugged** to add a ``slug`` to your models (thanks @apirobot) (ensure you have `awesome-slugify` installed, see above)
- Easily compose together multiple ``behaviors`` to get desired functionality (e.g. ``Authored`` and ``Editored``)
- Custom ``QuerySet`` methods added as managers to your models to utilize the added fields
- Easily compose together multiple ``queryset`` or ``manager`` to get desired functionality

Table of Contents
-----------------

- `Behaviors`_
   - `Timestamped`_
   - `StoreDeleted`_
   - `Authored`_
   - `Editored`_
   - `Published`_
   - `Released`_
   - `Slugged`_
- `Mixing in with Custom Managers`_
- `Mixing Multiple Behaviors`_

Behaviors
---------

Timestamped Behavior
``````````````````````

The model adds a ``created`` and ``modified`` field to your model.

.. code-block:: python

  class Timestamped(models.Model):
      """
      An abstract behavior representing timestamping a model with``created`` and
      ``modified`` fields.
      """
      created = models.DateTimeField(auto_now_add=True, db_index=True)
      modified = models.DateTimeField(null=True, blank=True, db_index=True)

      class Meta:
          abstract = True

      @property
      def changed(self):
          return True if self.modified else False

      def save(self, *args, **kwargs):
          if self.pk:
              self.modified = timezone.now()
          return super(Timestamped, self).save(*args, **kwargs)

``created`` is set on the next save and is set to the current UTC time.
``modified`` is set when the object already exists and is set to the current UTC time.

``MyModel.changed`` returns a boolean representing if the object has been updated after created (the ``modified`` field has been set).

Here is an example of using the model, note you do not need to add ``models.Model`` because ``Timestamped`` already inherits it.

.. code-block:: python

    # models.py
    from behaviors.behaviors import Authored, Editored, Timestamped, Published


    class MyModel(Timestamped):
        name = models.CharField(max_length=100)


    >>> m = MyModel.objects.create(name='dj')
    >>> m.created
    '2017-02-14 17:20:19.835517+00:00'
    >>> m.modified
    None
    >>> m.changed
    False
    >>> m.save()
    >>> m.modified
    '2017-02-14 17:20:46.836395+00:00'
    >>> m.changed
    True

StoreDeleted Behavior
``````````````````````

The model add a ``deleted`` field to your model and prevent record to be deleted and allow to restore it

.. code-block:: python

  class StoreDeleted(models.Model):
      """
      An abstract behavior representing store deleted a model with``deleted`` field,
      avoiding the model object to be deleted and allowing you to restore it.
      """
      deleted = models.DateTimeField(null=True, blank=True)

      objects = StoreDeletedQuerySet.as_manager()

      class Meta:
          abstract = True

      @property
      def is_deleted(self):
          return self.deleted != None

      def delete(self, *args, **kwargs):
          if not self.pk:
              raise ObjectDoesNotExist('Object must be created before it can be deleted')
          self.deleted = timezone.now()
          return super(StoreDeleted, self).save(*args, **kwargs)

      def restore(self, *args, **kwargs):
          if not self.pk:
              raise ObjectDoesNotExist('Object must be created before it can be restored')
          self.deleted = None
          return super(StoreDeleted, self).save(*args, **kwargs)

``deleted`` is set when ``delete()`` method is called, with current UTC time.

Here is an example of using the model, note you do not need to add ``models.Model`` because ``StoreDeleted`` already inherits it.

.. code-block:: python

    # models.py
    from behaviors.behaviors import StoreDeleted


    class GreatModel(StoreDeleted):
        name = models.CharField(max_length=100)

    # Deleting model
    >>> gm = GreatModel.objects.create(name='Xtra')
    >>> gm.deleted
    None
    >>> gm.delete()
    >>> gm.deleted
    '2018-05-14 08:35:41.197661+00:00'

    # Restoring model
    >>> gm = GreatModel.objects.deleted(name='Xtra')
    >>> gm.deleted
    '2018-05-14 08:35:41.197661+00:00'
    >>> gm.restore()
    >>> gm.deleted
    None


Authored Behavior
``````````````````

The authored model adds an ``author`` attribute that is a foreign key to the ``settings.AUTH_USER_MODEL`` and adds manager methods through ``objects`` and ``authors``.

.. code-block:: python

  class Authored(models.Model):
      """
      An abstract behavior representing adding an author to a model based on the
      AUTH_USER_MODEL setting.
      """
      author = models.ForeignKey(
          settings.AUTH_USER_MODEL,
          related_name="%(app_label)s_%(class)s_author")

      objects = AuthoredQuerySet.as_manager()
      authors = AuthoredQuerySet.as_manager()

      class Meta:
          abstract = True

Here is an example of using the behavior and its ``authored_by()`` manager method:

.. code-block:: python

    # models.py
    from behaviors.behaviors import Authored


    class MyModel(Authored):
        name = models.CharField(max_length=100)

    >>> m = MyModel.objects.create(author=User.objects.get(pk=2), name='tj')
    >>> m.author
    <User: ...>
    >>> queryset = MyModel.objects.authored_by(User.objects.get(pk=2))
    >>> queryset.count()
    1

The author is a required field and must be provided on initial ``POST`` requests that create an object.

A custom ``models.ModelForm`` is provided to automatically add the ``author``
on object creation:

.. code-block:: python

    # forms.py
    from behaviors.forms import AuthoredModelForm
    from .models import MyModel


    class MyModelForm(AuthoredModelForm):
        class Meta:
          model = MyModel
          fields = ['name']

    # views.py
    from django.views.generic.edit import CreateView
    from .forms import MyModelForm
    from .models import MyModel


    class MyModelCreateView(CreateView):
        model = MyModel
        form = MyModelForm

        # add request to form kwargs
        def get_form_kwargs(self):
          kwargs = super(MyModelCreateView, self).get_form_kwargs()
          kwargs['request'] = self.request
          return kwargs

Now when the object is created the ``author`` will be added on the call
to ``form.save()``.

If you are using functional views or another view type you simply need
to make sure you pass the request object along with the form.

.. code-block:: python

    # views.py

    class MyModelView(View):
      template_name = "myapp/mymodel_form.html"

      def get(self, request, *args, **kwargs):
          context = {
            'form': MyModelForm(),
          }
          return render(request, self.template_name, context=context)

      def post(self, request, *args, **kwargs):
          # pass in request object to the request keyword argument
          form = MyModelForm(self.request.POST, request=request)
          if form.is_valid():
              form.save()
              return reverse(..)
          context = {
            'form': form,
          }
          return render(request, self.template_name, context=context)

If for some reason you don't want to mixin the ``AuthoredModelForm`` with your existing
form you can just add the user like so:

.. code-block:: python

    # ...
    if form.is_valid()
        obj = form.save(commit=False)
        obj.author = request.user
        obj.save()
        return reverse(..)
    # ...

But it isn't recommended, the ``AuthoredModelForm`` is tested and doesn't reassign the
author on every save.

The ``related_name`` is set so that it will never create conflicts. Given the above example if you wanted to do a reverse foreign key lookup from the User model and ``MyModel`` was part of the ``blogs`` app it could be done like so:

.. code-block:: python

    >>> user = User.objects.get(pk=2)
    >>> user.blogs_mymodel_author.all()
    [<MyModel: ...>]

That would give a list of all ``MyModel`` objects that ``user`` has ``authored``.

Authored QuerySet
..................

The ``Authored`` behavior attaches a custom model manager to the default ``objects``
and to the ``authors`` variables on the model it is mixed into. If you haven't overrode
the ``objects`` variable with a custom manager then you can use that, otherwise the
``authors`` variable is a fallback.

To get all ``MyModel`` instances authored by people whose name starts with 'Jo'

.. code-block:: python

    # case is insensitive so 'joe' or 'Joe' matches
    >>> MyModel.objects.authored_by('Jo')
    [<MyModel: ...>, <MyModel: ...>, ...]

    # or use the authors manager variable
    >>> MyModel.authors.authored_by('Jo')
    [<MyModel: ...>, <MyModel: ...>, ...]

See `Mixing in with Custom Managers`_ for details on how
to mix in this behavior with a custom manager you have that overrides the ``objects``
default manager.


Editored Behavior
``````````````````

The editored model adds an ``editor`` attribute that is a foreign key to the ``settings.AUTH_USER_MODEL`` and adds manager methods through ``objects`` and ``editors`` variables.


.. code-block:: python

    class Editored(models.Model):
    """
    An abstract behavior representing adding an editor to a model based on the
    AUTH_USER_MODEL setting.
    """
    editor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="%(app_label)s_%(class)s_editor",
        blank=True, null=True)

    objects = EditoredQuerySet.as_manager()
    editors = EditoredQuerySet.as_manager()

    class Meta:
        abstract = True

The ``Editored`` model is similar to the ``Authored`` model except the foreign key is **not required**. Here is an example of its usage:

.. code-block:: python

    # models.py
    from behaviors.behaviors import Editored


    class MyModel(Editored):
        name = models.CharField(max_length=100)

    >>> m = MyModel.objects.create(name='pj')
    >>> m.editor
    None
    >>> m.editor = User.objects.all()[0]
    >>> m.save()
    >>> queryset = MyModel.objects.edited_by(User.objects.all()[0])
    >>> queryset.count()
    1

By default the ``editor`` is blank and null, if a ``request`` object is supplied to the form it will assign a new editor and erase the previous editor (or the null editor).

Instead of using the ``AuthoredModelForm`` use the ``EditoredModelForm`` as a mixin to
your form.

.. code-block:: python

    # forms.py
    from behaviors.forms import EditoredModelForm
    from .models import MyModel


    class MyModelForm(EditoredModelForm):
        class Meta:
          model = MyModel
          fields = ['name']

    # views.py
    from django.views.generic.edit import CreateView, UpdateView
    from .forms import MyModelForm
    from .models import MyModel


    MyModelRequestFormMixin(object):
        # add request to form kwargs
        def get_form_kwargs(self):
          kwargs = super(MyModelCreateView, self).get_form_kwargs()
          kwargs['request'] = self.request
          return kwargs


    class MyModelCreateView(MyModelRequestFormMixin, CreateView):
        model = MyModel
        form = MyModelForm


    class MyModelUpdateView(MyModelRequestFormMixin, UpdateView):
        model = MyModel
        form = MyModelForm


Now when the object is created or updated the ``editor`` will be updated
on the call to ``form.save()``.

If you are using functional views or another view type you simply need
to make sure you pass the request object along with the form.

.. code-block:: python

    # views.py

    class MyModelView(View):
      template_name = "myapp/mymodel_form.html"

      def get(self, request, *args, **kwargs):
          context = {
            'form': MyModelForm(),
          }
          return render(request, self.template_name, context=context)

      def post(self, request, *args, **kwargs):
          # pass in request object to the request keyword argument
          form = MyModelForm(self.request.POST, request=request)
          if form.is_valid():
              form.save()
              return reverse(..)
          context = {
            'form': form,
          }
          return render(request, self.template_name, context=context)

If for some reason you don't want to mixin the ``EditoredModelForm`` with your existing
form you can just add the user like so:

.. code-block:: python

    ...
    if form.is_valid()
        obj = form.save(commit=False)
        obj.editor = request.user
        obj.save()
        return reverse(..)
    ...

But it isn't recommended, the ``EditoredModelForm`` is tested and doesn't cause errors
if request.user is invalid.

The ``related_name`` is set so that it will never create conflicts. Given the above example if you wanted to do a reverse foreign key lookup from the User model and ``MyModel`` was part of the ``blogs`` app it could be done like so:

.. code-block:: python

    >>> user = User.objects.get(pk=2)
    >>> user.blogs_mymodel_editor.all()
    [<MyModel: ...>]

That would give a list of all ``MyModel`` objects that ``user`` is an ``editor``.

Editored QuerySet
..................

The ``Editored`` behavior attaches a custom model manager to the default ``objects``
and to the ``editors`` variables on the model it is mixed into. If you haven't overrode
the ``objects`` variable with a custom manager then you can use that, otherwise the
``editors`` variable is a fallback.

To get all ``MyModel`` instances edited by people whose name starts with 'Jo'

.. code-block:: python

    # case is insensitive so 'joe' or 'Joe' matches
    >>> MyModel.objects.edited_by('Jo')
    [<MyModel: ...>, <MyModel: ...>, ...]

    # or use the editors manager variable
    >>> MyModel.editors.edited_by('Jo')
    [<MyModel: ...>, <MyModel: ...>, ...]

See `Mixing in with Custom Managers`_ for details on how
to mix in this behavior with a custom manager you have that overrides the ``objects``
default manager.

Published Behavior
````````````````````

The ``Published`` behavior adds a field ``publication_status`` to your model. The status
has two states: 'Draft' or 'Published'.

.. code-block:: python

    class Published(models.Model):
        """
        An abstract behavior representing adding a publication status. A
        ``publication_status`` is set on the model with Draft or Published
        options.
        """
        DRAFT = 'd'
        PUBLISHED = 'p'

        PUBLICATION_STATUS_CHOICES = (
            (DRAFT, 'Draft'),
            (PUBLISHED, 'Published'),
        )

        publication_status = models.CharField(
            "Publication Status", max_length=1,
            choices=PUBLICATION_STATUS_CHOICES, default=DRAFT)

        class Meta:
            abstract = True

        objects = PublishedQuerySet.as_manager()
        publications = PublishedQuerySet.as_manager()

        @property
        def draft(self):
            return self.publication_status == self.DRAFT

        @property
        def published(self):
            return self.publication_status == self.PUBLISHED

The class offers two properties ``draft`` and ``published`` to know object state. The ``DRAFT`` and ``PUBLISHED`` class constants will be available from the class the ``Published`` behavior is mixed into. There is also a custom manager attached to ``objects`` and ``publications`` variables to get ``published()`` or ``draft()`` querysets.

.. code-block:: python

    # models.py
    from behaviors.behaviors import Published


    class MyModel(Published):
        name = models.CharField(max_length=100)

    >>> m = MyModel.objects.create(name='cj')
    >>> m.publication_status
    u'd'
    >>> m.draft
    True
    >>> m.published
    False
    >>> m.get_publication_status_display()
    u'Draft'
    >>> MyModel.objects.published().count()
    0
    >>> MyModel.objects.draft().count()
    1
    >>> m.publication_status = MyModel.PUBLISHED
    >>> m.save()
    >>> m.publication_status
    u'p'
    >>> m.draft
    False
    >>> m.published
    True
    >>> m.get_publication_status_display()
    u'Published'
    >>> MyModel.objects.published().count()
    1
    >>> MyModel.PUBLISHED
    u'p'
    >>> MyModel.PUBLISHED == m.publication_status
    True

The ``publication_status`` field defaults to ``Published.DRAFT`` when you make new
models unless you supply the ``Published.PUBLISHED`` attribute to the ``publication_status``
field.

.. code-block:: python

    MyModel.objects.create(name='Jim-bob Cooter', publication_status=MyModel.PUBLISHED)

Published QuerySet
...................

The ``Published`` behavior attaches to the default ``objects`` variable and
the ``publications`` variable as a fallback if ``objects`` is overrode.

.. code-block:: python

    # returns all MyModel.PUBLISHED
    MyModel.objects.published()
    MyModel.publications.published()

    # returns all MyModel.DRAFT
    MyModel.objects.draft()
    MyModel.publications.draft()


Released Behavior
``````````````````

The ``Released`` behavior adds a field ``release_date`` to your model. The field
is **not_required**. The release date can be set with the ``release_on(datetime)`` method.

.. code-block:: python

    class Released(models.Model):
        """
        An abstract behavior representing a release_date for a model to
        indicate when it should be listed publically.
        """
        release_date = models.DateTimeField(null=True, blank=True)

        class Meta:
            abstract = True

        objects = ReleasedQuerySet.as_manager()
        releases = ReleasedQuerySet.as_manager()

        def release_on(self, date=None):
            if not date:
                date = timezone.now()
            self.release_date = date
            self.save()

        @property
        def released(self):
            return self.release_date and self.release_date < timezone.now()

There is a ``released`` property added which determines if the object has been released. There is a custom manager attached to ``objects`` and ``releases`` variables to filter querysets on their release date.

Here is an example of using the behavior:

.. code-block:: python

    # models.py
    from django.utils import timezone
    from datetime import timedelta
    from behaviors.behaviors import Released


    class MyModel(Released):
        name = models.CharField(max_length=100)

    >>> m = MyModel.objects.create(name='rj')
    >>> m.release_date
    None
    >>> MyModel.objects.no_release_date().count()
    1
    >>> m.release_on()
    >>> MyModel.objects.no_release_date().count()
    0
    >>> MyModel.objects.released().count()
    1
    >>> m.release_on(timezone.now() + timedelta(weeks=1))
    >>> MyModel.objects.not_released().count()
    1
    >>> MyModel.objects.released().count()
    0

The ``release_on`` method defaults to the current time so that the object is immediately
released. You can also provide a date to the method to release on a certain date. ``release_on()`` just serves as a wrapper to setting and saving the date.

You can always provide a ``release_date`` on object creation:

.. code-block:: python

    MyModel.objects.create(name='Jim-bob Cooter', release_date=timezone.now())


Released QuerySet
...................

The ``Released`` behavior attaches to the default ``objects`` variable and
the ``releases`` variable as a fallback if ``objects`` is overrode.

.. code-block:: python

    # returns all not released MyModel objects
    MyModel.objects.not_released()
    MyModel.releases.not_released()

    # returns all released MyModel objects
    MyModel.objects.released()
    MyModel.releases.released()

    # returns all null release date MyModel objects
    MyModel.objects.no_release_date()
    MyModel.releases.no_release_date()

Slugged Behavior
``````````````````

The ``Slugged`` behavior allows you to easily add a ``slug`` field to your model. The slug is generated on the first model creation or the next model save and is based on the ``slug_source`` attribute.

**The** ``slug_source`` **property has no set default, you must add it to your model for the behavior to work.**

.. code-block:: python

    class Slugged(models.Model):
        """
        An abstract behavior representing adding a slug (by default, unique) to
        a model based on the slug_source property.
        """
        slug = models.SlugField(
            max_length=255,
            unique=BehaviorsConfig.are_slug_unique(),
            blank=True)

        class Meta:
            abstract = True

        def save(self, *args, **kwargs):
            if not self.slug:
                self.slug = self.generate_unique_slug() \
                    if BehaviorsConfig.are_slug_unique() else self.get_slug()
            super(Slugged, self).save(*args, **kwargs)

        def get_slug(self):
            return slugify(getattr(self, "slug_source"), to_lower=True)

        def is_unique_slug(self, slug):
            qs = self.__class__.objects.filter(slug=slug)
            return not qs.exists()

        def generate_unique_slug(self):
            slug = self.get_slug()
            new_slug = slug

            iteration = 1
            while not self.is_unique_slug(new_slug):
                new_slug = "%s-%d" % (slug, iteration)
                iteration += 1

            return new_slug

The ``slug`` uses the awesome-slugify package which will preserve unicode
character slugs. By default, the ``slug`` must be unique and is guaranteed to
be unique by the class appending a number ``-[0-9+]`` to the end of the slug
if it is not unique. The ``unique`` field type `adds an index`_ to the ``slug`` field.

Add the ``slug_source`` property to your class when mixing in the behavior.

To allow non-unique slugs, add ``UNIQUE_SLUG_BEHAVIOR = False`` to your project's settings.

.. code-block:: python

    # models.py
    from behaviors.behaviors import Slugged


    class MyModel(Slugged):
        name = models.CharField(max_length=100)

        # slug_source is required for the slug to be set
        @property
        def slug_source(self):
          return "prepended-text-for-fun-{}".format(self.name)

        # you can now use the slug for your get_absolute_url() method
        def get_absolute_url(self):
          return reverse('myapp:mymodel_detail', args=[self.slug])

    >>> m = MyModel.objects.create(name='aj')
    >>> m.slug
    'prepended-text-for-fun-aj'
    >>> m2 = MyModel.objects.create(name='aj')
    >>> m.slug
    'prepended-text-for-fun-aj-1'
    >>> m.get_absolute_url()
    '/myapp/prepended-text-for-fun-aj/detail'

Your ``slug_source`` attribute can be a mix of any of the model data available at the time of save, generally it is some ``name`` type of field. You could also hash the primary key and/or some other data as a ``slug_source``.
By default, the ``slug`` is unique so it can be used to define the ``get_absolute_url()`` method on your model.

Thanks to @apirobot for sending the PR for the ``Slugged`` behavior.

Mixing in with Custom Managers
------------------------------

If you have a custom manager on your model already:

.. code-block:: python

    # models.py
    from behaviors.behaviors import Authored, Editored, Published, Timestamped

    from django.db import models


    class MyModelCustomManager(models.Manager):

        def get_queryset(self):
            return super(MyModelCustomManager).get_queryset(self)

        def custom_manager_method(self):
            return self.get_queryset().filter(name='Jim-bob')

    class MyModel(Authored):
        name = models.CharField(max_length=100)

        # MyModel.objects.authored_by(..) won't work
        # MyModel.authors.authored_by(..) still will
        objects = MyModelCustomManager()

Simply add ``AuthoredManager`` from ``behaviors.managers`` as a mixin to
``MyModelCustomManager`` so they can share the ``objects`` variable.

.. code-block:: python

    # models.py
    from behaviors.behaviors import Authored, Editored, Published, Timestamped
    from behaviors.managers import AuthoredManager, EditoredManager, PublishedManager

    from django.db import models


    class MyModelCustomManager(AuthoredManager, models.Manager):

        def get_queryset(self):
            return super(MyModelCustomManager).get_queryset(self)

        def custom_manager_method(self):
            return self.get_queryset().filter(name='Jim-bob')

    class MyModel(Authored):
        name = models.CharField(max_length=100)

        # MyModel.objects.authored_by(..) now works
        objects = MyModelCustomManager()

Similarly if you are using a custom QuerySet and calling its ``as_manager()``
method to attach it to ``objects`` you can import from ``behaviors.querysets``
and mix it in.

.. code-block:: python

    # models.py
    from behaviors.behaviors import Authored, Editored, Published, Timestamped
    from behaviors.querysets import AuthoredQuerySet, EditoredQuerySet, PublishedQuerySet

    from django.db import models


    class MyModelCustomQuerySet(AuthoredQuerySet, models.QuerySet):

        def custom_queryset_method(self):
            return self.filter(name='Jim-bob')

    class MyModel(Authored):
        name = models.CharField(max_length=100)

        # MyModel.objects.authored_by(..) works
        objects = MyModelCustomQuerySet.as_manager()


Mixing in Multiple Behaviors
----------------------------

Many times you will want multiple behaviors on a model. You can simply mix in
multiple behaviors and, if you'd like to have all their custom ``QuerySet``
methods work on ``objects``, provide a custom manager with all the mixins.

.. code-block:: python

    # models.py
    from behaviors.behaviors import Authored, Editored, Published, Timestamped
    from behaviors.querysets import AuthoredQuerySet, EditoredQuerySet, PublishedQuerySet

    from django.db import models


    class MyModelQuerySet(AuthoredQuerySet, EditoredQuerySet, PublishedQuerySet):
        pass

    class MyModel(Authored, Editored, Published, Timestamped):
        name = models.CharField(max_length=100)

        # MyModel.objects.authored_by(..) works
        # MyModel.objects.edited_by(..) works
        # MyModel.objects.published() works
        # MyModel.objects.draft() works
        objects = MyModelQuerySet.as_manager()

    # you can also chain queryset methods
    >>> u = User.objects.all()[0]
    >>> u2 = User.objects.all()[1]
    >>> m = MyModel.objects.create(author=u, editor=u2)
    >>> MyModel.objects.published().authored_by(u).count()
    1


Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install tox
    (myenv) $ tox

Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage

.. _`Timestamped`: #timestamped-behavior
.. _`StoreDeleted`: #storedeleted-behavior
.. _`Authored`: #authored-behavior
.. _`Editored`: #editored-behavior
.. _`Published`: #published-behavior
.. _`Released`: #released-behavior
.. _`Slugged`: #slugged-behavior
.. _`settings.AUTH_USER_MODEL`: https://docs.djangoproject.com/en/1.10/ref/settings/#std:setting-AUTH_USER_MODEL
.. _`Mixing in with Custom Managers`: #mixing-in-with-custom-managers
.. _`Mixing Multiple Behaviors`: #mixing-in-multiple-behaviors
.. _`Django Model Behaviors`: http://blog.kevinastone.com/django-model-behaviors.html
.. _`adds an index`: https://docs.djangoproject.com/en/dev/ref/models/fields/#unique
