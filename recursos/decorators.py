# coding: utf8
# Un gran porcentaje del código del presente script se basa en el proyecto DJITelloPy de DAMIÀ FUENTES ESCOTÉ, cuya licencia MIT y nota de permiso se cita al final del archivo.
# A great percentage of the code of the present script is based upon DJITelloPy project by DAMIÀ FUENTES ESCOTÉ, whose MIT license and permission notice is cited at the end of the file.
# URL fuente proyecto DJITellopy / Source URL DJITelloPy project: github.com/damiafuentes/DJITelloPy
import sys
import functools

## DECORATORS.PY
# Decorator to check method param type, raise needed exception type
# http://code.activestate.com/recipes/578809-decorator-to-check-method-param-types/
def accepts(**types):
    def check_accepts(f):
        if sys.version_info >= (3, 0):
            fun_code = f.__code__
            fun_name = f.__name__
        else:
            fun_code = f.func_code
            fun_name = f.func_name

        argcount = fun_code.co_argcount
        if 'self' in fun_code.co_varnames:
            argcount -= 1

        s = "accept number of arguments not equal with function number of arguments in ", fun_name, ", argcount ", \
            argcount
        assert len(types) == argcount, s

        @functools.wraps(f)
        def new_f(*args, **kwds):
            for i, v in enumerate(args):
                if fun_code.co_varnames[i] in types and \
                        not isinstance(v, types[fun_code.co_varnames[i]]):
                    raise TypeError("arg '%s'=%r does not match %s" % (fun_code.co_varnames[i], v, types[fun_code.co_varnames[i]]))

            for k, v in kwds.items():
                if k in types and not isinstance(v, types[k]):
                    raise TypeError("arg '%s'=%r does not match %s" % (k, v, types[k]))

            return f(*args, **kwds)

        if sys.version_info >= (3, 0):
            new_f.__name__ = fun_name
        else:
            new_f.func_name = fun_name
        return new_f

    return check_accepts


def obtener_state_decorator(func):
    @functools.wraps(func)
    def wrapped(instance, *args, **kwargs):
        if instance.response_state == 'ok':
            return False
        else:
            try:
                return func(instance, *args, **kwargs)
            except:
                instance.LOGGER.error(f"Exception in {func.__name__} occured")
                return 0
    return wrapped

"""
MIT License

Copyright (c) 2018 DAMIÀ FUENTES ESCOTÉ

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""