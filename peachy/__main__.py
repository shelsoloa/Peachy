import os
import sys


def startproject(project_name):
    project_dirs = [
        '/assets', '/assets/images', '/assets/sounds',
        '/build',
        '/game', '/game/entities', '/game/stages', '/game/worlds'
    ]

    print("Creating %s project..." % project_name)
    if not os.path.exists(project_name):
        os.makedirs(project_name)
        for subdir in project_dirs:
            os.makedirs(project_name + subdir)
    else:
        print("[ERROR] %s directory already exists" % project_name)


def main():
    command = sys.argv[1]
    if command == 'startproject':
        project_name = sys.argv[2]
        startproject(project_name)

if __name__ == '__main__':
    main()
