from fabric.api import *
from fabric.colors import green
import test
bold=True

env.hosts = ['10.0.1.3']
@task
@parallel
def uname():
    run('uname -a')

@task
def prepare_deploy():
    local('git push')

@task
def reload():
    run('touch /etc/uwsgi/uwsgi_vassals/show.eggmen.net/uwsgi.xml')

@task
def pull():
    prepare_deploy()
    with cd('/home/igor/store'):
        run('git pull')

@task
def migrate():
    with hide('running', 'stdout', 'stderr'):
        pull()
        with cd('/home/igor/store'):
            with prefix('source /home/igor/.py_env/bin/activate'):
                run('python manage.py migrate')
        reload()
    print(green('Done', bold))

@task
def syncdb():
    pull()
    with cd('/home/igor/store'):
        with prefix('source /home/igor/.py_env/bin/activate'):
            run('python manage.py syncdb')
    print(green('Done', bold))

@task
def upgrade():
    pull()
    reload()
