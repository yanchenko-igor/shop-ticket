from fabric.api import *

@task
def qwerty():
    local('uname -a')
