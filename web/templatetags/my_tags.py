from django import template
from web import models
from django.utils.safestring import mark_safe


register = template.Library()

# user_obj = models.UserProfile.objects.get(name='hj')
# task_obj = user_obj.task_set.all()
# for t in task_obj:
#     res = t.taskdetail_set.all()
#     print(res)


@register.simple_tag
def get_taskdetail_content(taskdetail_obj):
    print('taskdetail_obj', taskdetail_obj, type(taskdetail_obj))

    task_type = taskdetail_obj.task.task_type

    if task_type == 'cmd':
        return taskdetail_obj.task.content
    else:
        """
        {"selected_host_ids": ["4"],
         "task_type": "file_transfer", "file_transfer_type": "send", 
         "local_file_path": "C:/Users/hj/Desktop/1.jpg", 
         "remote_file_path": "/home/hj/1.jpg"}
        """

        content = eval(taskdetail_obj.task.content)

        ele = """
            <ul><li>%s: %s</li>
        """ % ('文件传输方式', content.get('file_transfer_type'))

        # if content.get('file_transfer_type') == 'send':
        #     # li_ele1 = """<li>%s</li>""" % content.get('file_transfer_type')
        #     li_ele2 = """<li>%s</li>""" % content.get('local_file_path')
        #     li_ele3 = """<li>%s</li>""" % content.get('remote_file_path')
        # else:
        #     li_ele1 = "<li>" + content.get('local_file_path') + "</li>"
        #     li_ele2 = "<li>" + content.get('remote_file_path') + "</li>"

        if content.get('file_transfer_type') == 'send':
            li_ele2 = """<li>%s: %s</li>""" % ('本地路径', content.get('local_file_path'))
            li_ele3 = """<li>%s: %s</li>""" % ('远程路径', content.get('remote_file_path'))
            ele += li_ele2 + li_ele3
        else:
            li_ele3 = """<li>%s: %s</li>""" % ('远程路径', content.get('remote_file_path'))
            ele += li_ele3

        ele += "</ul>"
    return mark_safe(ele)



@register.simple_tag
def get_taskdetail_result(result):
    print('type', type(result))

    result = result.decode(encoding='utf-8')
    return result
