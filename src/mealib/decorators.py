"""Implementing of decorators for module."""
import functools
from os.path import isdir

def check_attr(*attr):
    def decorator_check_attr(func):
        @functools.wraps(func)
        def wrapper_attr(*args, **kwargs):
            for kattr in attr:
                if hasattr(args[0], kattr):
                    return func(*args, **kwargs)
                else:
                    if kattr == 'data':
                        print 'MCD file is not loaded, use read_mcd()'
                    else:
                        print 'The attribute does not exist.'
        return wrapper_attr
    return decorator_check_attr


def check_dir(func):
    @functools.wraps(func)
    def wrapper_dir(*args, **kwargs):
        folder = args[1]
        if isdir(folder):
            return func(*args, **kwargs)
        else:
            print 'Error in source folder. Check it'
    return wrapper_dir
