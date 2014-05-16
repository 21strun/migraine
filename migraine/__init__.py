#!/usr/bin/env python
# coding: utf-8

"""
Migraine helps with painful data migrations.
"""

from magic import gather_modules, toposort_migrators
from migrators import ValidationError


def run_from_command_line(migrators_package, argv):
    # gather available Migrator classes
    migrators = gather_modules(migrators_package)

    if '--list' in argv:
        for m in migrators.iterkeys():
            print m
        return

    # choose classes to run
    requested_migrators = argv[1:]
    if len(requested_migrators) == 0:
        to_run = migrators.items()
    else:
        to_run = []
        for rname in requested_migrators:
            try:
                m = migrators[rname]
            except KeyError:
                print 'Unknown migrator:', rname
                return
            to_run.append((rname, m))

    # run migrations
    try:
        for migrator in toposort_migrators(to_run, migrators):
            print 'running migrator', migrator.name
            migrator().run_migration()
    except ValidationError as ve:
        print 'ValidationError'
        print 'Object:', ve.imported_object
        print 'Errors:'
        for field, msg_list in ve.message_dict.iteritems():
            for msg in msg_list:
                print u'{:>20}: {}'.format(field, msg)
