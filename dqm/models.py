from peewee import *
from playhouse.mysql_ext import MySQLConnectorDatabase

# MySQL database implementation that utilizes mysql-connector driver.
db = MySQLConnectorDatabase('xxxx',
                            host='xxxx',
                            user='xxxx',
                            password="xxx")


class User(Model):
    id = AutoField()
    uid = IntegerField()
    email = CharField()
    gender = IntegerField(default=1)
    mobile = IntegerField(null=True)
    real_name = CharField()
    status = IntegerField(default=1)
    create_time = DateTimeField()
    update_time = DateTimeField()
    name = CharField()
    password = CharField(default="")

    class Meta:
        database = db
        table_name = "user"


class UserScheduler(Model):
    id = AutoField()
    user_id = IntegerField()
    scheduler_username = CharField()
    scheduler_password = CharField()
    scheduler_project_id = IntegerField()
    scheduler_project_name = CharField()
    create_time = DateTimeField()
    update_time = DateTimeField()

    class Meta:
        database = db
        table_name = "user_scheduler"


class UserWorkflow(Model):
    id = AutoField()
    user_id = IntegerField()
    scheduler_project_id = IntegerField()
    scheduler_project_name = CharField()
    workflow_definition = TextField(default="")
    workflow_name = CharField()
    workflow_id = IntegerField()
    workflow_status = IntegerField()
    create_time = DateTimeField()
    update_time = DateTimeField()

    class Meta:
        database = db
        table_name = "user_workflow"
