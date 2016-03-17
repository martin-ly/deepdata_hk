#coding: utf8

#调试模式打开后，爬虫进程数量将固定为1而不管下面的配置，爬虫的重定向输出将被关闭
DEBUG = False

#爬虫进程数量
process_num = 10

#失败重试次数
retry_num = 5

#输出终端字符编码，win为'gbk'，linux为'utf8'
terminal_charset = 'gbk'

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
        'enable' : False,
    },

    3 : {
        'description' : u'港股.参与者编号与经纪编号的对应关系',
        'package' : 'hk_codemap',
        'enable' : True,
    }
}
