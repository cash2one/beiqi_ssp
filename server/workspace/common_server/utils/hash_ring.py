#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-7-14

@author: Jay
"""
import md5

class HashRing(object):

    def __init__(self, nodes=None, replicas=3):
        """Manages a hash ring.

        `nodes` is a list of objects that have a proper __str__ representation.
        `replicas` indicates how many virtual points should be used pr. node,
        replicas are required to improve the distribution.
        注意:ring是没有保障任何顺序的
        """
        self.replicas = replicas

        self.ring = dict()
        self._sorted_keys = []

        if nodes:
            for node in nodes:
                self.add_node(node)

    def add_node(self, node):
        """Adds a `node` to the hash ring (including a number of replicas).
        """
        for i in xrange(0, self.replicas):
            key = self.gen_key('%s:%s' % (node, i))
            self.ring[key] = node
            self._sorted_keys.append(key)

        self._sorted_keys.sort()

    def remove_node(self, node):
        """Removes `node` from the hash ring and its replicas.
        """
        for i in xrange(0, self.replicas):
            key = self.gen_key('%s:%s' % (node, i))
            del self.ring[key]
            self._sorted_keys.remove(key)

    def has_node(self, node):
        """Check whether `node` is in the ring.
           True is return is node in ring else False
        """
        return node in self.ring.values()

    def get_node(self, string_key):
        """Given a string key a corresponding node in the hash ring is returned.

        If the hash ring is empty, `None` is returned.
        """
        return self.get_node_pos(string_key)[0]

    def get_node_pos(self, string_key):
        """Given a string key a corresponding node in the hash ring is returned
        along with it's position in the ring.

        If the hash ring is empty, (`None`, `None`) is returned.
        """
        if not self.ring:
            return None, None

        key = self.gen_key(string_key)

        nodes = self._sorted_keys
        for i in xrange(0, len(nodes)):
            node = nodes[i]
            if key <= node:
                return self.ring[node], i

        return self.ring[nodes[0]], 0

    def get_nodes(self, string_key):
        """Given a string key it returns the nodes as a generator that can hold the key.

        The generator is never ending and iterates through the ring
        starting at the correct position.
        """
        if not self.ring:
            yield None, None

        node, pos = self.get_node_pos(string_key)
        for key in self._sorted_keys[pos:]:
            yield self.ring[key]

        while True:
            for key in self._sorted_keys:
                yield self.ring[key]

    def gen_key(self, key):
        """Given a string key it returns a long value,
        this long value represents a place on the hash ring.

        md5 is currently used because it mixes well.
        """
        m = md5.new()
        m.update(key)
        return long(m.hexdigest(), 16)

    def next_nodes(self, node):
        """
        Given a node it returns the next virtual points after all the virtual points of the cur node

        The next point is a virtual point that on the next of the node's virtual points in the ring order
        The next points is returned
        """
        next_key = lambda i: self._sorted_keys[(i + 1) % len(self._sorted_keys)]
        return [self.ring[next_key(i)]
                for i, key in enumerate(self._sorted_keys)
                if self.ring[key] == node and self.ring[next_key(i)] != node]

