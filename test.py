# 导入数据库模块
import pymysql
# 导入Flask框架，这个框架可以快捷地实现了一个WSGI应用。
# flask can be a web server in backend.
from flask import Flask, url_for
# 默认情况下，flask在程序文件夹中的templates子文件夹中寻找模块
from flask import render_template,redirect  # 先引入index.html，同时根据后面传入的参数，对html进行修改渲染。
# 导入前台请求的request模块
from flask import request
import traceback
import json
import os.path




