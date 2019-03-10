from flask import Flask,render_template,jsonify,Response,request,url_for,session,redirect

import mysql.connector




#flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = True

#routings

## Analyst
@app.route('/analystlogin',methods = ['GET', 'POST'])
def analystlogin():
    if request.method=="POST":
        session['username'] = request.form['username']
        return redirect(url_for('dashboard'))
    return render_template('analystlogin.html')

@app.route('/dashboard')
def dashboard():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="parth123",
        database="barco"
        )
    if 'username' in session:
        cursor = mydb.cursor()
        cursor.execute("SELECT count(*) as hcount from Hospitals")
        hcount=cursor.fetchone()
        cursor.execute("SELECT count(*) as dcount from Doctors")
        dcount=cursor.fetchone()
        cursor.execute("SELECT State,count(*) from Hospitals group by State")
        shospitals=cursor.fetchall()
        
        mydb.commit()

        return render_template('dashboard.html',result={'hcount':hcount[0],'dcount':dcount[0],'shospitalsstate':[i[0] for i in shospitals],'shospitalscount':[i[1] for i in shospitals]})
    return redirect(url_for('analystlogin'))

@app.route('/analystlogout')
def alogout():
    session.pop('username',None)
    return redirect(url_for('analystlogin'))
    
@app.route('/medicine_requirement')
def medreq():
    return render_template('medicine_requirement.html')

@app.route('/disease_pred')
def dispred():
    return render_template('prediction_disease.html')

@app.route('/doctor_requirement')
def docreq():
    return render_template('doctor_requirement.html')

## Patient
@app.route('/patientsignup',methods = ['GET', 'POST'])
def psignup():
    if request.method=="POST":
        aadhar = request.form['aadhar']
        age = request.form['age']
        bg = request.form['bg']
        email = request.form['email']
        name = request.form['name']
        password = request.form['password']

        mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="parth123",
        database="barco"
        )
    
        cursor = mydb.cursor()
        cursor.execute("INSERT INTO `Patients` (`id`, `Aadhar`, `Age`, `Blood_Group`, `email`, `name`, `password`) VALUES (NULL, '{}', '{}', '{}', '{}', '{}', '{}')".format(aadhar,age,bg,email,name,password))
        cursor.fetchone()
        mydb.commit()
        return redirect(url_for('patientlogin'))
    return render_template('patientsignup.html')

@app.route('/patientlogin',methods = ['GET', 'POST'])
def patientlogin():
    if request.method=="POST":
        aadhar = request.form['aadhar']
        password = request.form['password']

        mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="parth123",
        database="barco"
        )
    
        cursor = mydb.cursor()
        cursor.execute("SELECT * FROM Patients where Aadhar='{}' and password='{}'".format(aadhar,password))
        pdetails=cursor.fetchall()
        print(pdetails)
        mydb.commit()
        if(len(pdetails)==1) :
            session['patientuser']=pdetails[0][1]
            print(session['patientuser'])
            return redirect(url_for('patientdashboard'))
        
    return render_template('patientlogin.html')

@app.route('/patientlogout')
def patientlogout():
    session.pop('patientuser',None)
    return redirect(url_for('patientdashboard'))


@app.route('/patientdashboard')
def patientdashboard():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="parth123",
        database="barco"
        )
    if 'patientuser' in session:
        patientuser = session['patientuser']
        cursor = mydb.cursor()
        cursor.execute("SELECT count(*) from Reservations where Patient_id in (Select id from Patients where Aadhar='{}') and status=1".format(session['patientuser']))
        countar=cursor.fetchone()
        cursor.execute("SELECT count(*) from Hospitals where City in (Select City from Patients where Aadhar='{}')".format(session['patientuser']))
        countnh=cursor.fetchone()
        mydb.commit()

        return render_template('patientdashboard.html',result={"aadhar":patientuser,"countar":countar[0],'countnh':countnh[0]})
    return redirect(url_for('patientlogin'))

@app.route('/reservation',methods=["GET","POST"])
def receiptgeneration():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="parth123",
        database="barco"
        )
    if request.method == "POST":
        cursor = mydb.cursor()
        dt=request.form['dtimeslot']
        symptoms=request.form['symptoms']
        dhosp=request.form['dhosp']
        painl=request.form['pain_level']
        ### TO DO :- Queries of this page
        cursor.execute("INSERT INTO `Patients` (`id`, `Aadhar`, `Age`, `Blood_Group`, `email`, `name`, `password`) VALUES (NULL, '{}', '{}', '{}', '{}', '{}', '{}')".format(aadhar,age,bg,email,name,password))     

    if 'patientuser' in session:
        patientuser = session['patientuser']
        
        mydb.commit()

        return render_template('reservationform.html',result={"aadhar":patientuser})
    return redirect(url_for('patientlogin'))

@app.route('/receipt_history',methods=["GET","POST"])
def receipthistory():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="parth123",
        database="barco"
        )
    
    if 'patientuser' in session:
        cursor=mydb.cursor()
        cursor.execute("SELECT created_at,Disease.Name as dname, Medicines.name as mname, Consult_days,Patient_Id FROM (SELECT * from`Reciepts` where Patient_Id in (Select id from Patients where Aadhar='{}')) as Reciepts  INNER JOIN reciept2medicines INNER JOIN reciept2diseases INNER JOIN Disease INNER JOIN Medicines on Reciepts.id=reciept2medicines.receipt AND Reciepts.id=reciept2diseases.receipt AND reciept2diseases.disease=Disease.id and reciept2medicines.medicine=Medicines.id  ORDER BY Reciepts.created_at ".format(session['patientuser']))
        patientuser = session['patientuser']
        res=cursor.fetchall()
        print(res)
        mydb.commit()

        return render_template('receipt_history.html',result={"aadhar":patientuser,"receipthistory":res})
    return redirect(url_for('patientlogin'))

@app.route('/nearby_hospital',methods=["GET","POST"])
def nearby_hospital():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="parth123",
        database="barco"
        )
    
    if 'patientuser' in session:
        cursor=mydb.cursor()
        cursor.execute("SELECT Name,Locality, State, City from Hospitals where City in (Select City from Patients where Aadhar='{}')".format(session['patientuser']))
        patientuser = session['patientuser']
        res=cursor.fetchall()
        print(res)
        mydb.commit()

        return render_template('nearby_hospital.html',result={"aadhar":patientuser,"nearbyhospital":res})
    return redirect(url_for('patientlogin'))


## Doctor
@app.route('/doctorsignup',methods = ['GET', 'POST'])
def dsignup():
    if request.method=="POST":
        aadhar = request.form['aadhar']
        hospid = request.form['Hospital']
        no_patients = request.form['no_patients']
        city = request.form['city']
        name = request.form['name']      
        password = request.form['password']

        mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="parth123",
        database="barco"
        )
    
        cursor = mydb.cursor()
        cursor.execute("INSERT INTO `Doctors` (`id`, `Aadhar`, `Hospital`, `no_patients`, `email`, `name`, `password`) VALUES (NULL, '{}', '{}', '{}', '{}', '{}', '{}')".format(aadhar,age,bg,email,name,password))
        cursor.fetchone()
        mydb.commit()
        return redirect(url_for('patientlogin'))
    return render_template('patientsignup.html')





app.run('0.0.0.0','3000')