from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import connections, transaction


class WrongDefinition(Exception):
    pass


class ValidationError(Exception):
    def __init__(self, imported_object, message_dict):
        super(ValidationError, self).__init__()
        self.imported_object = imported_object
        self.message_dict = message_dict


class Migrator(object):
    skip_on_match = []
    skip_validation = False

    def process_fields(self, source, target):
        for method_name in dir(self):
            if not method_name.startswith('import_'):
                continue

            field_name = method_name[7:]
            if field_name not in self.allowed_fields:
                raise WrongDefinition(
                    'field not in target model: %s' % field_name)

            field_value = getattr(self, method_name)(source)
            setattr(target, field_name, field_value)

    def pre_save(self, source, target):
        pass

    def post_save(self, source, target):
        pass

    def check_unique(self, target):
        """
        Checks if an object with fields matched by `skip_on_match`
        already extists in the target database.
        """
        if not self.skip_on_match:
            return False

        target_unique_filter = {
            fn: getattr(target, fn, None)
            for fn in self.skip_on_match
        }
        return self.target_model.objects.filter(**target_unique_filter).exists()


    @transaction.atomic
    def run_migration(self):
        self.allowed_fields = set(
            f.name for f in self.target_model._meta.fields)

        for source_object in self.iter_source():
            target_object = self.target_model()
            self.process_fields(source_object, target_object)
            self.pre_save(source_object, target_object)

            if self.check_unique(target_object):
                continue

            if not self.skip_validation:
                try:
                    target_object.full_clean()
                except DjangoValidationError as e:
                    raise ValidationError(
                        target_object,
                        e.message_dict)
            target_object.save()
            self.post_save(source_object, target_object)


class ModelToModelMigrator(Migrator):
    fields = []

    def process_fields(self, source, target):
        for source_field, target_field in self.fields:
            if target_field not in self.allowed_fields:
                raise WrongDefinition(
                    'field not in target model: %s' % target_field)

            field_value = getattr(source, source_field)
            setattr(target, target_field, field_value)

        super(ModelToModelMigrator, self).process_fields(source, target)

    def get_source_query_set(self):
        if hasattr(self, 'source_model'):
            return self.source_model.objects.all()
        else:
            return self.source_query_set

    def iter_source(self):
        return self.get_source_query_set().iterator()


class SQLToModelMigrator(Migrator):
    fields = []
    source_db = 'default'

    def get_cursor(self):
        cursor = connections[self.source_db].cursor()

        if hasattr(self, 'sql'):
            cursor.execute(self.sql)
        elif hasattr(self, 'source_table'):
            cursor.execute('select * from `%s`' % self.source_table)
        else:
            raise WrongDefinition(
                'no sql or source_table specified for SQLToModelMigrator')

        return cursor

    def iter_source(self):
        cursor = self.get_cursor()
        field_names = [d[0] for d in cursor.description]

        while True:
            v = cursor.fetchone()
            if not v:
                break
            yield dict(zip(field_names, v))

    def process_fields(self, source, target):
        for source_column, target_field in self.fields:
            if target_field not in self.allowed_fields:
                raise WrongDefinition(
                    'field not in target model: %s' % target_field)

            try:
                v = source[source_column]
            except KeyError:
                raise WrongDefinition(
                    'column %s not in SQL result' % source_column)
            setattr(target, target_field, v)

        super(SQLToModelMigrator, self).process_fields(source, target)

