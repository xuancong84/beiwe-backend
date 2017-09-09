import json, string

from random import choice as random_choice

from django.db import models
from django.db.models.base import ModelBase
from django.db.models.fields.related import RelatedField


ALPHANUMERICS = string.ascii_uppercase + string.ascii_lowercase + string.digits
class ObjectIdError(Exception): pass


class JSONTextField(models.TextField):
    """
    A TextField for holding JSON-serialized data. This is only different from models.TextField
    in AbstractModel.as_native_json, in that this is not JSON serialized an additional time.
    """
    pass


class AbstractModel(models.Model):
    """
    The AbstractModel is used to enable basic functionality for all database tables.

    AbstractModel descendants have a delete flag and function to mark as deleted, because
    we rarely want to truly delete an object. They also have a function to express the
    object as a JSON dict containing all fields and values of the object.
    """
    deleted = models.BooleanField(default=False)

    def mark_deleted(self):
        self.deleted = True
        self.save()

    @classmethod
    def generate_objectid_string(cls, field_name):
        """
        Takes a django database class and a field name, generates a unique BSON-ObjectId-like
        string for that field.
        In order to preserve functionality throughout the codebase we need to generate a random
        string of exactly 24 characters.  The value must be typeable, and special characters
        should be avoided.
        """
        for i in range(15):
            print i
            object_id = ''.join(random_choice(ALPHANUMERICS) for _ in range(24))
            if cls.objects.filter(**{field_name:object_id}).count() == 0:
                break
            if i > 10:
                raise ObjectIdError("Could not generate unique id for %s." % cls.__name__)
        return object_id

    def as_dict(self):
        """ Provides a dictionary representation of the object """
        return {field.name: getattr(self, field.name) for field in self._meta.fields}

    def as_native_python(self):
        """
        Collect all of the fields of the model and return their values in a python dict,
        with json fields appropriately deserialized.
        """
        field_dict = {}
        for field in self._meta.fields:
            field_name = field.name
            if isinstance(field, RelatedField):
                # Don't include related fields in the dict
                pass
            elif isinstance(field, JSONTextField):
                # If the field is a JSONTextField, load the field's value before returning
                field_raw_val = getattr(self, field_name)
                field_dict[field_name] = json.loads(field_raw_val)
            else:
                # Otherwise, just return the field's value
                field_dict[field_name] = getattr(self, field_name)
        return field_dict

    def as_native_json(self):
        """
        Collect all of the fields of the model and return their values in a python dict,
        with json fields appropriately serialized.
        """
        return json.dumps(self.as_native_python())

    def save(self, *args, **kwargs):
        # TODO if we encounter ValidationErrors here after the SQL migration, allow
        # invalid data but add a Sentry error.
        # Raise a ValidationError if any data is invalid
        self.full_clean()
        super(AbstractModel, self).save(*args, **kwargs)

    def __str__(self):
        if hasattr(self, 'study'):
            return '{} {} of Study {}'.format(self.__class__.__name__, self.pk, self.study.name)
        elif hasattr(self, 'name'):
            return '{} {}'.format(self.__class__.__name__, self.name)
        else:
            return '{} {}'.format(self.__class__.__name__, self.pk)

    class Meta:
        abstract = True
