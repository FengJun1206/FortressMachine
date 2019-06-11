from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import authenticate, login, logout
from backend.multitask import TaskHandler
import json
from web import models
from django.contrib.auth.decorators import login_required


@login_required
def dashboard(request):
    return render(request, 'index.html')


@login_required
def web_ssh(request):
    return render(request, 'web_ssh.html')


@login_required
def host_list(request):
    """主机列表"""
    return render(request, 'host_list.html')


@login_required
def batch_task(request):
    """处理前端提交过来的命令"""
    # selected_ids = request.POST.get_list()
    # print(request.POST)

    task_obj = TaskHandler(request)
    task_obj.task_parser()

    # 获取主任务 id，在 multitask.py 中，赋值 self.task_obj = task_obj，self 为 TaskHandler() 实例对象即 task_obj
    task_id = task_obj.task_obj.id

    # 已选择的主机列表
    selected_hosts = list(task_obj.task_obj.taskdetail_set.all().values(
        'id',
        'host_to_remote_user__host__ip_addr',
        'host_to_remote_user__host__name',
        'host_to_remote_user__remote_user__username'
    ))

    response = {
        'task_id': task_id,
        'selected_hosts': selected_hosts
    }
    return HttpResponse(json.dumps(response))


@login_required
def get_task_result(request):
    """接收前端发送过来的 ajax 请求，从数据库中取出批量命令执行结果并返回"""
    task_id = request.GET.get('task_id')
    print('task_id', task_id)

    # 批量命令执行结果
    task_detail_list = list(models.TaskDetail.objects.filter(task_id=task_id).values(
        'id',
        'result',
        'status'
    ))

    print('------------>', task_detail_list)
    return HttpResponse(json.dumps(task_detail_list))


@login_required
def file_transfer(request):
    """文件传输"""

    return render(request, 'file_transfer.html')


@login_required
def host_result_history(request):
    # data_list = []
    # task_obj = request.user.task_set.all()
    # for taskdetai_obj in task_obj:
    #     data_list.append(taskdetai_obj.taskdetail_set.all())
    #
    # print('data_list', data_list)
    task_detail_list = models.TaskDetail.objects.all()
    # print('task_detail_list', task_detail_list)

    return render(request, 'host_result_history.html', locals())


@login_required
def audit_log(request):
    """审计日志"""
    audit_log_list = models.AuditLog.objects.all()

    return render(request, 'audit_log.html', locals())


def account_login(request):
    """登录"""
    error_msg = ''

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect('/')
        else:
            error_msg = '用户名或密码错误'

    return render(request, 'account_login.html', {'error_msg': error_msg})


def account_logout(request):
    logout(request)
    return redirect('account_login')

