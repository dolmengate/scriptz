import os
import argparse
from pathlib import Path
from sys import exit


def main():
    parser = argparse.ArgumentParser(description='Create a boot.properties file to enable unattended startups of '
                                                 'WebLogic.')
    parser.add_argument('username', help='WebLogic admin username.')
    parser.add_argument('password', help='WebLogic admin password.')
    ns = parser.parse_args()

    bp_path = os.path.join('C:', os.sep, 'Oracle', 'Middleware', 'user_projects', 'domains', 'fffo_bo', 'servers',
                           'AdminServer', 'security')
    try:
        Path(bp_path).mkdir(parents=True)
    except FileExistsError:
        print('Directory already exists, continue?')
        cont = input('y/n\n')
        if cont == 'y':
            Path(bp_path).mkdir(parents=True, exist_ok=True)
        else:
            exit(0)

    with open(os.path.join(bp_path, 'boot.properties'), 'w') as bp:
        bp.writelines([f'username={ns.username}\n', f'password={ns.password}'])


if __name__ == '__main__':
    main()
