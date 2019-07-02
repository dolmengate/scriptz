import subprocess
import argparse
import os
import fileinput
import sys


def main():
    parser = argparse.ArgumentParser(description='Edit .properties files within .jar files. Creates a backup file in '
                                                 'case something goes wrong.')
    parser.add_argument('jar', help='Path of the .jar that contains the .properties file you want to alter.')
    parser.add_argument('prop_file', help='File name of the .properties file you want to alter.')
    parser.add_argument('prop', help='Name of the property you want to alter within prop_file.')
    parser.add_argument('value', help='Value of the property you want to alter within prop_file. '
                                      'Backslashes will preserved (\'\\\')')
    parser.add_argument('-v', '--verbose', action='store_true', help='Log a bunch of stuff while running')

    ns = parser.parse_args()
    ns.value = ns.value.replace('\\', '\\\\')
    VERBOSE = ns.verbose
    JAVA_HOME = os.environ['JAVA_HOME'].rstrip('\\')

    # check JAVA_HOME
    if VERBOSE:
        if 'jdk' not in os.environ["JAVA_HOME"]:
            print('WARNING: JAVA_HOME might not be set.')

    jar_cmd = f"{JAVA_HOME}\\bin\\jar"

    if VERBOSE:
        print(f"'jar' executable location: {jar_cmd}")

    # extract file
    jar_extract_cmd = [jar_cmd] + f'xf {os.path.abspath(ns.jar)} {ns.prop_file}'.split()
    if VERBOSE:
        print(f'Exracting .jar with command {jar_extract_cmd}')
    subprocess.run(jar_extract_cmd)

    # edit file while preserving comments
    try:
        for line in fileinput.input(ns.prop_file, inplace=True, backup='.bkp'):
            if ns.prop in line and not line.startswith('#'):
                print(f'{ns.prop}={ns.value}')  # prints to file because of context
            else:
                print(line, end='')
    except FileNotFoundError:
        print(f'File {ns.prop_file} in .jar {os.path.abspath(ns.jar)} doesn\'t exist.')
        sys.exit(0)

    # update jar
    jar_update_cmd = [jar_cmd] + f'uf {ns.jar} {ns.prop_file}'.split()
    if VERBOSE:
        print(f'Updating .jar with command {jar_update_cmd}')
    subprocess.run(jar_update_cmd)

    # delete the edited file that remains outside of the .jar
    os.remove(ns.prop_file)
    if VERBOSE:
        print('Deleting extracted .properties file')


if __name__ == '__main__':
    main()
