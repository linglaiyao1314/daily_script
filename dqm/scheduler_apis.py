"""
调度系统相关API:
 新用户创建逻辑:
     1. 创建新用户同名项目
 用户工作流创建与上线流程：
    1. 用户账号模拟登陆
    2. 在同名项目中创建工作流, 创建前验证，确保工作流唯一
    3. 上线工作流
    4. 创建定时任务
    5. 上线定时任务
    6. 验证执行逻辑
 工作流下线、更新流程:
    1. 用户模拟登陆
    2. 下线项目定时任务
    3. 下线项目
    4. 更新项目
    5. 执行上线流程
"""
import requests
import json
import functools

from loguru import logger

logger.add("api_manager.log", backtrace=True, diagnose=True, rotation="500 MB")

DEBUG = True


# 减少重复代码
def route(path, method="get", prefix="/dolphinscheduler"):
    def wrapped(func):
        @functools.wraps(func)
        def wrap(*args, **kwargs):
            # 获取self对象
            obj = args[0]
            assert method.lower() in ["get", "post"], ValueError(f"{method} is not allow")
            host = obj.host
            url = f"{host}{prefix}{path}".format(**kwargs)
            call = functools.partial(getattr(obj.session, method), url=url, headers=obj.headers)
            resp = func(call=call, *args, **kwargs)
            if DEBUG:
                logger.debug(f"[{method}->{path}] {resp['msg']}")
            return resp["data"]
        return wrap
    return wrapped


def project_route(path, method="get"):
    return route(path, method=method, prefix="/dolphinscheduler/projects")


class DolphinApiManager:
    def __init__(self, host, username, password):
        self.__session = requests.Session()
        self.__host = host
        self.__username = username
        self.__password = password
        self.__useful_data = {}
        res = self.init_login_info()
        if res is None:
            raise ValueError("login error")
        self.init_user_info()

    @property
    def headers(self):
        return {"content-type": "application/x-www-form-urlencoded"}

    @property
    def useful_data(self):
        return self.__useful_data

    @property
    def host(self):
        return self.__host

    @property
    def session(self):
        return self.__session

    @property
    def username(self):
        return self.__username

    @property
    def password(self):
        return self.__password

    # =======================
    # 用户信息
    # =======================
    @route("/login", method="post")
    def init_login_info(self, call):
        return call(params={"userName": self.username, "userPassword": self.password}).json()

    @route("/users/get-user-info", method="get")
    def init_user_info(self, call):
        resp = call().json()
        if resp["code"] == 0:
            self.__useful_data.update(resp["data"])
        return resp

    # ========================
    # 项目相关API
    # ========================
    @project_route(f"/create", method="post")
    def create_project(self, call, *, project_name, description=None):
        if description is None:
            description = project_name
        resp = call(params={"description": description, "projectName": project_name}).json()
        if resp["code"] != 0:
            return {"msg": resp["msg"], "data": False}
        return {"msg": resp["msg"], "data": True}

    @project_route(f"/list-paging", method="get")
    def get_project_info(self, call, *, project_name):
        params = {
            "pageNo": 1,
            "pageSize": 1,
            "searchVal": project_name
        }
        resp = call(params=params).json()
        if resp["code"] != 0 or len(resp["data"]["totalList"]) == 0:
            return {"msg": resp["msg"], "data": {}}
        return {"msg": resp["msg"], "data": resp["data"]["totalList"][0]}

    # ========================
    # 工作流相关API
    # ========================
    @project_route("/{project_name}/process/save", method="post")
    def create_workflow(self, call, *, project_name,
                        workflow_name: str,
                        definition: dict = None):
        if definition is None:
            definition = {}
        locations = {}
        for task in definition.get("tasks", []):
            locations.update({
                task["id"]: {"name": workflow_name,
                             "targetarr": "",
                             "x": 469,
                             "y": 166}
            })
        params = {
            "processDefinitionJson": json.dumps(definition),
            "name": workflow_name,
            "description": workflow_name,
            "locations": json.dumps(locations),
            "connects": json.dumps([])
        }
        resp = call(params=params).json()
        if resp["code"] != 0:
            return {"msg": resp["msg"], "data": False}
        return {"msg": resp["msg"], "data": True}

    @project_route("/{project_name}/process/update", method="post")
    def update_workflow(self, call, *, project_name, process_id, workflow_name, definition: dict):
        locations = {}
        for task in definition.get("tasks", []):
            locations.update({
                task["id"]: {"name": workflow_name,
                             "targetarr": "",
                             "x": 469,
                             "y": 166}
            })
        params = {
            "processDefinitionJson": json.dumps(definition),
            "name": workflow_name,
            "description": workflow_name,
            "locations": json.dumps(locations),
            "connects": json.dumps([]),
            "id": process_id,
            "projectName": project_name
        }
        resp = call(params=params).json()
        if resp["code"] != 0:
            return {"msg": resp["msg"], "data": False}
        return {"msg": resp["msg"], "data": True}

    @project_route("/{project_name}/process/list-paging", method="get")
    def get_workflow_info(self, call, *, project_name, workflow_name):
        params = {"pageNo": 1,
                  "pageSize": 1,
                  "searchVal": workflow_name,
                  "projectName": project_name,
                  "userId": self.useful_data["id"]}
        resp = call(params=params).json()
        if resp["code"] != 0 or len(resp["data"]["totalList"]) == 0:
            return {"msg": resp["msg"], "data": {}}
        return {"msg": resp["msg"], "data": resp["data"]["totalList"][0]}

    @project_route("/{project_name}/process/release", method="post")
    def release_workflow(self, call, *, project_name: str, process_id: int, release_type: int):
        params = {
            "processId": process_id,
            "releaseState": release_type,
        }
        resp = call(params=params).json()
        if resp["code"] != 0:
            return {"msg": resp["msg"], "data": False}
        return {"msg": resp["msg"], "data": True}

    @project_route("/{project_name}/process/verify-name", method="get")
    def is_exists_workflow_name(self, call, *, project_name: str, workflow_name):
        params = {
            "name": workflow_name,
            "projectName": project_name,
        }
        resp = call(params=params).json()
        # 存在，则名称验证不通过
        if resp["code"] != 0:
            return {"msg": resp["msg"], "data": True}
        return {"msg": resp["msg"], "data": False}

    # ========================
    # 定时任务相关API
    # ========================
    @project_route("/{project_name}/schedule/preview", method="post")
    def preview_schedule(self, call, *, project_name: str, schedule: dict):
        params = {
            "projectName": project_name,
            "schedule": json.dumps(schedule),
        }
        resp = call(params=params).json()
        if resp["code"] != 0:
            return {"msg": resp["msg"], "data": []}
        return {"msg": resp["msg"], "data": resp["data"]}

    @project_route("/{project_name}/schedule/create", method="post")
    def create_schedule(self, call, *, project_name: str, process_id: int, schedule: dict):
        params = {
            "processDefinitionId": process_id,
            "failureStrategy": "CONTINUE",
            "warningType": None,
            "processInstancePriority": "MEDIUM",
            "warningGroupId": 0,
            "workerGroupId": -1,
            "receivers": "",
            "receiversCc": "",
            "schedule": json.dumps(schedule),
        }
        resp = call(params=params).json()
        return {"msg": resp["msg"], "data": resp["data"]}

    @project_route("/{project_name}/schedule/update", method="post")
    def update_schedule(self, call, *, project_name: str, process_id: int, schedule_id: int, schedule: dict):
        params = {
            "id": schedule_id,
            "processDefinitionId": process_id,
            "failureStrategy": "CONTINUE",
            "warningType": None,
            "processInstancePriority": "MEDIUM",
            "warningGroupId": 0,
            "workerGroupId": -1,
            "receivers": "",
            "receiversCc": "",
            "schedule": json.dumps(schedule),
        }
        resp = call(params=params).json()
        if resp["code"] != 0:
            return {"msg": resp["msg"], "data": resp["data"]}
        return {"msg": resp["msg"], "data": resp["data"]}

    @project_route("/{project_name}/schedule/list-paging", method="get")
    def get_schedule(self, call, *, project_name: str, process_id: int):
        params = {
            "processDefinitionId": process_id,
            "projectName": project_name,
            "pageNo": 1,
            "pageSize": 1,
        }
        resp = call(params=params).json()
        if resp["code"] != 0 or len(resp["data"]["totalList"]) == 0:
            return {"msg": resp["msg"], "data": {}}
        return {"msg": resp["msg"], "data": resp["data"]["totalList"][0]}

    @project_route("/{project_name}/schedule/online", method="post")
    def online_schedule(self, call, *, project_name: str, schedule_id: int):
        params = {
            "id": schedule_id,
            "projectName": project_name,
        }
        resp = call(params=params).json()
        if resp["code"] != 0:
            return {"msg": resp["msg"], "data": False}
        return {"msg": resp["msg"], "data": True}

    @project_route("/{project_name}/schedule/offline", method="post")
    def offline_schedule(self, call, *, project_name: str, schedule_id: int):
        params = {
            "id": schedule_id,
            "projectName": project_name,
        }
        resp = call(params=params).json()
        if resp["code"] != 0:
            return {"msg": resp["msg"], "data": False}
        return {"msg": resp["msg"], "data": True}

    # ========================
    # 流程实例执行相关API
    # ========================
    @project_route("/{project_name}/executors/start-process-instance", method="post")
    def start_process_instance(self, call, *, project_name, process_id: int):
        params = {
            "processDefinitionId": process_id,
            "failureStrategy": "END",
            "warningType": "NONE",
            "scheduleTime": "",
            "warningGroupId": 0,
            "taskDependType": "TASK_POST",
            "runMode": "RUN_MODE_SERIAL",
            "workerGroupId": -1,
            "processInstancePriority": "MEDIUM",

        }
        resp = call(params=params).json()
        if resp["code"] != 0:
            return {"msg": resp["msg"], "data": False}
        return {"msg": resp["msg"], "data": True}

