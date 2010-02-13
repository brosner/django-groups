import datetime
import warnings

from django.db import models
from django.db.models.options import FieldDoesNotExist
from django.db.models.query import QuerySet
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType



def _get_queryset(klass):
    """
    Returns a QuerySet from a Model, Manager, or QuerySet. Created to make
    get_object_or_404 and get_list_or_404 more DRY.
    
    Pulled from django.shortcuts
    """
    
    if isinstance(klass, QuerySet):
        return klass
    elif isinstance(klass, models.Manager):
        manager = klass
    else:
        manager = klass._default_manager
    return manager.all()


class GroupAware(models.Model):
    """
    A mixin abstract base model to use on models you want to make group-aware.
    """
    
    group_content_type = models.ForeignKey(ContentType, null=True, blank=True)
    group_object_id = models.PositiveIntegerField(null=True, blank=True)
    group = generic.GenericForeignKey("group_content_type", "group_object_id")
    
    class Meta:
        abstract = True


class GroupBase(models.Model):
    
    slug_attr = "slug"
    
    class Meta(object):
        abstract = True
    
    def member_queryset(self):
        if not hasattr(self, "_members_field"):
            # look for the common case of a m2m named members (in some cases
            # the related_name of the user FK on the intermediary model might
            # be named members and we need User instances)
            try:
                field = self._meta.get_field("members")
            except FieldDoesNotExist:
                raise NotImplementedError("You must define a member_queryset for %s" % str(self.__class__))
            else:
                self._members_field = field
        else:
            field = self._members_field
        if isinstance(field, models.ManyToManyField) and issubclass(field.rel.to, User):
            return self.members.all()
        else:
            raise NotImplementedError("You must define a member_queryset for %s" % str(self.__class__))
    
    def user_is_member(self, user):
        return user in self.member_queryset()
    
    def _group_gfk_field(self, model):
        return [f for f in model._meta.virtual_fields if f.name == "group"][0]
    
    def content_objects(self, model, join=None):
        queryset = _get_queryset(model)
        content_type = ContentType.objects.get_for_model(self)
        group_gfk = self._group_gfk_field(model)
        if join:
            lookup_kwargs = {
                "%s__%s" % (join, group_gfk.fk_field): self.id,
                "%s__%s" % (join, group_gfk.ct_field): content_type,
            }
        else:
            lookup_kwargs = {
                group_gfk.fk_field: self.id,
                group_gfk.ct_field: content_type,
            }
        content_objects = queryset.filter(**lookup_kwargs)
        return content_objects
    
    def associate(self, instance, commit=True):
        group_gfk = self._group_gfk_field(instance)
        setattr(instance, group_gfk.fk_field, self.id)
        setattr(instance, group_gfk.ct_field, ContentType.objects.get_for_model(self))
        if commit:
            instance.save()
        return instance
    
    def get_url_kwargs(self):
        kwargs = {}
        if self.group:
            kwargs.update(self.group.get_url_kwargs())
        slug = getattr(self, self.slug_attr)
        kwargs.update({"%s_slug" % self._meta.object_name.lower(): slug})
        return kwargs


class Group(GroupBase, GroupAware):
    """
    a group is a group of users with a common interest
    """
    
    slug = models.SlugField(_("slug"), unique=True)
    name = models.CharField(_("name"), max_length=80, unique=True)
    creator = models.ForeignKey(User, verbose_name=_("creator"), related_name="%(class)s_created")
    created = models.DateTimeField(_("created"), default=datetime.datetime.now)
    description = models.TextField(_("description"))
    
    def __unicode__(self):
        return self.name
    
    class Meta(object):
        abstract = True


class GroupScopedId(models.Model):
    """
    a model to store scoped IDs for tasks (specific to a group)
    """
    
    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.IntegerField(null=True, blank=True)
    group = generic.GenericForeignKey()
    
    scoped_number = models.IntegerField()
    
    class Meta:
        abstract = True
        unique_together = (("content_type", "object_id", "scoped_number"),)
