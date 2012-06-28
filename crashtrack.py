"""
Track important values, print on exceptions.

Sample use:

@tracked
def foo(a=1):
  divisor = a - 1
  track("Dividing by %r", divisor)
  return 1 / divisor

@tracked
def bar(x):
    track('before foo(%r)', x)
    return foo(x)

>>> bar(1)
bar: before foo(1)
foo: Dividing by 0
<Normal stacktrace>
"""

__all__ = ['track', 'tracked']

from threading import local
import sys

_local = local()
_local.stack = [] # contains mutable [func_name, current_message] items

def _say(func_name, msg):
    """
    Output a stack line to stderr.
    """
    for s in func_name, ': ', msg, '\n':
        sys.stderr.write(s)

def track(msg, *data):
    """
    Store a string msg % data in a tracking stack.
    It will be printed if an unhandled exception is raised
    in a function decorated with @tracked.
    """
    _local.stack[-1][1] = msg % data

def tracked(func):
    """
    Decorator to use on functions where track() is used.
    If an unhandled exception happens in the function,
    the whole stack of  strings accumulated by track() calls
    in the decorated functions, with function names, is printed.
    The exception is then re-raised.
    """
    def printCrashTrack(*args, **kwargs):
        _local.stack.append([func.__name__, 'entered'])
        try:
            return func(*args, **kwargs)
        except:
            for func_name, msg in _local.stack:
                _say(func_name, msg)
            _local.stack = [] # so that upper levels don't print it
            raise
        finally:
            if _local.stack:
                _local.stack.pop()
    return printCrashTrack


# TODO:
# def trackedAllowing(*exception_classes):
#     """
#     Same as @tracked, but does not print the trace
#     if an exception for exception_classes is raised.
#     """
# Problem: how to cut the tracking stack exactly up to the handler?
# Storing actual call frame IDs could be a solution.
# It would allow to match tracking stack with excpetion stack trace if desired.
