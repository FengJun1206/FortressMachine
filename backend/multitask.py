import json
from web import models
from django import conf
import subprocess


class TaskHandler:
    """命令处理"""
    def __init__(self, request):
        self.request = request

    def task_parser(self):
        """命令解析"""
        # 批量命令：task_data = {'selected_host_ids': ['3', '2'], 'task_type': 'cmd', 'cmd': 'ifconfig'}
        # 文件传输：task_data = {'selected_host_ids': ['4', '6'], 'task_type': 'file_transfer', "file_transfer_type": "send", 'local_file_path': 'C:/Users/hj/Desktop/1.jpg', 'remote_file_path': '/home/hj/1.jpg'}
        self.task_data = json.loads(self.request.POST.get('task_data'))
        task_type = self.task_data.get('task_type')
        print('self.task_data', self.task_data)

        if hasattr(self, task_type):
            task_func = getattr(self, task_type)        # self 是 类 TaskHandler的实例对象， task_type：cmd，即判断类中是否有 cmd 这个方法
            task_func()         # cmd()、file_transfer()
        else:
            print('没有发现任务', task_type)

    def cmd(self):
        """
        命令调用，批量命令
        1、生成任务在数据库中记录， 拿到任务 id
        2、触发任务，不阻塞，搞一个新的进程， 新的线程不行，还是要等线程结束才能继续往下执行
        3、返回任务 id 给前端
        :return:
        """

        task_obj = models.Task.objects.create(
            task_type=self.task_data.get('task_type'),
            content=self.task_data.get('cmd'),
            user=self.request.user
        )

        selected_host_ids = set(self.task_data.get('selected_host_ids'))

        task_log_obj = []

        for id in selected_host_ids:
            task_log_obj.append(
                models.TaskDetail(task=task_obj, host_to_remote_user_id=id, result='init...')
            )

        # 批量创建 bulk_create()
        models.TaskDetail.objects.bulk_create(task_log_obj)

        # task_runner.py 为一个独立运行的脚步程序， 它与主进程无关系，为一个新的进程
        # python3 E:\Python_virtualenvs\for_django\Projects\FortressMachine/backend/task_runner.py 12
        #  , 执行命令，这里是将主任务的 id 作为参数执行并返回给子任务
        task_script = 'python3 %s/backend/task_runner.py %s' % (conf.settings.BASE_DIR, task_obj.id)

        # subprocess 模块的 Popen() 方法用于执行复杂的 shell 命令， shell=True 表示命令可为字符串
        cmd_process = subprocess.Popen(task_script, shell=True)

        print('开始执行批量命令....')
        # 赋值
        self.task_obj = task_obj

    def file_transfer(self):
        """文件分发"""
        task_obj = models.Task.objects.create(
            task_type=self.task_data.get('task_type'),
            content=json.dumps(self.task_data),     # 这里为啥要序列化一下？
            user=self.request.user
        )

        selected_host_ids = set(self.task_data.get('selected_host_ids'))

        task_log_obj = []

        for id in selected_host_ids:
            task_log_obj.append(
                models.TaskDetail(task=task_obj, host_to_remote_user_id=id, result='init...')
            )

        # 批量创建 bulk_create()
        models.TaskDetail.objects.bulk_create(task_log_obj)

        # task_runner.py 为一个独立运行的脚步程序， 它与主进程无关系，为一个新的进程
        # python3 E:\Python_virtualenvs\for_django\Projects\FortressMachine/backend/task_runner.py 12
        #  , 执行命令，这里是将主任务的 id 作为参数执行并返回给子任务
        task_script = 'python3 %s/backend/task_runner.py %s' % (conf.settings.BASE_DIR, task_obj.id)

        # subprocess 模块的 Popen() 方法用于执行复杂的 shell 命令， shell=True 表示命令可为字符串
        cmd_process = subprocess.Popen(task_script, shell=True)

        print('开始执行批量文件....')
        # 赋值
        self.task_obj = task_obj