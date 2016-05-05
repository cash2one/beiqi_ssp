# coding:utf-8


import bisect


DEFAULT_FUNC = lambda *x: True


def first_default(func, seq):
    """
    惰性展开
    """
    assert callable(func)
    for _ in seq:
        if func(_):
            return _
    return None


class SkipList(object):
    def __init__(self):
        # 跳表层，从0递增
        self.__levels = {}
        self.__entities = []

    def __append_level(self, lvl, rid):
        """
        默认已排序
        """
        assert isinstance(lvl, int)
        if lvl not in self.__levels:
            self.__levels.update({lvl: []})
        self.__levels[lvl].append((rid, len(self.__levels[lvl])))

    def append(self, rid, payload):
        assert rid and isinstance(rid, (int, long))
        assert payload and isinstance(payload, dict)

        self.__append_level(0, rid)
        self.__entities.append(payload)

    def __find_dst_insert(self, dst_rid):
        #超出0层的最大值
        if dst_rid > self.__levels.get(0)[-1][0]:
            return

        tot = len(self.__levels)
        for l in sorted(self.__levels.iterkeys()):
            below = self.__levels[l]
            above = self.__levels[l + 1] if l < tot - 1 else None

            below_rid = below[-1][0]
            above_rid = above[-1][0] if above else -1

            if below_rid == dst_rid:
                continue
            elif -1 != above_rid and above_rid == dst_rid:
                continue
            elif below_rid > dst_rid > above_rid:
                yield l + 1, self.__levels.get(0)[bisect.bisect(self.__levels.get(0), (dst_rid, 0))]

    def insert_level(self, dst_rid):
        """
        :param dst_rid: 目标rid
        """
        if not self.__entities:
            return

        _ = first_default(DEFAULT_FUNC, self.__find_dst_insert(dst_rid))
        if _ is None:
            return

        target_level, adjust = _
        tot = len(self.__levels) - 1
        for l in xrange(tot, target_level - 1, -1):
            self.__levels.update({l + 1: self.__levels.get(l)})
        self.__levels[target_level] = [(self.__levels[0][0][0], 0), adjust]

    def recycle_level(self, level):
        #todo: recycle unecssary levels
        pass

    def find(self, rid):
        target_level = first_default(DEFAULT_FUNC,
                                     (l for l in sorted(self.__levels.iterkeys()) if
                                      self.__levels.get(l)[-1][0] <= rid))
        if not target_level:
            #0层通过bisect查找
            index = bisect.bisect(self.__levels.get(0), (rid, 0))
            index = index + 1 if self.__levels.get(0)[index][0] == rid else index
            for i in xrange(index, len(self.__entities)):
                yield self.__entities[i]
        else:
            for i in xrange(self.__levels.get(target_level)[-1][1], len(self.__levels[0])):
                test_rid, cur_index = self.__levels[0][i]
                if test_rid <= rid:
                    continue
                yield self.__entities[cur_index]


class SkipCollection(object):
    """
    默认情况下，append的记录对象rid
    必定从小到大排序
    """
    def __init__(self):
        self.__sl = {}

    def append(self, eid, rid, payload):
        if eid not in self.__sl:
            self.__sl[eid] = SkipList()
        self.__sl[eid].append(rid, payload)

    def find(self, eid, rid, dumps=None):
        if eid not in self.__sl:
            return
        _ = tuple(self.__sl.get(eid).find(rid))
        if dumps is None:
            return _
        return dumps(_)