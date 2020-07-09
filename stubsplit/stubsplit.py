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

    # TODO: handle nested classes eventually (right now we have no docstrings for
    #    these so not urgent)
    # TODO: handle split lines. This is more urgent as the stubs will likely be 
    #    reformatted.
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

    # Gather together all the top-level functions and all the classes
    # in dicts. That way we can be resilient to reorderings, if not
    # file moves yet.

    def gather_def(lines, i):
        ln = lines[i].strip()
        name = ln[4:ln.find('(')]
        start = i
        i += 1
        while i < len(lines):
            ln = lines[i].strip()
            i += 1
            if ln == 'pass':
                break
        return name, lines[start:i], i

    top_level = {}
    classes = {}
    i = 0
    while i < len(doclines):
        ln = doclines[i]
        if ln[:6] == 'class ':
            name = ln[6:min(ln.find('('), ln.find(':'))]
            i += 1
            methods = {}
            classes[name] = methods
            while i < len(doclines) and doclines[i][0] == ' ':
                name, deflines, i = gather_def(doclines, i)
                methods[name] = deflines
        elif ln[:4] == 'def ':
            name, deflines, i = gather_def(doclines, i)
            top_level[name] = deflines
        elif len(ln.strip()) > 0:
            raise Exception(f'Unhandled line {i}: "{ln}"')
        else:
            i += 1

    # Now output the new stub lines. If we find a top-level method
    # or class that is in our gathered data, substitute the original
    # line for the gathered version.
    # TODO: again, this may get complicated later by folded lines.

    newstublines = []

    i = 0
    while i < len(stublines):
        ln = stublines[i]
        i += 1
        if ln[:6] == 'class ':
            name = ln[6:min(ln.find('('), ln.find(':'))]
            methods = classes[name] if name in classes else {}
            newstublines.append(ln)
            while i < len(stublines):
                # Either we have a indented line or a top-level
                # construct again
                ln = stublines[i]
                if ln[0] != ' ':
                    break
                i += 1
                ls = ln.strip()
                if ls[:4] == 'def ':
                    name = ls[4:ls.find('(')]
                    if name in methods:
                        newstublines.extend(methods[name])
                    else:
                        newstublines.append(ln)
                else:
                    newstublines.append(ln)
        elif ln[:4] == 'def ':
            name = ln[4:ln.find('(')]
            if name in top_level:
                newstublines.extend(top_level[name])
            else:
                newstublines.append(ln)
        else:
            newstublines.append(ln)

    with open(stubfile, 'w') as f:
        f.writelines(newstublines)


