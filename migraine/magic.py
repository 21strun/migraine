"""
Magic responsible for collecting migrators from a package and handling
dependencies.
"""

import importlib
import pkgutil


class DependencyCycle(Exception):
    pass


def iter_migrators_from_module(module):
    for m_name in getattr(module, 'migrators', []):
        m = getattr(module, m_name)
        yield m


def gather_modules(module):
    migrators = {}
    for importer, modname, ispkg in pkgutil.iter_modules(module.__path__):
        mod = importlib.import_module(module.__name__ + '.' + modname)
        for klass in iter_migrators_from_module(mod):
            migrators[modname + '.' + klass.__name__] = klass

    return migrators


def toposort_migrators(requested_migrators, available_migrators):
    """
    A DFS-based topological sort for Migrator dependencies.

    :param requested_migrators: list of requested migrators (pairs of
                                name, Migrator)
    :param available_migrators: dict mapping availble migrator names to classes
    :returns:                   sorted list
    """
    NOT_VISITED = 0
    ENTERED = 1
    VISITED = 2

    sorted_ = []

    def dfs(migrator):
        node_state = getattr(migrator, '_toposort_visited', NOT_VISITED)

        if node_state == VISITED:
            return

        if node_state == ENTERED:
            raise DependencyCycle(
                'found a dependency cycle containing %s' % migrator.name)

        # not visited yet
        migrator._toposort_visited = ENTERED
        for dep_name in getattr(migrator, 'depends_on', []):
            dep = available_migrators[dep_name]
            if getattr(dep, '_toposort_requested', False):
                dfs(dep)
            else:
                # TODO: Migrator depends on a migrator that was not requested.
                # Currently we only sort within the requested list and ignore
                # dependencies that were not requested.
                pass
        migrator._toposort_visited = VISITED
        sorted_.append(migrator)

    for name, migrator in requested_migrators:
        migrator._toposort_requested = True
        migrator.name = name  # hack name onto the Migrator

    for name, migrator in requested_migrators:
        dfs(migrator)

    # clean up
    for name, migrator in requested_migrators:
        delattr(migrator, '_toposort_visited')
        delattr(migrator, '_toposort_requested')

    return sorted_

