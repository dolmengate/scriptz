import subprocess
import argparse
import os
import fileinput


def main():
    parser = argparse.ArgumentParser(description='Edit .properties files within .jar files. Creates a backup file in '
                                                 'case something goes wrong.')
    parser.add_argument('jar', help='Path of the .jar that contains the .properties file you want to alter.')
    parser.add_argument('prop_file', help='File name of the .properties file you want to alter.')
    parser.add_argument('prop', help='Name of the property you want to alter within prop_file.')
    parser.add_argument('value', help='Value of the property you want to alter within prop_file. '
                                      'Backslashes will preserved (\'\\\')')

    ns = parser.parse_args()
    ns.value = ns.value.replace('\\', '\\\\')

    # check JAVA_HOME
    if 'jdk' not in os.environ["JAVA_HOME"]:
        print('WARNING: JAVA_HOME might not be set.')

    jar_cmd = f"{os.environ['JAVA_HOME']}\\bin\\jar"

    # extract file
    subprocess.run(f'{jar_cmd} xf {os.path.abspath(ns.jar)} {ns.prop_file}'.split())

    # edit file while preserving comments
    for line in fileinput.input(ns.prop_file, inplace=True, backup='.bkp'):
        if ns.prop in line and not line.startswith('#'):
            print(f'{ns.prop}={ns.value}')
        else:
            print(line, end='')

    # update jar
    subprocess.run(f'{jar_cmd} uf {ns.jar} {ns.prop_file} '.split())

    # delete the edited file that remains outside of the .jar
    os.remove(ns.prop_file)


if __name__ == '__main__':
    main()
