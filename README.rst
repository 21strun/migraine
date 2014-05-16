Migraine
========

Migraine helps with painful data migrations.

It provides a framework for running cross-model and SQL-to-model data
migrations for Django. Migraine's Migrator classes provide a declarative
approach to importing data from external databases and Django models
into other Django models, with a syntax somewhat similar to Django's
ModelForms. Migraine will also run you your migrations in order derived
from inter-migration dependencies.

Building a migration project
============================

To use Migraine, you will need to create a project containing two basic
elements: a migrators package containg one module per Django app and a
bootstrap script you will use to set up django settings and start a
migration.

Migraine projects are recommended to be placed outside of your main
application's source code, so make sure the target app is available on
the PYTHONPATH. You can append its path in an environment variable or in
the ``migrate.py`` script.

Assuming we want to migrate to a single app called ``polls``, here is
how our project structure will look like:

::

    polls_migration/
        __init__.py
        migrate.py
        migrators/
            __init__.py
            polls.py

We created a ``migrate.py`` module that will contain our configuration
code, and a ``polls.py`` module where we will define our migrator
classes.

Writing a bootstrap script
==========================

Your ``migrate.py`` script needs to do two things:

1. Import your migrators package.
2. Call ``run_from_command_line``.

You can also use it for additional configuration, like loading Django
settings.

Here is a basic example:

::

    #!/usr/bin/env python
    import sys
    from migraine import run_from_command_line
    import migrators

    if __name__ == "__main__":
        run_from_command_line(migrators, sys.argv)

Defining Migrators
==================

A Migrator class defines how we want to process the data we're going to
migrate. It can be any class providing a ``run_migration`` method.
Inside each of the ``migrators`` package submodules define a list called
``migrators``, containing names of classes from that submodule that you
wish to be detected by migraine's migration-running mechanism.

Model to Model migrations
-------------------------

Migraine provides a base ``ModelToModelMigrator`` that will create a
single record in the target model per each record from the source model.
We will use it to migrate data from an old model called OldPoll to a
fresh model called NewPoll.

::

    # our app's models:

    from django.db import models

    class OldPoll(models.Model):
        old_poll_name = models.CharField(max_length=30)

    class NewPoll(models.Model):
        new_poll_name = models.CharField(max_length=36)


    # migrators/polls.py:

    from migraine.migrators import ModelToModelMigrator
    from polls.models import OldPoll, NewPoll

    migrators = ['PollsMigrator']

    class PollsMigrator(ModelToModelMigrator):
        source_model = OldPoll
        target_model = NewPoll
        fields = [
            ('old_poll_name', 'new_poll_name')
        ]

We've just created a Migrator that will copy over OldPolls to NewPolls.

You can also define more complex rules for processing fields. Let's
assume we want the old polls' names to end with "(old)". For each such
field we can define a method that will return a processed value.
Migraine uses a convention of prepending such methods' names with
``import_``:

::

    class AppendingPollsMigrator(ModelToModelMigrator):
        source_model = OldPoll
        target_model = NewPoll

        def import_new_poll_name(self, source):
            return source.old_poll_name + ' (old)'

Effect of running such a migration will be identical to running

::

    new_poll.new_poll_name = source.old_poll_name + ' (old)'

for each newly created NewPoll object.

Instead of a ``source_model``, you can also define a ``query_set`` field
if you need more control over source data.

SQL table to model migrations
-----------------------------

Migraine can handle importing data from a raw SQL database. For this,
there is an ``SQLToModelMigrator``.

::

    from blog.models import Author, BlogPost
    migrators = ['BlogPostMigrator']

    class BlogPostMigrator(SQLToModelMigrator):
        source_db = 'oldblog'
        source_table = 'blog_posts'
        target_model = BlogPost
        skip_on_match = ['name']
        fields = [
            ('title', 'title'),
            ('content', 'content'),
        ]

        def import_author(self, source):
            return Author.objects.get_or_create(name=source['author_name'])

This simple example will populate the BlogPost model with data from
``blog_post`` table's rows. The ``import_`` methods' ``source`` argument
contains a dict mapping column names to values for each of source
table's rows.

The ``source_db`` field declares the database to be used. The database
needs to be decared in the DATABASES dict in django settings. It is
optional and defaults to ``default``.

Intead of ``source_table``, you can define an ``sql`` field. This will
cause the Migrator to use query's result rows as the source feed.

Running migrations
==================

To launch all migrations, run your bootstrap script:

::

    python migrate.py

You can also specify individual migrations to run. To see a list of
available migrations run ``migrate.py --list``.

Migrator dependencies
=====================

Migraine can sort your migrations using topological sorting based on
inter-migration dependencies. To use this feature, declare a
``depends_on`` field on your Migrators that will contain a list of
migrator names:

::

    # migrators/foo.py
    migrators = ['MigratorA', MigratorB']

    class MigratorA:
        depends_on = ['foo.MigratorB']
        # ...

    class MigratorB:
        # ...

In this example, MigratorB will always be run before MigratorA.

Running tests
=============

::

    cd testapp
    pip install -r requirements.txt  # you probably want to make a virtualenv
                                     # for this
    DJANGO_SETTINGS_MODULE=settings PYTHONPATH=`pwd` py.test

