#!/usr/bin/python2.7
# coding=utf-8
"""
Created on 2015-8-27

@author: Jay
"""
from utils.hash_ring import HashRing
from utils import logger


class ServiceCluster(object):
    service_mgr = None

    def __init__(self):
        # 虚拟节点必须只有1个，如果多个的话，虽然增加了分布式，但是同时该节点故障的话，也影响多个虚拟节点，进而影响多个实体节点的数据更新
        self.__hash_ring = HashRing(replicas=1)

    def add_service(self, service_obj, is_init=False):
        """
        添加一个服务对象到服务集群
        :param is_init:是否初始化，如果是初始化，无论如何，不清理缓存；否则考虑清理缓存
        """
        cur_node = service_obj.hash_key()
        if self.__hash_ring.has_node(cur_node):
            logger.warn("ServiceCluster::add_service failed, node has exist!!!, service_obj:%s" % service_obj)
            return

        self.__hash_ring.add_node(cur_node)

        if not is_init:
            self._do_effect_nodes(cur_node)
        logger.warn("ServiceCluster::add_service success, service_obj:%s cur_node:%s" % (service_obj, cur_node))

    def del_service(self, service_obj):
        """
        从服务集群里面删除一个服务
        """
        cur_node = service_obj.hash_key()
        if not self.__hash_ring.has_node(cur_node):
            logger.warn("ServiceCluster::del_service, node not exist!!!, service_obj:%s cur_node:%s" % (service_obj, cur_node))
            return

        self.__hash_ring.remove_node(service_obj.hash_key())
        logger.warn("ServiceCluster::del_service success, service_obj:%s cur_node:%s" % (service_obj, cur_node))

    def get_service_objs(self, string_key_ls):
        """
        根据key列表从服务集群获取服务对象列表
        :param string_key_ls: 筛选的key列表
        :return: [service_obj]
        """
        assert isinstance(string_key_ls, list)
        nodes = [self.__hash_ring.get_node(key) for key in string_key_ls]
        return self.service_mgr.get_services_by_hash_keys(nodes)

    def _do_effect_nodes(self, cur_node):
        """
        处理被影响的节点的缓存
        :param cur_node:
        :return:
        """
        eff_nodes = self.__hash_ring.next_nodes(cur_node)
        eff_service_objs = self.service_mgr.get_services_by_hash_keys(eff_nodes)

        # 将被影响的下一个节点清除缓存
        for service_obj in eff_service_objs:
            if service_obj.control_rpc:
                logger.info("ServiceCluster::_do_effect_nodes, clear_cache, service_obj:%s " % service_obj)
                service_obj.control_rpc.clear_cache()
            else:
                logger.warn("ServiceCluster::_do_effect_nodes, control_rpc not exist!!!, service_obj:%s " % service_obj)