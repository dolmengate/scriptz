import subprocess
import argparse
import os
import fileinput
import sys
import jprops


def main():
    parser = argparse.ArgumentParser(description='Edit .properties files within .jar files. Creates a backup file in '
                                                 'case something goes wrong.')
    parser.add_argument('jar', help='Path of the .jar that contains the .properties file you want to alter.')
    parser.add_argument('prop_file', help='File name of the .properties file you want to alter.')
    parser.add_argument('prop', help='Name of the property you want to alter within prop_file.')
    parser.add_argument('-v', '--value', help="Value of the property you want to alter within prop_file. "
                                              "Backslashes will preserved ('\\'). If no value is given, 'prop's "
                                              "current value will be displayed and 'prop_file' will not be edited")
    parser.add_argument('-d', '--debug', action='store_true', help='Log a bunch of stuff while running')

    ns = parser.parse_args()
    if ns.value:
        ns.value = ns.value.replace('\\', '\\\\')
    DEBUG = ns.debug
    JAVA_HOME = os.environ['JAVA_HOME'].rstrip('\\')
    CHECK_ONLY = True if ns.value is None else False

    # check JAVA_HOME
    if DEBUG:
        if 'jdk' not in os.environ["JAVA_HOME"]:
            print('WARNING: JAVA_HOME might not be set.')
    jar_cmd = f"{JAVA_HOME}\\bin\\jar"

    if DEBUG:
        print(f"'jar' executable location: {jar_cmd}")

    # extract file
    jar_extract_cmd = [jar_cmd] + f'xf {os.path.abspath(ns.jar)} {ns.prop_file}'.split()
    if DEBUG:
        print(f'Exracting .jar with command {jar_extract_cmd}')
    subprocess.run(jar_extract_cmd)

    if CHECK_ONLY:
        try:
            with open(ns.prop_file) as pf:
                    props = jprops.load_properties(pf)
                    print(f"Current value of property '{ns.prop}' in '{ns.jar}' is '{props[ns.prop]}'")
        except KeyError:
            print(f'No property {ns.prop} in {ns.jar}')
            sys.exit(0)
        except FileNotFoundError:
            print(f'No file {ns.prop_file} in {ns.jar}')
            sys.exit(0)

    # edit file while preserving comments
    else:
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
        if DEBUG:
            print(f'Updating .jar with command {jar_update_cmd}')
        subprocess.run(jar_update_cmd)

    # delete extracted file that remains outside of the .jar
    if DEBUG:
        print('Deleting extracted .properties file')
    os.remove(ns.prop_file)


if __name__ == '__main__':
    main()
