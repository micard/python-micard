def convert_to_utf8_str(arg):
    # written by Michael Norton (http://docondev.blogspot.com/)
    if isinstance(arg, unicode):
        arg = arg.encode('utf-8')
    elif not isinstance(arg, str):
        arg = str(arg)
    return arg
    

def is_iterable(arg):
    iterable = False
    try:
        iter(arg)
        if not isinstance(arg, basestring):
            iterable = True
    except TypeError:
        pass
        
    return iterable