from subprocess import call

def reset():
    call(['jlink', 'reset.jlink'])

if __name__ == '__main__':
    reset()
