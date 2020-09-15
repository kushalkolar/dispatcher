from functools import wraps
from typing import *
import dill
import os
from uuid import uuid4
from inspect import getsource
import subprocess


def dispatch(attrs: Optional[List[str]] = None):
    """
    """
    def f(func):
        @wraps(func)
        def fn(self, *args, **kwargs):
            # print('np' in globals().keys())
            # globals().update(globals_dict)
            # print('np' in globals().keys())

            tmp_dir = os.path.join('/tmp', f'dispatch-{uuid4()}')
            os.makedirs(tmp_dir)

            if attrs is not None:
                pass

            self_path = os.path.join(tmp_dir, 'self')
            dill.dump(
                self,
                open(self_path, 'wb')
            )

            args_path = os.path.join(tmp_dir, 'args')
            dill.dump(
                args,
                open(args_path, 'wb')
            )

            kwargs_path = os.path.join(tmp_dir, 'kwargs')
            dill.dump(
                kwargs,
                open(kwargs_path, 'wb')
            )

            # globals_path = os.path.join(tmp_dir, 'globals')
            # dill.dump(
            #     globals_dict,
            #     open(globals_path, 'wb')
            # )



            # strip decorators away
            src = '\n'.join([l for l in getsource(func).split('\n') if not l.startswith('@')])

            runfile_path = os.path.join(tmp_dir, '__main__.py')
            out_path = os.path.join(tmp_dir, 'out')

            with open(runfile_path, 'w') as f:
                header = '\n'.join(
                    [
                        f'#!/home/kushal/python-virtual-environments/mesmerize/bin/python3',
                        f'import dill',
                        f'self = dill.load(open("{self_path}", "rb"))',
                        f'args = dill.load(open("{args_path}", "rb"))',
                        f'kwargs = dill.load(open("{kwargs_path}", "rb"))',
                        # f'globals_dict = dill.load(open("{globals_path}", "rb"))',
                        # f'globals().update(globals_dict)'
                    ]
                )

                footer = '\n'.join(
                    [
                        f'out = {func.__name__}(self, *args, **kwargs)',
                        f'dill.dump(out, open("{out_path}", "wb"))',
                    ]
                )

                f.write(header)
                f.write('\n' + src)
                f.write(footer)

            subprocess.Popen(
                ["/home/kushal/python-virtual-environments/mesmerize/bin/python3", runfile_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            return out_path
        return fn
    return f