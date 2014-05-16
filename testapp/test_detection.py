import pytest

from migraine.magic import DependencyCycle, gather_modules, toposort_migrators

def test_finding_migrators():
    import migrators
    modules_dict = gather_modules(migrators)
    assert set(modules_dict.keys()) == set([
        'polls.PollsMigrator',
        'polls.AppendingPollsMigrator',
    ])

    from migrators.polls import PollsMigrator
    assert modules_dict['polls.PollsMigrator'] == PollsMigrator

def test_sorting_requested_list():
    from migrators.dependencies import Spam1, Spam2, Ham1, Ham2
    modules = {
        'dependencies.Spam1': Spam1,
        'dependencies.Spam2': Spam2,
        'dependencies.Ham1': Ham1,
        'dependencies.Ham2': Ham2,
    }

    sorted_ = toposort_migrators(
        [('dependencies.Spam1', Spam1), ('dependencies.Ham1', Ham1)],
        modules)
    assert sorted_ == [Ham1, Spam1]

    with pytest.raises(DependencyCycle):
        toposort_migrators(modules.items(), modules)
