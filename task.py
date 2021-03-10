from flask import Flask, render_template, request, redirect, url_for
from flask_mongoengine import MongoEngine
from datetime import datetime
import mongoengine as me
from mongoengine import *

app = Flask(__name__)
title = "Task Manager"
heading = "Task Manager"

app.config['MONGODB_SETTINGS'] = {  # connection to databse
    'db': 'mydb',
    'host': 'localhost',
    'port': 27017
}

db = MongoEngine()
db.init_app(app)  # creates the object of database connection

count=1
user=None

class Task(me.EmbeddedDocument):  # creating database model
    tid = me.IntField(default=0)
    name = me.StringField(max_length=100, required=True)
    desc = me.StringField(max_length=200, required=True)
    date = me.DateTimeField(default=datetime.utcnow())
    status = me.BooleanField(default=False)

class User(me.Document):
    Uname = me.StringField(max_length=200, required=True)
    Password = me.StringField(max_length=200, required=True)
    Tasks = me.ListField(EmbeddedDocumentField(Task))


def redirect_url():
    return request.args.get('next') or request.referrer or url_for('index')

def getUser():
    global user
    return user

def setUser(u1):
    global user
    user=u1


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
        setUser(User1)
        if User1:
            return render_template('index.html',user=User1,Error=Error,a1="active")
            #return redirect('/tasks')
        else:
            Error = True
            return render_template('login.html',Error=Error)    
    
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
        new_task=Task(tid=task_id,name=task_name,desc=task_desc) 
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
        User1 = User.objects(Uname=uname, Tasks__tid=id).update(set__Tasks__S__name=tname)
        User1 = User.objects(Uname=uname, Tasks__tid=id).update(set__Tasks__S__desc=tdesc)            
        try:   
            return redirect('/tasks')
            #return render_template('index.html',user=User2,a1 = "active")
        except:
            return 'There was an issue while updating your task'
    else:
        return render_template('update.html',user=User2,task=selected_task,id=id)  # if method is GET then redirect requet to update page to get the new content


if __name__ == "__main__":
    app.run()
