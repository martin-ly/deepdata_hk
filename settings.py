#coding: utf8

#调试模式打开后：
# 1. 所有输出将被记录日志，否则，只有错误日志被记录到日志
# 2. 记录工作进程的PID
DEBUG = False

#爬虫进程数量
process_num = 20

#失败重试次数
retry_num = 5

#输出终端字符编码，win为'gbk'，linux为'utf8'
terminal_charset = 'gbk'

#任务定义
#description: 任务描述，unicode编码
#package: 对应每一个爬虫任务的目录名，该任务详细定义在目录下的__init__.py中
#enable: 控制不带参数运行main.py时，调度哪一个爬虫任务
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
        'enable' : False,
    }
}
