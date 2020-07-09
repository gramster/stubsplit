import os


def split(stubroot, docroot, fname):
    """
    Given the path to a .pyi file in `fname` as a path relative to `stubroot`,
    split it into a docstring part and a stub part. The stub part should get 
    written to the original file, and the docstring part should be written to
    a file with a .ds extension at the same relative path but under `docroot`.

    So for example, if called with `split('orig', 'target', 'module/__init__.py')`,
    you will end up with a stripped version of the stub in `orig/module/__init__.py`,
    and the docstrings in `target/module/__init__.py.ds`.

    The docstring file will preserve `class` lines, and the signature of the 
    specific function/method.

    The inverse function is `combine`.
    """
    stubfile = os.path.join(stubroot, fname)
    docfile = os.path.join(docroot, fname) + '.ds'
    if not os.path.exists(stubfile):
        raise Exception(f'Missing stub file {fname}')
    with open(stubfile) as f:
        stublines = f.readlines()
    newstublines = []    
    newdoclines = []
    defbuff = None
    classbuff = None
    indoc = False
    target = newstublines
    gotclose = False
    for line in stublines:
        ls = line.strip()
        if defbuff:
            if ls[:3] == "'''" or ls[:3] == '"""':  # start of docstring
                if classbuff and defbuff[0] == ' ':
                    newdoclines.append('\n')
                    newdoclines.append(classbuff)
                newstublines.append(defbuff[:-1] + ' ...\n')
                newdoclines.append(defbuff)
                indoc = True
                classbuff = None
            else:
                newstublines.append(defbuff)
                if defbuff[0] == 'd':  # top level def?
                    classbuff = None
            defbuff = None

        if indoc:  # Keep adding to docstring until we hit a 'pass' line
            newdoclines.append(line)
            if gotclose and ls == 'pass': 
                indoc = False
            else:
                gotclose = ls == "'''" or ls == '"""'
        elif ls[:4] == 'def ':
            defbuff = line
        else:
            if ls[:6] == 'class ':
                classbuff = line
            newstublines.append(line)

    
    with open(stubfile, 'w') as f:
        f.writelines(newstublines)

    with open(docfile, 'w') as f:
        f.writelines(newdoclines)
        print('OUTPUT DOC:\n=====\n')
        print(''.join(newdoclines))
        print('=====\n')


def combine(stubroot, docroot, fname):
    """
    Given the path to a .pyi file in `fname` as a path relative to `origroot`,
    and given that a similar file exists under `docroot` with the same relative
    path but an additional `.ds` suffix, combine these and replace the original
    stubfile with one that has the docstrings merged in.

    The inverse function is `split`.
    """   
    stubfile = os.path.join(stubroot, fname)
    docfile = os.path.join(docroot, fname) + '.ds'
    if not os.path.exists(stubfile):
        raise Exception(f'Missing stub file {fname}')
    if not os.path.exists(docfile):
        raise Exception(f'Missing doc file {fname}.ds')
    with open(stubfile) as f:
        stublines = f.readlines()
    with open(docfile) as f:
        doclines = f.readlines()

    newstublines = []



