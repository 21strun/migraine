from model_mommy import mommy
from model_mommy.recipe import Recipe, seq
import pytest

from migraine.migrators import ValidationError
from polls.models import OldPoll, NewPoll
import migrators.polls as mp


@pytest.mark.django_db
def test_polls_migrator():
    old_polls = mommy.make(OldPoll, _quantity=3)
    migrator = mp.PollsMigrator()
    migrator.run_migration()
    assert NewPoll.objects.count() == 3

    for p in old_polls:
        assert NewPoll.objects.filter(new_poll_name=p.old_poll_name).count() == 1

@pytest.mark.django_db
def test_appending_polls_migrator():
    old_polls = mommy.make(OldPoll, _quantity=3)
    migrator = mp.AppendingPollsMigrator()
    migrator.run_migration()
    assert NewPoll.objects.count() == 3

    for p in old_polls:
        np_match = NewPoll.objects.filter(
            new_poll_name=p.old_poll_name + ' (old)')
        assert np_match.count() == 1

@pytest.mark.django_db
def test_queryset_to_model_migrator():
    ignored_old_polls = mommy.make(OldPoll, _quantity=3)
    collected_old_polls = mommy.make(
        OldPoll, old_poll_name=seq('herpderp'), _quantity=3)
    migrator = mp.QuerysetToModelMigrator()
    migrator.run_migration()
    assert NewPoll.objects.count() == 3

    for p in collected_old_polls:
        np_match = NewPoll.objects.filter(new_poll_name=p.old_poll_name)
        assert np_match.count() == 1

@pytest.mark.django_db
def test_skipping_migrator():
    old_polls = mommy.make(OldPoll, old_poll_name='derp', _quantity=3)
    migrator = mp.SkippingPollsMigrator()
    migrator.run_migration()
    assert NewPoll.objects.count() == 1

@pytest.mark.django_db
def test_nonunique_target_field():
    old_polls = mommy.make(OldPoll, old_poll_name='derp', _quantity=3)
    migrator = mp.PollsMigrator()
    with pytest.raises(ValidationError):
        migrator.run_migration()

    assert NewPoll.objects.count() == 0

@pytest.mark.django_db
def test_simple_sql_to_model_migrator():
    old_polls = mommy.make(OldPoll, _quantity=3)
    migrator = mp.PollsBySQLMigrator()
    migrator.run_migration()
    assert NewPoll.objects.count() == 3

    for p in old_polls:
        np_match = NewPoll.objects.filter(new_poll_name=p.old_poll_name)
        assert np_match.count() == 1

@pytest.mark.django_db
def test_sql_query_to_model_migrator():
    ignored_old_polls = mommy.make(OldPoll, _quantity=3)
    collected_old_polls = mommy.make(
        OldPoll, old_poll_name=seq('herpderp'), _quantity=3)
    migrator = mp.ComplexPollsBySQLMigrator()
    migrator.run_migration()
    assert NewPoll.objects.count() == 3

    for p in collected_old_polls:
        np_match = NewPoll.objects.filter(
            new_poll_name=p.old_poll_name + ' (old)')
        assert np_match.count() == 1

