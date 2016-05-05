#coding:utf-8


class FieldDict(dict):
    def __init__(self, **kw):
        super(FieldDict, self).__init__(**kw)

    def __setattr__(self, key, value):
        self.update({key: value})

    def __getattr__(self, item):
        """
        无需判定item是否为空，python解释器会搞定
        """
        #强制要求键值存在
        if item not in self:
            raise ValueError('key %r not exist' % item)
        return self.get(item)

    def contain_keys(self, *keys):
        """
        递归判定
        """
        r = self
        for k in keys:
            r = r.get(k)
            if r is None:
                return False

        return True