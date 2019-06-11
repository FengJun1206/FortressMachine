# 独立运行的脚步

import sys, os, json
import time, socket
from concurrent.futures import ThreadPoolExecutor
import paramiko


def ssh_cmd(sub_task_obj):
    print('sub_task_obj', sub_task_obj)  # sub_task_obj cmd ifconfig test root: 123
    # 远程主机对象
    host_to_user_obj = sub_task_obj.host_to_remote_user

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    try:
        ssh.connect(
            hostname=host_to_user_obj.host.ip_addr,
            port=host_to_user_obj.host.port,
            username=host_to_user_obj.remote_user.username,
            password=host_to_user_obj.remote_user.password,
            timeout=5)
        # # sub_task_obj.task.content 为命令本身， 如：df、ls 等
        stdin, stdout, stderr = ssh.exec_command(sub_task_obj.task.content)
        stdout_res = (stdout.read()).decode(encoding='utf-8')
        stderr_res = (stderr.read()).decode(encoding='utf-8')

        # 子任务结果由命令标准输出和错误组成
        sub_task_obj.result = stderr_res + stdout_res
        print('-----------result------------')
        print('+++++', stdout_res, type(stderr_res), stderr_res, type(stderr_res))
        print(sub_task_obj.result)

        # 如果有错误，则将状态修改为失败，即命令执行失败，否则为成功
        if stderr_res:
            sub_task_obj.status = 2
        else:
            sub_task_obj.status = 1
    except Exception as e:
        sub_task_obj.result = e
        sub_task_obj.status = 2
    sub_task_obj.save()  # 保存


def file_transfer(sub_task_obj, task_data):
    """
    文件分发
    :param sub_task_obj:
    :param task_data: {'selected_host_ids': ['4', '6'], 'task_type': 'file_transfer', "file_transfer_type": "send", 'local_file_path': 'C:/Users/hj/Desktop/1.jpg', 'remote_file_path': '/home/hj/1.jpg'}
    :return:
    """
    print('sub_task_obj', sub_task_obj, task_data)
    host_to_user_obj = sub_task_obj.host_to_remote_user

    local_file_path = task_data.get('local_file_path')  # 本地文件路径
    remote_file_path = task_data.get('remote_file_path')  # 远程文件路径
    ip_addr = host_to_user_obj.host.ip_addr  # 远程主机 IP 地址       # type: str
    port = host_to_user_obj.host.port  # 远程主机端口
    username = host_to_user_obj.remote_user.username  # 远程主机账户
    password = host_to_user_obj.remote_user.password  # 远程主机密码

    try:
        t = paramiko.Transport((ip_addr, port))
        t.connect(username=username, password=password)

        sftp = paramiko.SFTPClient.from_transport(t)

        # send 为发送，get 为下载
        if task_data.get('file_transfer_type') == 'send':
            sftp.put(local_file_path, remote_file_path)

            result = '本地 [%s] 文件发送到远程主机 [%s] 发送成功' % (local_file_path, remote_file_path)

        else:  # 下载保存到本地 download 文件夹中
            # 'E:\\Python_virtualenvs\\for_django\\Projects\\FortressMachine\\download\\44'
            upload_file_path = os.path.join(conf.settings.TASK_DOWNLOADS_DIRS, str(task_obj.id))
            if not os.path.isdir(upload_file_path):
                os.mkdir(upload_file_path)

            # 'remote_file_path': '/home/hj/1.jpg'
            file_name = '%s-%s' % (ip_addr, remote_file_path.split('/')[-1])     # '192.168.21.128-1.jpg'

            # 最终存储路径
            download_path = os.path.join(upload_file_path, file_name)
            sftp.get(remote_file_path, download_path)

            result = '从远程主机 [%s] 下载成功' % remote_file_path

        t.close()
        sub_task_obj.status = 1
    except Exception as e:
        print('-----------> e', e)
        sub_task_obj.status = 2
        result = e

    sub_task_obj.result = result
    sub_task_obj.save()


if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(base_dir)  # 加入到系统环境变量中

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "FortressMachine.settings")
    import django

    django.setup()
    from django import conf
    from web import models

    # python3 task_runner.py 1
    if len(sys.argv) == 1:
        exit('没有提供任务 ID')
    task_id = sys.argv[1]  # 1 、2 、3、 4
    task_obj = models.Task.objects.get(id=task_id)
    print('task running', task_obj)  # cmd ifconfig

    # 创建 10 个线程
    pool = ThreadPoolExecutor(10)
    # 批量命令
    if task_obj.task_type == 'cmd':
        for sub_task_obj in task_obj.taskdetail_set.all():
            # sub_task_obj：taskdetail 对象
            pool.submit(ssh_cmd, sub_task_obj)
    else:
        # 文件传输
        task_data = json.loads(task_obj.content)
        for sub_task_obj in task_obj.taskdetail_set.all():
            pool.submit(file_transfer, sub_task_obj, task_data)
    pool.shutdown(wait=True)
