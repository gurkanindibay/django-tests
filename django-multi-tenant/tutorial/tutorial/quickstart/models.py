from django.db import models

# Create your models here.
from django.contrib.auth.models import User

import uuid

from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver


from django_multitenant.mixins import TenantModelMixin, TenantManagerMixin
from django_multitenant.models import TenantModel
from django_multitenant.fields import TenantForeignKey


class Country(models.Model):
    name = models.CharField(max_length=255)


class Account(TenantModel):
    name = models.CharField(max_length=255)
    domain = models.CharField(max_length=255)
    subdomain = models.CharField(max_length=255)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    # TODO change to Meta
    tenant_id = "id"

    def __str__(self):
        return "{}".format(self.name)




class ModelConfig(TenantModel):
    name = models.CharField(max_length=255)
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="configs"
    )

    tenant_id = "account_id"
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['id', 'account_id'], name='unique_modelconfig_account')
        ]


class Manager(TenantModel):
    name = models.CharField(max_length=255)
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="managers"
    )
    tenant_id = "account_id"
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['id', 'account_id'], name='unique_manager_account')
        ]


class Project(TenantModel):
    name = models.CharField(max_length=255)
    account = models.ForeignKey(
        Account, related_name="projects", on_delete=models.CASCADE
    )
    managers = models.ManyToManyField(Manager, through="ProjectManager")
    tenant_id = "account_id"
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['id', 'account_id'], name='unique_project_account')
        ]


    def __str__(self):
        return "{} ({})".format(self.name, self.account)


class ProjectManager(TenantModel):
    project = TenantForeignKey(
        Project, on_delete=models.CASCADE, related_name="projectmanagers"
    )
    manager = TenantForeignKey(Manager, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)

    tenant_id = "account_id"



class TaskQueryset(models.QuerySet):
    def opened(self):
        return self.filter(opened=True)

    def closed(self):
        return self.filter(opened=False)


class TaskManager(TenantManagerMixin, models.Manager):
    _queryset_class = TaskQueryset

    def opened(self):
        return self.get_queryset().opened()

    def closed(self):
        return self.get_queryset().closed()


class Task(TenantModelMixin, models.Model):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    opened = models.BooleanField(default=True)

    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, db_index=False, blank=True, null=True
    )

    objects = TaskManager()

    tenant_id = "account_id"
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['id', 'account_id'], name='unique_task_account')
        ]



    def __str__(self):
        return "{} ({})".format(self.name, self.project)


class SubTask(TenantModel):
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    task = TenantForeignKey(Task, on_delete=models.CASCADE)
    project = TenantForeignKey(Project, on_delete=models.CASCADE, null=True)

    tenant_id = "account_id"



class UnscopedModel(models.Model):
    name = models.CharField(max_length=255)


class AliasedTask(TenantModel):
    project_alias = TenantForeignKey(Project, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)

    tenant_id = "account_id"



class Revenue(TenantModel):
    # To test for correct tenant_id push down in query
    acc = models.ForeignKey(Account, on_delete=models.CASCADE)
    project = TenantForeignKey(
        Project, on_delete=models.CASCADE
    )
    value = models.CharField(max_length=30)

    tenant_id = "acc_id"



# Models for UUID tests
class Organization(TenantModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    tenant_id = "id"




class Record(TenantModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    tenant_id = "organization_id"


class TenantNotIdModel(TenantModel):
    tenant_column = models.IntegerField(primary_key=True, editable=False)
    name = models.CharField(max_length=255)

    tenant_id = "tenant_column"


class SomeRelatedModel(TenantModel):
    related_tenant = models.ForeignKey(TenantNotIdModel, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    tenant_id = "related_tenant_id"


class MigrationTestModel(TenantModel):
    name = models.CharField(max_length=255)
    tenant_id = "id"


class MigrationTestReferenceModel(models.Model):
    name = models.CharField(max_length=255)
