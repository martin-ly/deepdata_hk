#coding: utf8

#爬虫进程数量
process_num = 1

#失败重试次数
retry_num = 5

#任务定义
init_tasks = {
    1 : {
        'description' : u'港股.券商追踪.股份解码',
        'package' : 'hk_qszz_gfjm',
        'enable' : True,
    },

    2 : {
        'description' : u'港股.市场沽空',
        'package' : 'hk_shortselling',
        'enable' : True,
    }
    3 : {
        'description' : u'港股.参与者编号与经纪编号的对应关系',
        'package' : 'hk_codemap',
        'enable' : True,
    }
}
