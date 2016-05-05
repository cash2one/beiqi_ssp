#coding:utf-8

import imp
import sys
from inspect import getmembers
import inspect
from collections import defaultdict

from pkgutil import iter_modules

ATTACH_ATTR = '__venusian_callbacks__'

class Scanner(object):
    def __init__(self, **kw):
        self.__dict__.update(kw)
        self.__collects = defaultdict(list)
        
        
    def get_maps(self):
        return self.__collects.copy()
        

    def scan(self, package, ignore=None):
        '''扫描package
        
        ignore: 可以是basestring也可以是function
        '''
        categories = None
        onerror = None
        pkg_name = package.__name__

        if ignore is not None and not hasattr(ignore, '__iter__'):
            ignore = [ignore]
        
        def _ignore(fullname):
            if ignore is None:
                return False
            for ign in ignore:
                if not callable or not isinstance(ign, basestring):
                    return False
                if callable(ign):
                    return ign(fullname)
                if ign.startswith('.'):
                    if fullname.startswith(pkg_name + ign):
                        return True
                else:
                    if ign in fullname:
                        return True
                    if fullname.startswith(ign):
                        return True


        def invoke(mod_name, name, ob):
            fullname = mod_name + '.' + name

            if _ignore(fullname):
                return
            self.__collects[mod_name].append({name: ob})
            

        for name, ob in getmembers(package):
            invoke(pkg_name, name, ob)
            
        if not hasattr(package, '__path__'):
            return
    
        #package, not module
        results = walk_packages(package.__path__, package.__name__+'.',
                                onerror=onerror, ignore=_ignore)

        for importer, modname, ispkg in results:
            loader = importer.find_module(modname)
            if loader is not None: # happens on pypy with orphaned pyc
                try:
                    if hasattr(loader, 'etc'):
                        # python < py3.3
                        module_type = loader.etc[2]
                    else: # pragma: no cover
                        # py3.3b2+ (importlib-using)
                        module_type = imp.PY_SOURCE
                        fn = loader.get_filename()
                        if fn.endswith(('.pyc', '.pyo', '$py.class')):
                            module_type = imp.PY_COMPILED
                    # only scrape members from non-orphaned source files
                    # and package directories
                    if module_type in (imp.PY_SOURCE, imp.PKG_DIRECTORY):
                        # NB: use __import__(modname) rather than
                        # loader.load_module(modname) to prevent
                        # inappropriate double-execution of module code
                        try:
                            __import__(modname)
                        except Exception:
                            if onerror is not None:
                                onerror(modname)
                            else:
                                raise
                        module = sys.modules.get(modname)
                        if module is not None:
                            for name, ob in getmembers(module, None):
                                invoke(modname, name, ob)
                finally:
                    if  ( hasattr(loader, 'file') and
                          hasattr(loader.file,'close') ):
                        loader.file.close()
                        

class AttachInfo(object):
    def __init__(self, **kw):
        self.__dict__.update(kw)

        
class Categories(dict):
    def __init__(self, attached_to):
        super(dict, self).__init__()
        if attached_to is None:
            self.attached_id = None
        else:
            self.attached_id = id(attached_to)

    def attached_to(self, obj):
        if self.attached_id:
            return self.attached_id == id(obj)
        return True
    
def attach(wrapped, callback, category=None, depth=1):
    frame = sys._getframe(depth+1)
    scope, module, f_locals, f_globals, codeinfo = getFrameInfo(frame)
    module_name = getattr(module, '__name__', None)
    if scope == 'class':
        # we're in the midst of a class statement
        categories = f_locals.setdefault(ATTACH_ATTR, Categories(None))
        callbacks = categories.setdefault(category, [])
        callbacks.append((callback, module_name))
    else:
        categories = getattr(wrapped, ATTACH_ATTR, None)
        if categories is None or not categories.attached_to(wrapped):
            # if there aren't any attached categories, or we've retrieved
            # some by inheritance, we need to create new ones
            categories = Categories(wrapped)
            setattr(wrapped, ATTACH_ATTR, categories)
        callbacks = categories.setdefault(category, [])
        callbacks.append((callback, module_name))
    return AttachInfo(
        scope=scope, module=module, locals=f_locals, globals=f_globals,
        category=category, codeinfo=codeinfo)

        
def walk_packages(path=None, prefix='', onerror=None, ignore=None):
    def seen(p, m={}):
        if p in m: # pragma: no cover
            return True
        m[p] = True

    # iter_modules is nonrecursive
    for importer, name, ispkg in iter_modules(path, prefix):

        if ignore is not None and ignore(name):
            # if name is a package, ignoring here will cause
            # all subpackages and submodules to be ignored too
            continue

        # do any onerror handling before yielding

        if ispkg:
            try:
                __import__(name)
            except Exception:
                if onerror is not None:
                    onerror(name)
                else:
                    raise
            else:
                yield importer, name, ispkg
                path = getattr(sys.modules[name], '__path__', None) or []

                # don't traverse path items we've seen before
                path = [p for p in path if not seen(p)]

                for item in walk_packages(path, name+'.', onerror):
                    yield item
        else:
            yield importer, name, ispkg

            
    
def getFrameInfo(frame):
    """Return (kind,module,locals,globals) for a frame

    'kind' is one of "exec", "module", "class", "function call", or "unknown".
    """

    f_locals = frame.f_locals
    f_globals = frame.f_globals

    sameNamespace = f_locals is f_globals
    hasModule = '__module__' in f_locals
    hasName = '__name__' in f_globals

    sameName = hasModule and hasName
    sameName = sameName and f_globals['__name__']==f_locals['__module__']

    module = hasName and sys.modules.get(f_globals['__name__']) or None

    namespaceIsModule = module and module.__dict__ is f_globals

    frameinfo = inspect.getframeinfo(frame)
    try:
        sourceline = frameinfo[3][0].strip()
    except: # dont understand circumstance here, 3rdparty code without comment
        sourceline = frameinfo[3]

    codeinfo = frameinfo[0], frameinfo[1], frameinfo[2], sourceline

    if not namespaceIsModule:
        # some kind of funky exec
        kind = "exec" # don't know how to repeat this scenario
    elif sameNamespace and not hasModule:
        kind = "module"
    elif sameName and not sameNamespace:
        kind = "class"
    elif not sameNamespace:
        kind = "function call"
    else:
        # How can you have f_locals is f_globals, and have '__module__' set?
        # This is probably module-level code, but with a '__module__' variable.
        kind = "unknown"
    return kind, module, f_locals, f_globals, codeinfo
    
