import datetime
import random
import json

from loguru import logger

from dqm.scheduler_apis import DolphinApiManager
from dqm.models import UserScheduler, UserWorkflow, User

logger.add("dqm_client.log", backtrace=True, diagnose=True, rotation="500 MB")


class Task:
    def __init__(self, task_name, task_type="SHELL"):
        self.__info = {
            "name": task_name,
            "type": task_type,
            "id": f"tasks-{int(random.random() * 10000)}",
            "description": f"to run {task_name}",
            "runFlag": "NORMAL",
            "dependence": {},
            "maxRetryTimes": "0",
            "retryInterval": "1",
            "timeout": {"strategy": "",
                        "interval": None,
                        "enable": False},
            "taskInstancePriority": "MEDIUM",
            "workerGroupId": -1, "preTasks": [],
            "params": {}

        }
        self.__resource_list = []
        self.__local_params = []

    @property
    def resource_list(self):
        return self.__resource_list

    def add_resource(self, resource_name):
        self.__resource_list.append({"res": resource_name})
        return self

    def add_local_params(self, key, value):
        self.__local_params.append({
            "prop": key,
            "direct": "IN",
            "type": "VARCHAR",
            "value": value
        })
        return self

    def add_script(self, script):
        self.__info["params"].update({"rawScript": script})
        return self

    def generate_task_definition(self):
        self.__info["params"].update({
            "resourceList": self.__resource_list,
            "localParams": self.__local_params,
        })
        return self.__info


class WorkFlowDefinition:
    def __init__(self, tasks):
        self.__definition = {
            "tenantId": -1,
            "timeout": 0,
            "globalParams": [],
            "tasks": tasks
        }

    @property
    def definition(self):
        return self.__definition


class DQMClient:
    def __init__(self, username, user_id, apis: DolphinApiManager):
        self.__user_id = user_id
        self.__user_name = username
        # todo ensure username and user_id exists
        self.__project_name = f"{self.user_name}_{self.user_id}"
        self.__apis = apis

    @property
    def project_name(self):
        return self.__project_name

    @property
    def user_name(self):
        return self.__user_name

    @property
    def user_id(self):
        return self.__user_id

    @property
    def apis(self):
        return self.__apis

    def get_or_create_user_scheduler(self) -> UserScheduler:
        project_name = self.project_name
        if not self.apis.get_project_info(project_name=project_name):
            self.apis.create_project(project_name=project_name)
        project_info = self.apis.get_project_info(project_name=project_name)
        project_id = project_info["id"]
        rows = UserScheduler.select().where(UserScheduler.scheduler_project_id == project_id).limit(1)
        if len(rows) == 0:
            logger.debug(f"Create new project: {project_name}")
            user_scheduler = UserScheduler()
            user_scheduler.user_id = self.user_id
            user_scheduler.create_time = datetime.datetime.now()
            user_scheduler.update_time = datetime.datetime.now()
            user_scheduler.scheduler_project_name = project_name
            user_scheduler.scheduler_username = self.apis.username
            user_scheduler.scheduler_password = self.apis.password
            user_scheduler.scheduler_project_id = project_id
            user_scheduler.save()
            return user_scheduler
        else:
            return rows[0]

    def create_workflow(self, workflow_name, wfd: WorkFlowDefinition):
        project_name = self.project_name
        if self.apis.is_exists_workflow_name(project_name=project_name,
                                             workflow_name=workflow_name):
            workflow_info = self.apis.get_workflow_info(project_name=project_name,
                                                        workflow_name=workflow_name)
        else:
            success = self.apis.create_workflow(project_name=project_name,
                                                workflow_name=workflow_name,
                                                definition=wfd.definition)
            if not success:
                logger.error(f"Workflow {workflow_name} create error")
                return {}
            workflow_info = self.apis.get_workflow_info(project_name=project_name, workflow_name=workflow_name)
        user_scheduler = UserScheduler.select().where(UserScheduler.scheduler_project_name == project_name).get()
        rows = UserWorkflow.select().where(UserWorkflow.workflow_id == workflow_info["id"]).limit(1)
        if len(rows) == 0:
            logger.debug(f"Create new workflow: {workflow_name}")
            user_workflow = UserWorkflow()
            user_workflow.user_id = self.user_id
            user_workflow.create_time = datetime.datetime.now()
            user_workflow.update_time = datetime.datetime.now()
            user_workflow.workflow_id = workflow_info["id"]
            user_workflow.workflow_name = workflow_name
            user_workflow.workflow_definition = json.dumps(wfd.definition)
            user_workflow.workflow_status = 0
            user_workflow.scheduler_project_id = user_scheduler.scheduler_project_id
            user_workflow.scheduler_project_name = project_name
            user_workflow.save()
            return user_workflow
        else:
            return rows[0]

    def update_workflow(self, workflow_name, wfd: WorkFlowDefinition):
        if not self.apis.is_exists_workflow_name(project_name=self.project_name, workflow_name=workflow_name):
            return
        workflow_info = self.apis.get_workflow_info(project_name=self.project_name,
                                                    workflow_name=workflow_name)
        self.apis.update_workflow(project_name=self.project_name, process_id=workflow_info["id"], workflow_name=workflow_name,
                                  definition=wfd.definition)
        rows = UserWorkflow.select().where(UserWorkflow.workflow_id == workflow_info["id"]).limit(1)
        if len(rows) == 1:
            logger.debug(f"Update new workflow: {workflow_name}")
            user_workflow = rows[0]
            user_workflow.update_time = datetime.datetime.now()
            user_workflow.workflow_definition = json.dumps(wfd.definition)
            user_workflow.workflow_status = 0
            user_workflow.save()
            return user_workflow

    def run_workflow(self, workflow_name):
        workflow_info = self.apis.get_workflow_info(project_name=self.project_name,
                                                    workflow_name=workflow_name)
        if len(workflow_info) == 0:
            logger.error(f"Workflow can't run: {workflow_name}")
            return
        self.apis.release_workflow(project_name=self.project_name,
                                   process_id=workflow_info["id"],
                                   release_type=1)
        running = self.apis.start_process_instance(project_name=self.project_name,
                                                   process_id=workflow_info["id"])
        logger.info(f"run {workflow_name} status is {running}")

    def update_schedule(self, process_id, schedule):
        old_schedule = self.apis.get_schedule(project_name=self.project_name,
                                              process_id=process_id)
        if old_schedule:
            logger.debug(f"Update schedule: {schedule}")
            schedule_id = old_schedule["id"]
            # 先下线,再更新
            self.apis.offline_schedule(project_name=self.project_name,
                                       schedule_id=schedule_id)
            self.apis.update_schedule(project_name=self.project_name,
                                      process_id=process_id,
                                      schedule_id=schedule_id,
                                      schedule=schedule)
        else:
            logger.debug(f"Create schedule: {schedule}")
            self.apis.create_schedule(project_name=self.project_name,
                                      process_id=process_id,
                                      schedule=schedule)
        new_schedule = self.apis.get_schedule(project_name=self.project_name,
                                              process_id=process_id)
        self.apis.online_schedule(project_name=self.project_name,
                                  schedule_id=new_schedule["id"])
        return new_schedule

    def get_workflow_schedule(self, workflow_name):
        workflow_info = self.apis.get_workflow_info(project_name=self.project_name,
                                                    workflow_name=workflow_name)
        schedule_info = self.apis.get_schedule(project_name=self.project_name,
                                               process_id=workflow_info["id"])
        schedule = {
            "startTime": schedule_info["startTime"],
            "endTime": schedule_info["endTime"],
            "crontab": schedule_info["crontab"]
        }
        return self.apis.preview_schedule(project_name=self.project_name,
                                          schedule=schedule)


def create_count_task(task_name: str, tables: str):
    task = Task(task_name)
    return task.add_script("""echo "start run"
/root/anaconda3/bin/python rows_monitor.py count-monitor --tables ${tables}  --minutes ${minutes} --notify_emails ${emails} --db_setting ${setting}
echo "run over" """). \
        add_resource("rows_monitor.py"). \
        add_resource("command_settings.yml"). \
        add_local_params("tables", tables). \
        add_local_params("minutes", 120). \
        add_local_params("emails", "yaohaohua@innotechx.com"). \
        add_local_params("setting", "orion_tidb").generate_task_definition()
