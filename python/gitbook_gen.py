# -*- coding: utf-8 -*- 
"""
This script will generate a gitbook projects based on the given dir.
The generated dir contains the same structure and have the necessary markdown files.
Output will can be redirected as the SUMMARY.md.

Author: yeasy@github.com
"""

import os 
import sys

ROOT_DIR = os.getcwd()
RESULT_DIR= ROOT_DIR+os.sep+'outline_dir'

def create_file(file_path, content, forced=False):
    """
    Create a file at the path, and write into the content.
    If not forced, when file already exists, then do nothing.
    """
    if os.path.isfile(file_path) and not forced:
        print "%s already exists, stop writing content=%s" % (file_path, content)
        return
    with open(file_path, 'w') as f:
        f.write(content+'\n')

def append_summary(content, debug=False):
    """
    Write the content into the SUMMARY.md file
    """
    summary_path = RESULT_DIR + os.sep + 'SUMMARY.md'
    if not os.path.isfile(summary_path):
        create_file(summary_path, content)
    else:    
        with open(summary_path, 'a') as f:
            f.write(content+'\n')
    if debug:
        print content

def init_gb_dir(dirname, title):
    """
    Initialized a gitbook dir by make sure its existence and init a README.md
    """
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    create_file(dirname+os.sep+'README.md', '', forced=True)

def refine_dirname(dirname):
    """
    Refine a dirname string to make sure it's validate for processing.
    """
    dirname = dirname.replace('.'+os.sep,'') # remove ./
    if dirname.endswith('/') or dirname.endswith('\\'):
        dirname = dirname[:-1]
    return dirname

def process_dir(rootDir, level=1): 
    """
    Process the dir, checking sub dirs and files.
    """
    if level>4: # do not process very deep dir
        return
    valid_dirs = filter(lambda x: not x.startswith('.'), os.listdir(rootDir))
    list_dir = filter(lambda x: os.path.isdir(os.path.join(rootDir, x)), valid_dirs)
    list_file = filter(lambda x: os.path.isfile(os.path.join(rootDir, x)) and not x.startswith('_'), valid_dirs)
    
    for e in list_dir: # dirs
        path = os.path.join(rootDir, e).replace('.'+os.sep,'')
        if level == 4:
            create_file(RESULT_DIR+os.sep+path+'.md', '#'*level+' '+e)
            line = '* [%s](%s.md)' % (e,path.replace('\\','/'))
        else:
            if not os.path.exists(RESULT_DIR+os.sep+path):
                os.makedirs(RESULT_DIR+os.sep+path)
            create_file(RESULT_DIR+os.sep+path+os.sep+'README.md', '#'*level+' '+e, forced=True)
            line = '* [%s](%s/README.md)' % (e, path.replace('\\','/'))
        append_summary(' '*3*(level-1)+line)
        process_dir(path, level+1)
    for e in list_file: # files
        name, suffix = os.path.splitext(e) #test .py
        path = os.path.join(rootDir, name).replace('.'+os.sep,'') + suffix.replace('.','_') # test\test_py
        create_file(RESULT_DIR+os.sep+path+'.md', '#'*level+' '+e)
        line = '* [%s](%s.md)' % (e, path.replace('\\','/'))
        append_summary(' '*3*(level-1)+line)

if __name__ == '__main__':
    if len(sys.argv)>1:
        for d in sys.argv[1:]:
            if not os.path.exists(d):
                print "%s does not exist" %d
                continue
            d = refine_dirname(d)
            RESULT_DIR = ROOT_DIR+os.sep+d.replace('/','_').replace('\\','_')+'_gitbook'
            init_gb_dir(RESULT_DIR, d)
            append_summary("#Summary\n")
            os.chdir(d)
            process_dir('.')
    else:
        print "Put your path as parameters"

