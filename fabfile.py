from fabric.api import *

env.hosts = ['10.0.1.3']
@parallel
def uname():
    run('uname -a')

def prepare_deploy():
    local('git push')

def reload():
    run('touch /etc/uwsgi/uwsgi_vassals/show.eggmen.net/uwsgi.xml')

def pull():
    prepare_deploy()
    with cd('/home/igor/store'):
        run('git pull')

def migrate():
    pull()
    with cd('/home/igor/store'):
        with prefix('source /home/igor/.py_env/bin/activate'):
            run('python manage.py migrate')
    reload()

def upgrade():
    pull()
    reload()
