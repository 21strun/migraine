from migraine.migrators import ModelToModelMigrator, SQLToModelMigrator
from testapp.polls.models import OldPoll, NewPoll

migrators = ['PollsMigrator', 'AppendingPollsMigrator']

class PollsMigrator(ModelToModelMigrator):
    source_model = OldPoll
    target_model = NewPoll
    fields = [
        ('old_poll_name', 'new_poll_name')
    ]

class AppendingPollsMigrator(ModelToModelMigrator):
    source_model = OldPoll
    target_model = NewPoll

    def import_new_poll_name(self, source):
        return source.old_poll_name + ' (old)'


class QuerysetToModelMigrator(ModelToModelMigrator):
    source_query_set = OldPoll.objects.filter(
        old_poll_name__startswith='herpderp')
    target_model = NewPoll
    fields = [
        ('old_poll_name', 'new_poll_name')
    ]

class SkippingPollsMigrator(ModelToModelMigrator):
    source_model = OldPoll
    target_model = NewPoll
    fields = [
        ('old_poll_name', 'new_poll_name')
    ]
    skip_on_match = ['new_poll_name']

class PollsBySQLMigrator(SQLToModelMigrator):
    source_table = 'polls_oldpoll'
    target_model = NewPoll

    fields = [
        ('old_poll_name', 'new_poll_name')
    ]

class ComplexPollsBySQLMigrator(SQLToModelMigrator):
    sql = "SELECT * FROM polls_oldpoll WHERE old_poll_name LIKE 'herpderp%'"
    target_model = NewPoll

    def import_new_poll_name(self, source):
        return source['old_poll_name'] + ' (old)'
