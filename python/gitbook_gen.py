# -*- coding: utf-8 -*- 
"""
This script will generate a gitbook projects based on the given dir.
The generated dir contains the same structure and the corresponding markdown
files.

Usage: python gitbook_gen [source_dir1] [source_dir2] ...

Author: yeasy@github.com
"""

import __future__
import os 
import sys

ROOT_PATH = os.getcwd()
RESULT_PATH = ""


def create_file(file_path, content, forced=False):
    """ Create a file at the path, and write the content.
    If not forced, when file already exists, then do nothing.

    :param file_path: The whole path of the file
    :param content: Content to write into the file
    :param forced: Whether to force to overwrite file content
    :return: None
    """
    if os.path.isfile(file_path) and not forced:
        print("Warn: {} already exists, stop writing content={}".format(
            file_path, content))
        return
    with open(file_path, 'w') as f:
        f.write(content+'\n')


def append_summary_file(content, debug=False):
    """ Append the content into the SUMMARY.md file

    :param content: content to append to SUMMARY file
    :param debug: Whether to output the result
    :return: None
    """
    summary_file = RESULT_PATH + os.sep + 'SUMMARY.md'
    if not os.path.isfile(summary_file):
        create_file(summary_file, content)
    else:    
        with open(summary_file, 'a') as f:
            f.write(content+'\n')
    if debug:
        print(content)


def init_gitbook_dir(dir_path, title):
    """ Initialized a gitbook dir by make sure its existence and init a README.md

    :param dir_path: whole dir path
    :param title: project title
    :return:
    """
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    create_file(dir_path + os.sep + 'README.md',
                ("{}\n"+"="*len(title)).format(title), forced=True)


def refine_dirname(name):
    """ Refine a dir name to make sure it's validate for processing.

    :param name: directory name to refine
    :return: refined result
    """
    name = name.replace('.' + os.sep, '')  # remove ./
    if name.endswith('/') or name.endswith('\\'):
        name = name[:-1]
    return name


def process_dir(root_dir, level=1):
    """ Process the dir, checking sub dirs and files.

    :param root_dir:
    :param level:
    :return:
    """
    if level > 4:  # do not process very deep dir
        return
    valid_dirs = filter(lambda x: not x.startswith('.'), os.listdir(root_dir))
    list_dir = filter(lambda x: os.path.isdir(os.path.join(root_dir, x)),
                      valid_dirs)
    list_file = filter(lambda x: os.path.isfile(os.path.join(root_dir, x)) and
                                 not x.startswith('_'), valid_dirs)
    
    for e in list_dir:  # dirs
        path = os.path.join(root_dir, e).replace('.' + os.sep, '')
        if level == 4:
            create_file(RESULT_PATH + os.sep + path + '.md', '#' * level + ' ' + e)
            line = '* [%s](%s.md)' % (e,path.replace('\\','/'))
        else:
            if not os.path.exists(RESULT_PATH+os.sep+path):
                os.makedirs(RESULT_PATH + os.sep + path)
            create_file(RESULT_PATH + os.sep + path + os.sep + 'README.md',
                        '#' * level + ' ' + e, forced=True)
            line = '* [%s](%s/README.md)' % (e, path.replace('\\','/'))
        append_summary_file(' ' * 3 * (level - 1) + line)
        process_dir(path, level+1)
    for e in list_file:  # files
        name, suffix = os.path.splitext(e)  # test .py
        path = os.path.join(root_dir, name).replace('.' + os.sep, '') \
               + suffix.replace('.', '_')  # test\test_py
        create_file(RESULT_PATH + os.sep + path + '.md', '#' * level + ' ' + e)
        line = '* [%s](%s.md)' % (e, path.replace('\\', '/'))
        append_summary_file(' ' * 3 * (level - 1) + line)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        for d in sys.argv[1:]:
            if not os.path.exists(d):
                print("WARN: dir name {} does not exist".format(d))
                continue
            d = refine_dirname(d)
            RESULT_PATH = ROOT_PATH + os.sep \
                          + d.replace('/', '_').replace('\\', '_') \
                          + '_gitbook'
            print("Will init the output dir={}".format(RESULT_PATH))
            init_gitbook_dir(RESULT_PATH, d)
            append_summary_file("#Summary\n")
            os.chdir(d)
            process_dir('.')
    else:
        print("Put the input dir name(s) as parameters")
        print("Usage: python gitbook_gen [source_dir1] [source_dir2] ... ")

