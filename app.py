from flask import Flask, redirect,render_template,request,flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import LoginManager, UserMixin
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user,login_required,logout_user,current_user,login_manager



app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///database.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY']='Self-Tracking App by Sahastranshu'
db=SQLAlchemy(app)



class User( db.Model, UserMixin):
    id =db.Column(db.Integer, primary_key=True)
    email=db.Column(db.String(150),unique=True)
    password=db.Column(db.String(150),nullable=False)
    name=db.Column(db.String(150),nullable=False)
    trackers=db.relationship('Tracker')
    logs=db.relationship('Log')


class Tracker(db.Model):
    id =db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(150),nullable=False)
    description=db.Column(db.String(25000))
    type=db.Column(db.String(150),nullable=False)
    settings=db.Column(db.String(15000))
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'))
    logs=db.relationship('Log',cascade="all, delete")


class Log(db.Model):
    id =db.Column(db.Integer, primary_key=True)
    value=db.Column(db.String(150),nullable=False)
    note=db.Column(db.String(25000))
    time=db.Column(db.String(150),default=datetime.now().strftime('%Y-%m-%dT%H:%M:%S %Z %z'))
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'))
    tracker_id=db.Column(db.Integer,db.ForeignKey('tracker.id'))





login_manager=LoginManager()
login_manager.login_view='/signin'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))





@app.route("/")
@login_required
def index():
    freq_c={}
    type_c={"Numerical":0,"TimeDuration":0,"Boolean":0,"MultipleChoice":0}
    for tkr in current_user.trackers:
        freq_c[tkr]=len(tkr.logs)
        if tkr.type=="Numerical":
            type_c["Numerical"]+=1
        elif tkr.type=="Boolean":
            type_c["Boolean"]+=1
        elif tkr.type=="Time Duration":
            type_c["TimeDuration"]+=1
        else:
            type_c["MultipleChoice"]+=1
    freq = sorted(freq_c.items(), key=lambda x: x[1],reverse=True) 
    labels=""
    values=""
    for i in freq[:5]:
        labels+=".&."+ (i[0].name)
        values+=".&."+str(i[1])
    labels=labels[3:]
    values=values[3:]
   
    type="Numeric TimeDuration Boolean MultipleChoice"
    count=""
    for i in type_c.keys():
        count+=" "+str(type_c[i])
    count=count[1:]
    return render_template('dashBoard.html',user=current_user,values=values,labels=labels,type=type,count=count)
   


@app.route("/signin",methods=['GET','POST'])
def signin():
    if request.method=='POST':
        email=request.form.get("email")
        password=request.form.get("password")

        user=User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password,password):
                login_user(user)
                flash(" Signed in successfully !",category='success')
                return redirect('/')
            else:
                flash('Incorrect password!',category='error')
        else:
            flash("Email doesn't exist!",category='error')

    return render_template('signin.html')



@app.route("/signup",methods=['GET','POST'])
def signup():
    if request.method=='POST':
        new_name=request.form.get("new name")
        new_email=request.form.get("new email")
        new_password=request.form.get("new password")

        user=User.query.filter_by(email=new_email).first()
        if user:
            flash("Email already exists !",category='error')
        else:
            l=True
            e=True
            p=True
            if len(new_name)<3:
                flash("Name too short!",category='error')
                l=False
            if len(new_email)<6:
                flash("Email too short !",category='error')
                e=False
            if len(new_password)<4:
                flash("Password too short !",category='error')
                p=False
            if (l and p and e):
                new_user=User(email=new_email,name=new_name,password=generate_password_hash(new_password,method='sha256'))  
                db.session.add(new_user)
                db.session.commit()    
                login_user(new_user)
                flash("Signed up successfully !",category='success')
                return redirect('/')
    return render_template('signup.html')



@app.route("/signout")
@login_required
def signout():
    logout_user()
    return redirect('/signin')





@app.route("/addTracker",methods=['GET','POST'])
def addTrackers():
    if request.method=='POST':
        name=request.form.get("name")
        type=request.form.get("type")
        desc=request.form.get("description")
        setting=request.form.get("setting")
        for tkr in current_user.trackers:
            if tkr.name==name:
                flash("Tracker already exist !",category='error')
                break
        else:
            if len(name)<2:
                flash("Name too short!",category='error')
            elif type=="Multiple Choice" and setting=="":
                flash("Settings can't be empty. Please enter comma seperated values !",category='error')
            else:
                new_tracker=Tracker(name=name,type=type,description=desc,settings=setting,user_id=current_user.id)  
                db.session.add(new_tracker)
                db.session.commit()
                flash("Tracker added successfully !",category='success')    
                return redirect('/')
    return render_template('addTracker.html',user=current_user)


@app.route("/deleteTracker/<int:id>",methods=['GET','POST'])
def deleteTracker(id):
    curr_tkr=Tracker.query.filter_by(id=id).first()

    db.session.delete(curr_tkr)
    db.session.commit()
    return redirect('/')


@app.route("/updateTracker/<int:id>",methods=['GET','POST'])
def updateTracker(id):
    curr_tkr=Tracker.query.filter_by(id=id).first()
    if request.method=='POST':
        name=request.form.get("name")
        type=request.form.get("type")
        desc=request.form.get("description")
        setting=request.form.get("setting")
        if len(name)<2:
            flash("Name too short!",category='error')
        elif type=="Multiple Choice" and setting=="":
            flash("Settings can't be empty for Multiple Choice tracker!",category='error')
        else:
            curr_tkr.name=name
            curr_tkr.description=desc
            curr_tkr.settings=setting
            if curr_tkr.type!=type:
                curr_tkr.logs.clear()
                curr_tkr.type=type
            db.session.commit()
            flash("Tracker Updated successfully !",category='success')    
            return redirect(f'/tracker/{id}')
    return render_template('updateTracker.html',user=current_user,tkr=curr_tkr)





@app.route("/addLog/<int:id>",methods=['GET','POST'])
def addLog(id):
    curr_tkr=Tracker.query.filter_by(id=id).first()
    if request.method=='POST':
        value=request.form.get("value")
        note=request.form.get("note")
        time=request.form.get("time")
        if len(value)<1:
                flash("Please enter value !",category='error')
        else:
            new_log=Log(value=value,note=note,tracker_id=id,user_id=current_user.id,time=time)  
            db.session.add(new_log)
            db.session.commit()
            flash("Log added successfully !",category='success')    
            return redirect(f'/tracker/{id}')

    return render_template('addLog.html',user=current_user,tkr=curr_tkr,time=datetime.now().strftime('%Y-%m-%dT%H:%M:%S %Z %z'))


@app.route("/deleteLog/<int:id>",methods=['GET','POST'])
def deleteLog(id):
    curr_log=Log.query.filter_by(id=id).first()
    tkr_id=curr_log.tracker_id
    db.session.delete(curr_log)
    db.session.commit()
    return redirect(f'/tracker/{tkr_id}')


@app.route("/updateLog/<int:id>",methods=['GET','POST'])
def updateLog(id):
    curr_log=Log.query.filter_by(id=id).first()
    curr_tkr=Tracker.query.filter_by(id=curr_log.tracker_id).first()
    if request.method=='POST':
        value=request.form.get("value")
        note=request.form.get("note")
        if len(value)<1:
                flash("Please enter value !",category='error')
        else:
            curr_log.value=value
            curr_log.note=note
            db.session.commit()
            flash("Log updated successfully !",category='success')    
            return redirect(f'/tracker/{curr_tkr.id}')
    return render_template('updateLog.html',user=current_user,log=curr_log,tkr=curr_tkr)




@app.route("/tracker/<int:id>")
def tracker(id):
    curr_tkr=Tracker.query.filter_by(id=id).first()
    dLabel=""
    dValue=""
    dict={}
    if curr_tkr.type=='Numerical':
        for l in curr_tkr.logs:
            dValue+=" "+str(l.value)
    elif curr_tkr.type=="Time Duration":
        for l in curr_tkr.logs:
            dValue+=" "+l.value.replace(":",".")
    elif curr_tkr.type=='Boolean':
        dict={'True':1,'False':0}
        for l in curr_tkr.logs:
            if l.value=='True':
                dValue+=" "+'1'
            else:
                dValue+=" "+'0'
    else:
        v=-1
        for set in curr_tkr.settings.split(","):
            if set not in dict.keys():
                dict[set]=v+1
                v+=1 
        for l in curr_tkr.logs:
            dValue+=" "+str(dict[l.value])
    dValue=dValue[1:]

    for l in curr_tkr.logs:
        dLabel+=" "+l.time
    dLabel=dLabel[1:]
    print(dLabel.split(" "))
    if dict:
        return render_template('tracker.html',user=current_user,tkr=curr_tkr,dValue=dValue,dLabel=dLabel,dict=dict)
    return render_template('tracker.html',user=current_user,tkr=curr_tkr,dValue=dValue,dLabel=dLabel)


@app.route("/showAllLogs")
def showAllLogs():
    return render_template('showAll.html',user=current_user,tkr=-2)
@app.route("/showAllTrackers")
def showAllTrackers():
    return render_template('showAll.html',user=current_user,tkr=-1)
@app.route("/showAllLogs/<int:id>")
def showAllLogsT(id):
    curr_tkr=Tracker.query.filter_by(id=id).first()
    return render_template('showAll.html',user=current_user,tkr=curr_tkr)




if __name__=="__main__":
    app.run(debug=True,port=1000)


















    
