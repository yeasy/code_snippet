# -*- coding: utf-8 -*- 
"""
This script will generate a gitbook projects based on the given dir.
The resulted dir will have the same structure.
Output will can be redirected as the SUMMARY.md.

Author: yeasy@github.com
"""

import os 
import sys

RESULT_DIR=os.getcwd()+os.sep+'outline_dir'

def create_file(file_path, content):
    """
    Create a file at the path, and write down the content.
    """
    with open(file_path, 'w') as f:
        f.write(content+'\n')

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
            create_file(RESULT_DIR+os.sep+path+os.sep+'README.md', '#'*level+' '+e)
            line = '* [%s](%s/README.md)' % (e, path.replace('\\','/'))
        print ' '*3*(level-1)+line
        process_dir(path, level+1)
    for e in list_file: # files
        name, suffix = os.path.splitext(e) #test .py
        path = os.path.join(rootDir, name).replace('.'+os.sep,'') + suffix.replace('.','_') # test\test_py
        create_file(RESULT_DIR+os.sep+path+'.md', '#'*level+' '+e)
        line = '* [%s](%s.md)' % (e, path.replace('\\','/'))
        print ' '*3*(level-1)+line

if __name__ == '__main__':
    if len(sys.argv)>1:
        if not os.path.exists(RESULT_DIR):
            os.makedirs(RESULT_DIR)
            create_file(RESULT_DIR+os.sep+'README.md', '#')
        for d in sys.argv[1:]:
            os.chdir(d)
            print "#Summary\n\n"
            process_dir('.')
    else:
        print "Put your path as parameters"

