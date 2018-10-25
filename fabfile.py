from fabric import task

@task
def build(c):
    print("Fab Building!")
