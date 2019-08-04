# 导入数据库模块
import pymysql
# 导入Flask框架，这个框架可以快捷地实现了一个WSGI应用。
# flask can be a web server in backend.
from flask import Flask, url_for
# 默认情况下，flask在程序文件夹中的templates子文件夹中寻找模块
from flask import render_template,redirect  # 先引入index.html，同时根据后面传入的参数，对html进行修改渲染。
# 导入前台请求的request模块
from flask import Response
from flask import request
from flask import jsonify
import traceback
import json
import os
from functools import wraps
from flask import make_response
from flask_cors import *
import time
import datetime
import base64
from werkzeug.utils import secure_filename
from flask import send_from_directory,abort
from werkzeug.security import generate_password_hash,check_password_hash

# 传递根目录
app = Flask(__name__, static_folder='static')

# CORS(app, resources=r'/*')

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,session_id')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS,HEAD')
    # 这里不能使用add方法，否则会出现 The 'Access-Control-Allow-Origin' header contains multiple values 的问题
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

#action changed, and then url change, but html is still remain.
# default page: load html page to browser
@app.route('/')
def loginRaw():# 'online==1' conflict #???????? conflict: add friend , skip to login.html ????
        return render_template('login.html')  # seach the template file
    # This function is aimed to dispaly HTML
    # if skip to login.html, server will run the function:login(), which can achieve page's function
    # 'return' can skip page
    #return render_template('upload.html')


# 获取登录参数及处理
@app.route('/login', methods=['POST'])
def login():
    data=json.loads(request.get_data())
    userID1=data["registerId"]
    password1=data["password"]

    # 查询用户名及密码是否匹配及存在
    # 连接数据库
    db = pymysql.connect("localhost", "root", "lvxinyue", "Universe")
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    # SQL 查询语句
    sql = "select * from user where userID='{0}'".format(userID1)
    try:
        # 执行sql语句
        cursor.execute(sql)
        results = cursor.fetchall()  # 接收全部的返回结果行

        dic = {}
        if len(results) == 1:
                print(userID1)
                sql='UPDATE user SET onLine = 1 WHERE userID = ("%s")'% (userID1)#set user online
                cursor.execute(sql)
                db.commit()#important!!
                # print(results[0][2])
                a=check_password_hash(results[0][2],password1)
                # print(a)
                if a:
                    dic['loginState'] = 1
                else:
                    dic['loginState'] = 0
        else:
                dic['loginState'] = 0

        json_str = json.dumps(dic, separators=(',', ':'), ensure_ascii=False)
        return json_str  # must return something, cause of ajax!

        # 提交到数据库执行
        db.commit()
    except:
        # 如果发生错误则回滚
        traceback.print_exc()
        db.rollback()
    # 关闭数据库连接
    db.close()

@app.route('/chatRaw')
def chatRaw():
    return render_template('chat.html')

# load register page to browser
@app.route('/registerRaw')
def registerRaw():
    return render_template('register.html')

@app.route('/judgeUserIDUniqueOrNot', methods=['POST'])
def judgeUserIDUniqueOrNot():
    data = json.loads(request.get_data())
    print(data['RegisterUserID'])

    # 连接数据库
    db = pymysql.connect("localhost", "root", "lvxinyue", "Universe")
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    # judge userId unique
    sql = "select * from user where userID=('%s')" % (data['RegisterUserID'])
    cursor.execute(sql)
    result = cursor.fetchall()  # all friends

    if len(result)==0:#unique
        dic = {'uniqueOrNot':1}
    else:
        dic = {'uniqueOrNot': 0}

    json_str = json.dumps(dic, separators=(',', ':'), ensure_ascii=False)  # dic-->str/json
    return json_str


# 获取注册请求及处理
@app.route('/register', methods=['POST'])
def register():
    data = json.loads(request.get_data())
    userID1 = data["registerId"]
    password = data["password"]

    password1 = generate_password_hash(password)
    print(password1)

    # 连接数据库
    db = pymysql.connect("localhost", "root", "lvxinyue", "Universe")
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()


    # 把用户名和密码写入到数据库中
    # SQL 插入语句
    sql = "INSERT INTO user(userID, password,onLine) VALUES (%s, %s,0)"
    userID = userID1
    password = password1
    values = (userID, password)

    # 执行sql语句
    cursor.execute(sql, values)
    # 提交到数据库执行
    db.commit()
    # 注册成功之后跳转到登录页面
    db.close()

    dic={}
    json_str = json.dumps(dic, separators=(',', ':'), ensure_ascii=False)  # dic-->str/json
    return json_str


#middle online friends display
@app.route('/friendsOnline', methods=['GET','POST'])
def friendsOnline():
    #当浏览器请求某网站时，会将本网站下所有Cookie信息提交给服务器
    #pay attention to cookie's logic
    currentUserIDRaw = request.cookies.get('userID')

    db = pymysql.connect("localhost", "root", "lvxinyue", "Universe")
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    sql = "select * from friends where userID=('%s')"%(currentUserIDRaw)
    cursor.execute(sql)
    results = cursor.fetchall()  # all friends
    friendsNum=len(results)

    friends = []
    for i in range(0, friendsNum):
        friends.append(results[i][1])

    onlineUserNum=0#the number of friends online
    value = []
    for j in range(0,friendsNum):
        sql = "select * from user where onLine=1 and userID=('%s')" % (friends[j])
        cursor.execute(sql)
        result = cursor.fetchall()#after friend，then confirm online
        if len(result)==1:
            value.append(result[0][1])#!!!!important: add element in the end of list
            onlineUserNum+=1

    dic={}
    for i in range(0, onlineUserNum):
        dic[i]=value[i]

    json_str=json.dumps(dic, separators=(',', ':'), ensure_ascii=False)#dic-->str/json
    return json_str

#click one of middle online friends
@app.route('/sendMessage',methods=['POST'])
#actually, data is sent to mysql
def sendMessage():
    # receive前端发来的content
    #only the receiver is online, the message can be sent successfully.
    data = json.loads(request.get_data())

    senderID1=request.cookies.get('userID')
    receiverID1=data['receiverID']
    time1=data['time']
    content1=data['content']

    print(senderID1,receiverID1,time1,content1)

    # 连接数据库
    db = pymysql.connect("localhost", "root", "lvxinyue", "Universe")
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    # SQL 插入语句
    sql = "INSERT INTO record(content,time,receiverID,senderID) VALUES (%s, %s, %s, %s)"
    content=content1
    time = time1
    receiverID = receiverID1
    senderID=senderID1
    values = (content,time,receiverID,senderID)
    try:
        # 执行sql语句
        cursor.execute(sql, values)
        # 提交到数据库执行
        db.commit()
    except:
        # 抛出错误信息
        traceback.print_exc()
        # 如果发生错误则回滚
        db.rollback()
    # 关闭数据库连接
    db.close()

    dic = {}
    json_str = json.dumps(dic, separators=(',', ':'), ensure_ascii=False)
    return json_str  # must return something, cause of ajax!

@app.route('/displayAllFriends',methods=['POST'])
def displayAllFriends():
    # 当浏览器请求某网站时，会将本网站下所有Cookie信息提交给服务器
    # pay attention to cookie's logic
    myCookies = request.cookies.get('userID')
    currentUserIDRaw = myCookies
    print(currentUserIDRaw)
    # currentUserID=int(currentUserIDRaw)#int

    db = pymysql.connect("localhost", "root", "lvxinyue", "Universe")
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    sql = "select * from friends where userID=('%s')"%(currentUserIDRaw)
    cursor.execute(sql)
    results = cursor.fetchall()  # all friends
    friendsNum = len(results)

    print(results)

    dic = {}
    for i in range(0, friendsNum):
        dic[i] = results[i][1]

    json_str = json.dumps(dic, separators=(',', ':'), ensure_ascii=False)  # dic-->str/json
    db.close()
    return json_str

@app.route('/judgeFriendOnlineOrNot',methods=['get','post'])
def judgeFriendOnlineOrNot():
    userID = request.cookies.get('userID')
    # print(type(userID))

    data = json.loads(request.get_data())
    # print(data)

    # 连接数据库
    db = pymysql.connect("localhost", "root", "lvxinyue", "Universe")
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    # get whether the friend is online
    sql1 = "select * from user where userID=('%s') " % (data['senderID'])
    cursor.execute(sql1)
    result = cursor.fetchall()  # unreceived message
    onlineOrNot = str(result[0][3])
    print(type(onlineOrNot))

    dic={}
    dic['onlineOrNot'] = onlineOrNot

    json_str = json.dumps(dic, separators=(',', ':'), ensure_ascii=False)
    return json_str  # must return something, cause of ajax!

@app.route('/receiveMessage',methods=['get','post'])
def receiveMessage():
    userID=request.cookies.get('userID')
    # print(type(userID))

    data = json.loads(request.get_data())
    # print(data)

    # 连接数据库
    db = pymysql.connect("localhost", "root", "lvxinyue", "Universe")
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    if(data['senderID']!='' and data['senderID']!='blank'):
        #get whether the friend is online
        sql1 = "select * from user where userID=('%s') "% (data['senderID'])
        cursor.execute(sql1)
        result = cursor.fetchall() # unreceived message
        onlineOrNot=str(result[0][3])
        print("onlineOrNot",onlineOrNot)

        #select unread message
        sql = "select * from record where received=0 and senderID=('%s') and receiverID=('%s')" % (data['senderID'],userID)
        cursor.execute(sql)
        results = cursor.fetchall()  # unreceived message
        messageNum=len(results)

        # #delete readed message from DB
        # sql = "delete from record where senderID=('%s') and receiverID=('%s')" % (data['senderID'], userID)
        # cursor.execute(sql)
        # db.commit()  # important!!
        # SQL update
        sql = 'UPDATE record SET received = 1 WHERE receiverID = ("%s")' % (userID)  # set user online
        cursor.execute(sql)
        db.commit()  # important!!

        dic = {}
        if messageNum!= 0:
            for i in range(0,messageNum):
                if results[i][1]==0:# receive text
                    dic[onlineOrNot]=results[i][2]
                elif results[i][1]==1:#file
                    dic[onlineOrNot + '1111111'] = results[i][2]#content
                elif results[i][1]==2: #video request
                    dic[onlineOrNot + '2222222'] = results[i][4]#senderID
                elif results[i][1] == 3: #video reply
                    dic[onlineOrNot + '3333333'] = results[i][2] #agree/disagree
                elif results[i][1] == 4: #audio request
                    dic[onlineOrNot + '4444444'] = results[i][4] #senderID
                elif results[i][1] == 5: #audio reply
                    dic[onlineOrNot + '5555555'] = results[i][2] #agree/disagree
        else:
            dic = {'blank': 0}
            json_str = json.dumps(dic, separators=(',', ':'), ensure_ascii=False)
            return json_str  # must return something, cause of ajax!
            # 'blank' represent no new message in front

        print(dic,'1111111111111')

        db.close()  # important

        json_str = json.dumps(dic, separators=(',', ':'), ensure_ascii=False)
        return json_str  # must return something, cause of ajax!

#search friend from all friend according to keywords inputed by user
@app.route('/search',methods=['POST'])
def search():
    data = json.loads(request.get_data())

    # 当浏览器请求某网站时，会将本网站下所有Cookie信息提交给服务器
    # pay attention to cookie's logic
    currentUserIDRaw = request.cookies.get('userID')

    # print(type(currentUserIDRaw))
    # currentUserID=int(currentUserIDRaw)#int

    db = pymysql.connect("localhost", "root", "lvxinyue", "Universe")
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    sql = "select * from friends where userID=('%s')" % (currentUserIDRaw)
    cursor.execute(sql)
    results = cursor.fetchall()  # all friends
    friendsNum = len(results)

    dic = {}
    for i in range(0, friendsNum):
        if (results[i][1].find(data['searchContent'])) != -1:
            dic[i] = results[i][1]
    #print(dic)

    json_str = json.dumps(dic, separators=(',', ':'), ensure_ascii=False)
    return json_str  # must return something, cause of ajax!

@app.route('/addNewFriendRaw',methods=['get','post'])
def addNewFriendRaw():
    return render_template('addNewFriend.html')

#Determine if the friend to be added exists
@app.route('/addingFriendExistingOrNot',methods=['get','post'])
def addingFriendExistingOrNot():
    #Exist or not
    data = json.loads(request.get_data())

    # 当浏览器请求某网站时，会将本网站下所有Cookie信息提交给服务器
    # pay attention to cookie's logic
    currentUserIDRaw = request.cookies.get('userID')

    db = pymysql.connect("localhost", "root", "lvxinyue", "Universe")
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    dic={}#return to front
    #new friend is existing or not, and they are friends already or not
    sql = "select * from user where userID=('%s')" % (data['newFriend'])
    cursor.execute(sql)
    results = cursor.fetchall()  # all friends
    isUser = len(results)

    if isUser==0:
        dic['isExisting'] = -1
    else :
        sql1 = "select * from friends where userID=('%s') and friendsID=('%s')" % (data['newFriend'], currentUserIDRaw)
        cursor.execute(sql1)
        results = cursor.fetchall()  # all friends

        #print(results)
        isFriend = len(results)
        if isFriend==1:
            dic['isExisting'] = 0
            #print(dic)
        else:
            dic['isExisting'] = 1
            sql2='INSERT INTO newFriends(applicant,target) values (%s,%s)'
            applicant = currentUserIDRaw
            target = data['newFriend']
            values = (applicant,target)
            # 执行sql语句
            cursor.execute(sql2, values)
            # 提交到数据库执行
            db.commit()
            db.close()

    json_str = json.dumps(dic, separators=(',', ':'), ensure_ascii=False)
    return json_str  # must return something, cause of ajax!


@app.route('/displayNewFriendsList',methods=['get','post'])
def displayNewFriendsList():
    # 当浏览器请求某网站时，会将本网站下所有Cookie信息提交给服务器
    # pay attention to cookie's logic
    currentUserIDRaw = request.cookies.get('userID')

    db = pymysql.connect("localhost", "root", "lvxinyue", "Universe")
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    sql = "select * from newFriends where target=('%s')" % (currentUserIDRaw)
    cursor.execute(sql)
    results = cursor.fetchall()  # all friends
    #print(results)

    newFriendsNum = len(results)

    dic={}
    for i in range(0,newFriendsNum):
        dic[i]=results[i][1]
    #print(dic)

    json_str = json.dumps(dic, separators=(',', ':'), ensure_ascii=False)
    return json_str  # must return something, cause of ajax!


@app.route('/addNewFriend',methods=['get','post'])
def addNewFriend():
    data = json.loads(request.get_data())
    # 当浏览器请求某网站时，会将本网站下所有Cookie信息提交给服务器
    # pay attention to cookie's logic
    currentUserIDRaw = request.cookies.get('userID')
    #print(currentUserIDRaw)

    db = pymysql.connect("localhost", "root", "lvxinyue", "Universe")
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    if data['addOrNot']==1:
        #add 2 rows to friends
        sql = 'INSERT INTO friends(friendsID,userID) values (%s,%s)'
        friendsID = currentUserIDRaw
        userID = data['applicantID']
        values = (friendsID, userID)
        # 执行sql语句
        cursor.execute(sql, values)
        # 提交到数据库执行
        db.commit()

        sql = 'INSERT INTO friends(friendsID,userID) values (%s,%s)'
        friendsID = data['applicantID']
        userID = currentUserIDRaw
        values = (friendsID, userID)
        # 执行sql语句
        cursor.execute(sql, values)
        # 提交到数据库执行
        db.commit()

    sql = "DELETE FROM NEWFRIENDS WHERE applicant = ('%s') and target= ('%s')" % (data['applicantID'],currentUserIDRaw)
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 提交修改
        db.commit()
    except:
        # 发生错误时回滚
        db.rollback()

    db.close()

    dic = {}
    json_str = json.dumps(dic, separators=(',', ':'), ensure_ascii=False)
    return json_str  # must return something, cause of ajax!

#delete Friend
@app.route('/deleteFriend',methods=['get','post'])
def deleteFriend():
    #get:  ajax send data
    data = json.loads(request.get_data())
    # 当浏览器请求某网站时，会将本网站下所有Cookie信息提交给服务器
    # pay attention to cookie's logic
    currentUserIDRaw = request.cookies.get('userID')
    # print(currentUserIDRaw)

    db = pymysql.connect("localhost", "root", "lvxinyue", "Universe")
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    #delete FREIENDS TABLE
    sql = "DELETE FROM FRIENDS WHERE friendsID = ('%s') and userID=('%s')" % (data['deletedID'],currentUserIDRaw)
    cursor.execute(sql)
    db.commit()

    sql = "DELETE FROM FRIENDS WHERE friendsID = ('%s') and userID=('%s')" % (currentUserIDRaw,data['deletedID'])
    cursor.execute(sql)
    db.commit()

    db.close()

    dic = {}
    json_str = json.dumps(dic, separators=(',', ':'), ensure_ascii=False)
    return json_str  # must return something, cause of ajax!

#receive file sended by frontend
UPLOAD_FOLDER='upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
basedir = os.path.abspath(os.path.dirname(__file__))
ALLOWED_EXTENSIONS = set(['txt','png','jpg','xls','JPG','PNG','xlsx','gif','GIF'])

# 用于判断文件后缀
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS

# 上传文件
@app.route('/uploadFile', methods=['POST'])#, strict_slashes=False
def uploadFile():
    receiveFileUserId =request.values['friendId'] #'name' attribute!!!not 'id'!!!
    print(receiveFileUserId)

    # access background file: frontend access默认路由是static
    #app.config['UPLOAD_FOLDER']=url_for("static",filename="upload")
    #路径进行拼接
    file_dir = os.path.join(basedir, "static/fileMessage")
    print(file_dir)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    #f = request.files['myfile']  # 从表单的file字段获取文件，myfile为该表单的name值
    f=request.files["file"]
    print(f)

    if f and allowed_file(f.filename):  # 判断是否是允许上传的文件类型
        fname = f.filename #prevent文件名中文错误
        print(fname)
        ext = fname.rsplit('.', 1)[1]  # 获取文件后缀
        unix_time = int(time.time())
        #new_filename = str(unix_time) + '.' + ext  # 修改了上传的文件名
        print(file_dir,'1111111111111111')
        f.save(os.path.join(file_dir, fname))  # 保存文件到upload目录

    # 连接数据库
    db = pymysql.connect("localhost", "root", "lvxinyue", "Universe")
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    # SQL 插入语句
    sql = "INSERT INTO record(content,time,receiverID,senderID,messageType) VALUES ( %s,%s, %s, %s,1)"  # '1'-file,'0'-text
    # content = content1
    content=fname
    time1 = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(time1)
    receiverID = receiveFileUserId
    senderID = request.cookies.get('userID')
    values = (content,time1, receiverID, senderID)
    try:
        # 执行sql语句
        cursor.execute(sql, values)
        # 提交到数据库执行
        db.commit()
    except:
        # 抛出错误信息
        traceback.print_exc()
        # 如果发生错误则回滚
        db.rollback()
    # 关闭数据库连接
    db.close()

    dic = {}
    json_str = json.dumps(dic, separators=(',', ':'), ensure_ascii=False)
    return json_str

@app.route('/audioCallRequest', methods=['POST'])#, strict_slashes=False
def audioCallRequest():
    currentUserID = request.cookies.get('userID')
    data = json.loads(request.get_data())
    friendId = data['friendId']
    print(friendId)

    db = pymysql.connect("localhost", "root", "lvxinyue", "Universe")
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    dic = {}  # return to front
    # new friend is existing or not, and they are friends already or not
    sql = "select * from user where userID=('%s')" % (friendId)
    cursor.execute(sql)
    results = cursor.fetchall()  # all friends
    #friend not online
    if results[0][3]==0:
        dic = {'friendDeny': 'The friend is not online. Please wait a moment.'}
        json_str = json.dumps(dic, separators=(',', ':'), ensure_ascii=False)
        return json_str  # must return something, cause of ajax!
    else:#send audio call  request
        data = json.loads(request.get_data())

        senderID1 = request.cookies.get('userID')
        receiverID1 = data['friendId']
        time1 = data['time']
        content1 = data['content']

        print(senderID1, receiverID1, time1, content1)

        # 连接数据库
        db = pymysql.connect("localhost", "root", "lvxinyue", "Universe")
        # 使用cursor()方法获取操作游标
        cursor = db.cursor()
        # SQL 插入语句
        sql = "INSERT INTO record(content,time,receiverID,senderID,messageType) VALUES (%s, %s, %s, %s,4)"
        content = content1
        time = time1
        receiverID = receiverID1
        senderID = senderID1
        values = (content, time, receiverID, senderID)
        try:
            # 执行sql语句
            cursor.execute(sql, values)
            # 提交到数据库执行
            db.commit()
        except:
            # 抛出错误信息
            traceback.print_exc()
            # 如果发生错误则回滚
            db.rollback()
        # 关闭数据库连接
        db.close()

        dic = {'waitForFriendAnswer': 'waitForFriendAnswer'}
        json_str = json.dumps(dic, separators=(',', ':'), ensure_ascii=False)
        return json_str  # must return something, cause of ajax!

@app.route('/audioCallReply', methods=['POST'])#, strict_slashes=False
def audioCallReply():
    currentUserID = request.cookies.get('userID')
    data = json.loads(request.get_data())
    friendId = data['friendId']
    print(friendId)

    db = pymysql.connect("localhost", "root", "lvxinyue", "Universe")
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    dic = {}  # return to front
    # new friend is existing or not, and they are friends already or not
    sql = "select * from user where userID=('%s')" % (friendId)
    cursor.execute(sql)
    results = cursor.fetchall()  # all friends

    data = json.loads(request.get_data())

    senderID1 = request.cookies.get('userID')
    receiverID1 = data['friendId']
    time1 = data['time']
    content1 = data['content']

    # 连接数据库
    db = pymysql.connect("localhost", "root", "lvxinyue", "Universe")
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    # SQL 插入语句
    sql = "INSERT INTO record(content,time,receiverID,senderID,messageType) VALUES (%s, %s, %s, %s,5)"
    content = content1
    time = time1
    receiverID = receiverID1
    senderID = senderID1
    values = (content, time, receiverID, senderID)
    try:
        # 执行sql语句
        cursor.execute(sql, values)
        # 提交到数据库执行
        db.commit()
    except:
        # 抛出错误信息
        traceback.print_exc()
        # 如果发生错误则回滚
        db.rollback()
    # 关闭数据库连接
    db.close()

    dic = { }
    json_str = json.dumps(dic, separators=(',', ':'), ensure_ascii=False)
    return json_str  # must return something, cause of ajax!

@app.route('/videoCallRequest', methods=['POST'])#, strict_slashes=False
def videoCallRequest():
    currentUserID = request.cookies.get('userID')
    data = json.loads(request.get_data())
    friendId = data['friendId']
    print(friendId)

    db = pymysql.connect("localhost", "root", "lvxinyue", "Universe")
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    dic = {}  # return to front
    # new friend is existing or not, and they are friends already or not
    sql = "select * from user where userID=('%s')" % (friendId)
    cursor.execute(sql)
    results = cursor.fetchall()  # all friends
    if results[0][3]==0:
        dic = {'friendDenyNotOnline': 'The friend is not online. Please wait a moment.'}
        json_str = json.dumps(dic, separators=(',', ':'), ensure_ascii=False)
        return json_str  # must return something, cause of ajax!
    else:#send another client request
        data = json.loads(request.get_data())

        senderID1 = request.cookies.get('userID')
        receiverID1 = data['friendId']
        time1 = data['time']
        content1 = data['content']

        print(senderID1, receiverID1, time1, content1)

        # 连接数据库
        db = pymysql.connect("localhost", "root", "lvxinyue", "Universe")
        # 使用cursor()方法获取操作游标
        cursor = db.cursor()
        # SQL 插入语句
        sql = "INSERT INTO record(content,time,receiverID,senderID,messageType) VALUES (%s, %s, %s, %s,2)"
        content = content1
        time = time1
        receiverID = receiverID1
        senderID = senderID1
        values = (content, time, receiverID, senderID)
        try:
            # 执行sql语句
            cursor.execute(sql, values)
            # 提交到数据库执行
            db.commit()
        except:
            # 抛出错误信息
            traceback.print_exc()
            # 如果发生错误则回滚
            db.rollback()
        # 关闭数据库连接
        db.close()

        dic = {'waitForFriendAnswer': 'waitForFriendAnswer'}#no use
        json_str = json.dumps(dic, separators=(',', ':'), ensure_ascii=False)
        return json_str  # must return something, cause of ajax!


@app.route('/videoCallReply', methods=['POST'])#, strict_slashes=False
def videoCallReply():
    currentUserID = request.cookies.get('userID')
    data = json.loads(request.get_data())
    friendId = data['friendId']
    print(friendId)

    db = pymysql.connect("localhost", "root", "lvxinyue", "Universe")
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    dic = {}  # return to front
    # new friend is existing or not, and they are friends already or not
    sql = "select * from user where userID=('%s')" % (friendId)
    cursor.execute(sql)
    results = cursor.fetchall()  # all friends

    data = json.loads(request.get_data())

    senderID1 = request.cookies.get('userID')
    receiverID1 = data['friendId']
    time1 = data['time']
    content1 = data['content']

    # 连接数据库
    db = pymysql.connect("localhost", "root", "lvxinyue", "Universe")
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    # SQL 插入语句
    sql = "INSERT INTO record(content,time,receiverID,senderID,messageType) VALUES (%s, %s, %s, %s,3)"
    content = content1
    time = time1
    receiverID = receiverID1
    senderID = senderID1
    values = (content, time, receiverID, senderID)
    try:
        # 执行sql语句
        cursor.execute(sql, values)
        # 提交到数据库执行
        db.commit()
    except:
        # 抛出错误信息
        traceback.print_exc()
        # 如果发生错误则回滚
        db.rollback()
    # 关闭数据库连接
    db.close()

    dic = { }
    json_str = json.dumps(dic, separators=(',', ':'), ensure_ascii=False)
    return json_str  # must return something, cause of ajax!

@app.route('/video',methods=['get','post'])
def video():
    return render_template('audioRequest.html')

@app.route('/audioRaw',methods=['get','post'])
def audioRaw():
    return render_template('audioRequest.html')

@app.route('/exit',methods=['get','post'])
def exit():#no return
    # set online=0
    myCookies = request.cookies.get('userID')
    currentUserIDRaw = myCookies  # list ['x']
    # 连接数据库
    db = pymysql.connect("localhost", "root", "lvxinyue", "Universe")
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    #if not(request.cookies.get('userID')):
    # SQL update
    sql = 'UPDATE user SET onLine = 0 WHERE userID = ("%s")' % (currentUserIDRaw)  # set user online
    cursor.execute(sql)
    db.commit()  # important!!


    db.close()  # important

    # #delete cookie
    # path = r'C:\Users\lvxinyue\PycharmProjects\Universe\cookie.txt'

    dic = {}
    json_str = json.dumps(dic, separators=(',', ':'), ensure_ascii=False)
    return json_str# must return something, cause of ajax!

# 使用__name__ == '__main__'是 Python 的惯用法，确保直接执行此脚本时才启动服务器，若其他程序调用该脚本可能父级程序会启动不同的服务器
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
