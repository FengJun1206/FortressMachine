# from backend import main
# import os, sys
#
# if __name__ == '__main__':
#     os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FortressMachine.settings')
#     import django
#     django.setup()
#
#     obj = main.ArgvHander(sys.argv)
#     obj.call()


import sys, os


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "FortressMachine.settings")
    import django
    django.setup()

    from backend import main
    interactive_obj = main.ArgvHander(sys.argv)
    interactive_obj.call()


