#在wsgi文件中的项目引入
import sys
 
sys.path.insert(0, "C:\Users\lvxinyue\PycharmProjects\Universe") #项目路径
 
from Universe import app #将我们的flask项目project名引入

application = app