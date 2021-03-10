from flask import Flask, render_template, request, redirect, url_for
from flask_mongoengine import MongoEngine
from datetime import datetime
import mongoengine as me
from mongoengine import ListField,EmbeddedDocumentField,EmbeddedDocument
from mongoengine import *
from bson.objectid import ObjectId

app = Flask(__name__)
title = "Task-Manager"
heading = "Task-Manager"

app.config['MONGODB_SETTINGS'] = {  # connection to databse
    'db': 'mydb1',
    'host': 'localhost',
    'port': 27017
}
db = MongoEngine()
db.init_app(app)  # creates the object of database connection

count=1
user=None
admin=None
class Task(me.EmbeddedDocument):  # creating database model
    tid = me.IntField(default=0)
    name = me.StringField(max_length=200, required=True)
    desc = me.StringField(max_length=250, required=True)
    comments = me.StringField(max_length=250, required=True)
    priority = me.IntField(default=5)
    date = me.DateTimeField(default=datetime.utcnow())
    status = me.BooleanField(default=False)
    
class User(me.Document):
    Uname = me.StringField(max_length=200, required=True)
    Password = me.StringField(max_length=200, required=True)
    Tasks = me.ListField(EmbeddedDocumentField(Task))

class Admin(me.Document):
    AdminName = me.StringField(max_length=200, required=True)
    AdminPass = me.StringField(max_length=200, required=True)
    Tasks = me.ListField(EmbeddedDocumentField(Task))
    Users = me.ListField(me.ReferenceField(User))

# task1 = Task(name="t1",desc="description1",comments="some comment1",priority=1)
# task2 = Task(name="t2",desc="description2",comments="some comment2",priority=2)
# task3 = Task(name="t3",desc="description3",comments="some comment3",priority=3)

# user1=User(Uname="Irfan",Password="irfan")
# user1.Tasks = [task1,task2]
# user1.save()
# user2=User(Uname="Mohit",Password="mohit")
# user2.Tasks = [task3]
# user2.save()

# Admin_Task1 = Task(tid=1,name="t4",desc="description4",comments="some comment4",priority=4)
# Admin_Task2 = Task(tid=2,name="t5",desc="description5",comments="some comment5",priority=5)
# Admin_Task3 = Task(tid=3,name="t6",desc="description6",comments="some comment6",priority=6)

# AdminName = "roshan"
# AdminPass = "roshan"
# users = [user1,user2]
# tasks = [Admin_Task1,Admin_Task2,Admin_Task3]
# new_admin= Admin(AdminName=AdminName,AdminPass=AdminPass,Tasks=tasks,Users=users)
# new_admin.save() 

def redirect_url():
    return request.args.get('next') or request.referrer or url_for('index')

def getUser():
    global user
    return user

def setUser(u1):
    global user
    user=u1

def getAdmin():
    global admin
    return admin

def setAdmin(a1):
    global admin
    admin=a1

@app.route('/', methods=['POST', 'GET'])  # default routing function
def login():
    a1 = "active"
    if request.method == 'GET':        
        return render_template('login.html')
    else:
        # return render_template('index.html')
        Uname = request.form['Uname']
        Password = request.form['Pass']
        Error = False
        User1=User.objects(Uname=Uname,Password=Password).first()
        Admin1=Admin.objects(AdminName=Uname,AdminPass=Password).first()
        setAdmin(Admin1)
        setUser(User1)
        if User1:
            #return render_template('index.html',user=User1,Error=Error,a1=a1)
            return redirect('/tasks')
        elif Admin1:
            return redirect('/admin')
        else:
            Error = True
            return render_template('login.html',Error=Error)    

@app.route('/admin', methods=['POST','GET'])
def Admin1():
    if request.method == "GET":
        admin=getAdmin()
        Admin1=Admin.objects(AdminName="roshan").first()
        print(Admin1.Users[0].Uname)
        return render_template('adminhome.html',admin=Admin1,task1=False,all=True)
    else:
        return render_template('adminhome.html',admin=Admin1,task1=False,all=True)


@app.route('/addmember', methods=['POST','GET'])
def Addmember():
    if request.method == "POST":
        admin=getAdmin()
        Admin1=Admin.objects(AdminName="roshan").first()
        Uname=request.form['Uname']
        Pass=request.form['Pass']
        new_user= User(Uname=Uname,Password=Pass)
        new_user.save()
        users = [new_user]
        Admin1.Users.append(new_user)
        Admin1.save()
        return redirect('/admin')
    else:
        return render_template('addmember.html')


@app.route('/addtasks/<id>', methods=['POST','GET'])
def AddTasks(id):
    if request.method == "GET":
        admin=getAdmin()
        Admin1=Admin.objects(AdminName="roshan").first()
        #print(Admin1.Tasks[0].name)
        return render_template('adminhome.html',admin=Admin1,task1=True,all=False)
    else:
        Admin3 = Admin.objects.get(id=id)
        global count
        task_id = count
        increment()  
        task_name = request.form['name']  # get the data from form  and
        task_desc = request.form['desc']
        task_comments = request.form['comments']
        task_priority = request.form['priority']
        new_task=Task(tid=task_id,name=task_name,desc=task_desc,comments=task_comments,priority=task_priority) 
        Admin3.Tasks.append(new_task)
        Admin3.save()         
        try:          
            return render_template('adminhome.html',admin=Admin3,task1=True,all=False)
        except:
            return 'There was an while issue adding your task you messed up bruh!!!'


@app.route("/pendingAdmin/<uname>")
def tasksAdmin(uname):
    # Display the Pending Tasks
    admin = Admin.objects.filter(AdminName=uname,Tasks__status=False).first()
    #print(user.Tasks[0].name)
    a2 = "active"
    return render_template('adminhome.html',admin=admin,a2=a2)


@app.route("/completedAdmin/<uname>")
def completedAdmin(uname):
    # Display the Completed Tasks
    admin = Admin.objects.filter(AdminName=uname,Tasks__status=True).first()
    a3 = "active"
    return render_template('adminhome.html', a3=a3, admin=admin)


@app.route('/doneAdmin/<id>/<uname>')  # updating status of task by id
def doneAdmin(id,uname):
    a1 = "active"
    Admin2 = Admin.objects(AdminName=uname).first()
    Admin3 = Admin.objects(AdminName=uname, Tasks__tid=id).update(set__Tasks__S__status=True)
    try:
        return redirect('/addtasks/id')
    except:
        return 'There was an issue updating your task'

@app.route('/undoAdmin/<id>/<uname>')  # updating status of stored task by id
def undoAdmin(id,uname):
    Admin2 = Admin.objects(AdminName=uname).first()
    Admin3 = Admin.objects(AdminName=uname, Tasks__tid=id).update(set__Tasks__S__status=False)
    try:
        return redirect('/addtasks/id')
    except:
        return 'There was an issue updating your task'


@app.route('/deleteAdmin/<id>/<uname>')  # deleting task by id
def deleteAdmin(id,uname):
    Admin2 = Admin.objects(AdminName=uname).first()
    Admin2.update(pull__Tasks__tid=id)
    try:
        return redirect('/addtasks/id')
    except:
        return 'There was an issue while deleting your task'


@app.route('/updateAdmin/<id>/<uname>', methods=['POST', 'GET'])  # updating stored task by id
def updateAdmin(id,uname):
    Error = False
    Admin2 = Admin.objects(AdminName=uname).first()
    for task in Admin2.Tasks:
        if task.tid == int(id):
            selected_task=task

    if request.method == 'POST':  # if method is POST then
        tname = request.form['name']  # getting new content from form and set into databse
        tdesc = request.form['desc']
        tcomments = request.form['comments']
        tpriority = request.form['priority']
        Admin1 = Admin.objects(AdminName=uname, Tasks__tid=id).update(set__Tasks__S__name=tname)
        Admin1 = Admin.objects(AdminName=uname, Tasks__tid=id).update(set__Tasks__S__desc=tdesc)            
        Admin1 = Admin.objects(AdminName=uname, Tasks__tid=id).update(set__Tasks__S__comments=tcomments) 
        Admin1 = Admin.objects(AdminName=uname, Tasks__tid=id).update(set__Tasks__S__priority=tpriority) 
        try:   
            return redirect('/addtasks/id')
            #return render_template('index.html',user=User2,a1 = "active")
        except:
            return 'There was an issue while updating your task'
    else:
        return render_template('updateadmin.html',admin=Admin2,task=selected_task,id=id)  # if method is GET then redirect requet to update page to get the new content
        

@app.route('/assign/<id>', methods=['POST', 'GET'])  # updating stored task by id
def assign(id):
    admin=getAdmin()
    Admin2=Admin.objects(AdminName="roshan").first()
    if request.method == 'POST':  # if method is POST then
        try:   
            return redirect('/addtasks/id')
            #return render_template('index.html',user=User2,a1 = "active")
        except:
            return 'There was an issue while updating your task'
    else:
 
       return render_template('assign.html',admin=Admin2,tid=id)  # if method is GET then redirect requet to update page to get the new content

@app.route('/assign/<id>/<uname>', methods=['POST', 'GET'])  # updating stored task by id
def assign2(id,uname):
    admin=getAdmin()
    Admin2=Admin.objects(AdminName="roshan").first()
    for task in Admin2.Tasks:
        if task.tid == int(id):
            sel_task=task
    User2=User.objects(Uname=uname).first()
    setUser(User2)
    new_task=Task(tid=sel_task.tid,name=sel_task.name,desc=sel_task.desc,comments=sel_task.comments,priority=sel_task.priority) 
    User2.Tasks.append(new_task)
    User2.save()  
    Admin2.update(pull__Tasks__tid=id)
    if request.method == 'POST':  # if method is POST then
        try:   
            return redirect('/addtasks/id')
            #return render_template('index.html',user=User2,a1 = "active")
        except:
            return 'There was an issue while updating your task'
    else:
        return redirect('/addtasks/id')  # if method is GET then redirect requet to update page to get the new content



#
#___________________________________________________________________________________________________________________________
#----------------------------------------------------------------------------------------------------------------------------
#
#__________________________________________________________________________________________________________________________ 
#---------------------------------------------------------------------------------------------------------------------------
# 
#

@app.route('/tasks', methods=['POST','GET'])
def Tasks():
    user = getUser()
    User1 = User.objects(Uname=user.Uname).first()
    if request.method == "GET":
        return render_template('index.html',user=User1,a1="active")
    else:
        return render_template('index.html', user=User1,a1="active")


@app.route('/register',methods=['POST','GET'])
def register():
    if request.method == "POST":
        Uname=request.form['Uname']
        Pass=request.form['Pass']

        new_user= User(Uname=Uname,Password=Pass)
        new_user.save()
        return redirect('/')
    else:
        return render_template('register.html')

def increment():
    global count
    count += 1

@app.route('/add/<id>', methods=['POST', 'GET'])  # default routing function
def add(id):
    a1 = "active"
    if request.method == 'POST':  # if method is POST
        User3 = User.objects.get(id=id)
        global count
        task_id = count
        increment()  
        task_name = request.form['name']  # get the data from form  and
        task_desc = request.form['desc']
        task_comments = request.form['comments']
        task_priority = request.form['priority']
        new_task=Task(tid=task_id,name=task_name,desc=task_desc,comments=task_comments,priority=task_priority) 
        User3.Tasks.append(new_task)
        User3.save()         
        try:          
            return redirect('/tasks')
        except:
            return 'There was an while issue adding your task you messed up bruh'
    else:
        return render_template('index.html')


@app.route("/pending/<uname>")
def tasks(uname):
    # Display the Pending Tasks
    user = User.objects.filter(Uname=uname,Tasks__status=False).first()
    #print(user.Tasks[0].name)
    a2 = "active"
    return render_template('index.html',user=user,a2=a2)


@app.route("/completed/<uname>")
def completed(uname):
    # Display the Completed Tasks
    user = User.objects.filter(Uname=uname,Tasks__status=True).first()
    a3 = "active"
    return render_template('index.html', a3=a3, user=user)


@app.route('/done/<id>/<uname>')  # updating status of task by id
def done(id,uname):
    a1 = "active"
    User2 = User.objects(Uname=uname).first()
    User3 = User.objects(Uname=uname, Tasks__tid=id).update(set__Tasks__S__status=True)
    try:
        return redirect('/tasks')
    except:
        return 'There was an issue updating your task'

@app.route('/undo/<id>/<uname>')  # updating status of stored task by id
def undo(id,uname):
    User2 = User.objects(Uname=uname).first()
    User3 = User.objects(Uname=uname, Tasks__tid=id).update(set__Tasks__S__status=False)
    try:
        return redirect('/tasks')
    except:
        return 'There was an issue updating your task'


@app.route('/delete/<id>/<uname>')  # deleting task by id
def delete(id,uname):
    User2 = User.objects(Uname=uname).first()
    User2.update(pull__Tasks__tid=id)
    try:
        return redirect('/tasks')
    except:
        return 'There was an issue while deleting your task'


@app.route('/update/<id>/<uname>', methods=['POST', 'GET'])  # updating stored task by id
def update(id,uname):
    Error = False
    User2 = User.objects(Uname=uname).first()
    for task in User2.Tasks:
        if task.tid == int(id):
            selected_task=task

    if request.method == 'POST':  # if method is POST then
        tname = request.form['name']  # getting new content from form and set into databse
        tdesc = request.form['desc']
        tcomment = request.form['comment']
        tpriority = request.form['priority']
        User1 = User.objects(Uname=uname, Tasks__tid=id).update(set__Tasks__S__name=tname)
        User1 = User.objects(Uname=uname, Tasks__tid=id).update(set__Tasks__S__desc=tdesc)            
        User1 = User.objects(Uname=uname, Tasks__tid=id).update(set__Tasks__S__comment=tcomment) 
        User1 = User.objects(Uname=uname, Tasks__tid=id).update(set__Tasks__S__priority=tpriority) 
        try:   
            return redirect('/tasks')
            #return render_template('index.html',user=User2,a1 = "active")
        except:
            return 'There was an issue while updating your task'
    else:
        return render_template('update.html',user=User2,task=selected_task,id=id)  # if method is GET then redirect requet to update page to get the new content



if __name__ == "__main__":
    app.run(debug=True)
