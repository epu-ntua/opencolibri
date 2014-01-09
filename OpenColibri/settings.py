import sys
import os

this_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.abspath(this_path + '/configs')) # add xtreme to our path

from settings_local import *

try:
    with open('configs/application.id', 'r+') as f:
        APPLICATION_ENV = f.read()
except IOError as e:
    APPLICATION_ENV = 'production'

if APPLICATION_ENV == 'development':
    from settings_development import *
elif APPLICATION_ENV == 'mpetyx':
    from settings_mpetyx import *
elif APPLICATION_ENV == 'production':
    from settings_production import *