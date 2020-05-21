from flask import Flask,session,request,redirect,render_template,url_for,flash,jsonify
from datetime import timedelta,datetime
from flask_pymongo import PyMongo

app=Flask(__name__)
app.config["MONGO_URI"]="mongodb://localhost:27017/GoChat"
db=PyMongo(app).db
app.secret_key="cD7nTw3jF4cwA1dv"
app.permanent_session_lifetime=timedelta(days=10)

@app.route("/",methods=["GET","POST"])
def logreg():
    if request.method=="POST":
        if request.form.get("login","0")!="0":
            return redirect(url_for("login"))
        return redirect(url_for("register"))
    if "handle" in session.keys():
        return redirect(url_for("profile"))
    return render_template("logreg.html")

@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        usr=db.users.find_one({"handle":request.form["handle"]})
        if usr==None or usr["password"]!=request.form["password"]:
            return render_template("login.html")
        session.permanent=True
        session["handle"]=request.form["handle"]
        return redirect(url_for("profile"))
    if "handle" in session.keys():
        return redirect(url_for("profile"))
    return render_template("login.html")

@app.route("/register",methods=["GET","POST"])
def register():
    if request.method=="POST":
        u1=db.users.find_one({"handle":request.form["handle"]})
        u2=db.users.find_one({"handle":request.form["email"]})
        if u1==None and u2==None:
            db.users.insert_one({"name":request.form["name"],"password":request.form["password"],"email":request.form["email"],"handle":request.form["handle"],"chats":{},"friends":[],"requests":[]})
            return redirect(url_for("login"))
        return render_template("register.html")
    if "handle" in session.keys():
        return redirect(url_for("profile"))
    return render_template("register.html")

@app.route("/profile",methods=["GET","POST"])
def profile():
    if "handle" in session.keys():
        return render_template("profile.html",usr=db.users.find_one({"handle":session["handle"]}))
    return redirect(url_for("logreg"))

@app.route("/send",methods=["GET","POST"])
def sendRequest():
    if request.method=="POST":
        h=session["handle"]
        rh=request.form["rhandle"]
        u=db.users.find_one({"handle":rh})
        if u!=None:
            me=db.users.find_one({"handle":h})
            if h not in u["friends"] and h not in u["requests"] and rh!=h and rh not in me["friends"] and rh not in me["requests"]:
                db.users.update_one({"handle":rh},{"$push":{"requests":h}})
        return redirect(url_for("profile"))
    if "handle" in session.keys():
        return render_template("sendreq.html")
    return redirect(url_for("logreg"))

@app.route("/<user>")
def view(user):
    if "handle" in session.keys():
        u=db.users.find_one({"handle":user})
        return render_template("view.html",user=u)
    return render_template("404.html")

@app.route("/<sndr>/<rcvr>")
def chat(sndr,rcvr):
    u=db.users.find_one({"handle":sndr})
    if sndr==session["handle"] and rcvr in u["friends"]:
        return render_template("chat.html",u1=u,u2=rcvr)
    return redirect(url_for("logreg"))

@app.route("/logout")
def logout():
    session.pop("handle",None)
    return redirect(url_for("logreg"))

@app.route("/accept",methods=["POST"])
def accept():
    mh=session["handle"]
    rh=request.form["handle"]
    db.users.update_one({"handle":mh},{"$push":{"friends":rh},"$pull":{"requests":rh}})
    db.users.update_one({"handle":rh},{"$push":{"friends":mh}})
    return jsonify({"status":"OK"})

@app.route("/sndrcv",methods=["POST"])
def sndrcv():
    s=session["handle"]
    r=request.form["rcvr"]
    m=request.form["msg"]
    d=datetime.now()
    dd=str(d.day)+"/"+str(d.month)+"/"+str(d.year)+" "+str(d.hour)+":"+str(d.minute)+":"+str(d.second)
    db.users.update_one({"handle":s},{"$push":{"chats."+r:(m,dd,1)}})
    db.users.update_one({"handle":r},{"$push":{"chats."+s:(m,dd,0)}})
    return jsonify({"timestamp":dd,"sender":s})

if __name__=="__main__":
    app.run(debug=True,host="0.0.0.0")