from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask import redirect
import json, codecs
from sqlalchemy.exc import IntegrityError
import matplotlib
import matplotlib.pyplot as plt
from datetime import date

app  = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///userCredentials.sqlite3"
db = SQLAlchemy(app)

app.app_context().push()

class AdminCred(db.Model):
    __tablename__ = "AdminCred"
    admin_id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(), unique=True)
    pasword = db.Column(db.String())
    last_login = db.Column(db.String())
    role = db.Column(db.String())

class Customer(db.Model):
    __tablename__ = "Customer"
    customer_id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(), unique=True)
    pasword = db.Column(db.String())
    email = db.Column(db.String(), unique=True)
    phone_number = db.Column(db.Integer, unique=True)
    address = db.Column(db.String(), unique=True)
    pincode = db.Column(db.Integer)
    avg_rating = db.Column(db.Integer)
    number_of_services = db.Column(db.Integer)
    banned_or_not = db.Column(db.String())


class ServiceProfessional(db.Model):
    __tablename__ = "ServiceProfessional"
    professional_id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(), unique=True)
    pasword = db.Column(db.String())
    email = db.Column(db.String(), unique=True)
    phone_number = db.Column(db.Integer, unique=True)
    experience = db.Column(db.Integer)
    service_type = db.Column(db.String())
    description = db.Column(db.String())
    date_created = db.Column(db.String())
    status = db.Column(db.String())
    avg_ratings = db.Column(db.Integer)
    preferred_pincode = db.Column(db.Integer)

class Service(db.Model):
    __tablename__ = "Service"
    service_id = db.Column(db.Integer, primary_key = True)
    service_type = db.Column(db.String())
    price = db.Column(db.Integer)
    time_required = db.Column(db.Integer)
    description = db.Column(db.String(),  unique=True)
    banned_or_not = db.Column(db.String())
    available_pincodes = db.Column(db.String())

class ServiceRequest(db.Model):
    __tablename__ = "ServiceRequest"
    request_id = db.Column(db.Integer, primary_key = True)
    service_id = db.Column(db.Integer, db.ForeignKey('Service.service_id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('Customer.customer_id'))
    professional_id = db.Column(db.Integer, db.ForeignKey('ServiceProfessional.professional_id'))
    date_of_start = db.Column(db.String())
    date_of_completion = db.Column(db.String())
    service_status = db.Column(db.String())
    remarks = db.Column(db.String())

class Ratings(db.Model):
    __tablename__ = "Ratings"
    reques_id = db.Column(db.Integer, db.ForeignKey('ServiceRequest.request_id'),  primary_key = True,)
    rating = db.Column(db.Integer)

class Pincodes(db.Model):
    __tablename__ = "Pincodes"
    reques_id = db.Column(db.Integer,  primary_key = True,)
    pincode = db.Column(db.String(), unique=True)

db.create_all()

@app.route('/adminDashboard/<code>', methods=["GET","POST"])
def adminDashboard(code=None):
    service = Service.query.all()
    professional = ServiceProfessional.query.all()
    for i in professional:
        if i.status == "Approved":
            i.ac = "rd"
        elif i.status == "Rejected" or i.status == "":
            i.ac = "aaad"
    serviceRequests = ServiceRequest.query.all()
    l = []
    for i in serviceRequests:
        tem = i
        n = ServiceProfessional.query.filter_by(professional_id = i.professional_id).first()
        nn = Customer.query.filter_by(customer_id = i.customer_id).first()
        nnn = Service.query.filter_by(service_id = i.service_id).first()
        if n:
            tem.prof_username = n.username
        else:
            tem.prof_username = "-"
        if nn:
            tem.customer_username = nn.username
        else:
            tem.customer_username = "-"
        if nnn:
            tem.service_type = nnn.service_type
        else:
            tem.service_type = "-"
        l.append(tem)
    return render_template("adminDashboard.html",
                           service = service,
                           professional = professional,
                           serviceRequests = l,
                           code = code,
                           )

@app.route('/deleteService/<service_id>/<code>', methods=["GET","POST"])
def deleteService(service_id=None, code = None):
    l = Service.query.filter_by(service_id = service_id)
    n = ServiceRequest.query.filter_by(service_id = service_id).delete()
    # for i in n:
    #     i.delete()
    l.delete()
    db.session.commit()
    return redirect("/adminDashboard/deleted")

@app.route('/editService/<service_id>/<code>', methods=["GET","POST"])
def editService(service_id=None, code = None):
    l = Service.query.filter_by(service_id = service_id).first()
    if request.method == "POST":
        
        
        description = request.form["description"]
        duration = request.form["duration"]
        price = request.form["price"]
        available_pincodes = request.form["pincodes"]
        if  description and duration and price and available_pincodes:
            try:
                a = Service.query.filter_by(service_id = service_id).update({'price' :  int(price),
                'time_required' : int(duration),
                'description' : description,
                'banned_or_not' : "No",
                'available_pincodes' : available_pincodes})
                
                db.session.add(a)
                db.session.commit() 
            except Exception as error:
                print(error)
                return redirect("/adminDashboard/2")
        else:
            return redirect("editService/"+str(service_id)+"/1")
        
    return render_template('editService.html', code =  code,
                           service_type = l.service_type)

@app.route('/validProfessional/<professional_id>/<code>', methods=["GET","POST"])
def validProfessional(professional_id=None, code = None):
    if code == "Delete":
        l = ServiceProfessional.query.filter_by(professional_id = professional_id)
        n = ServiceRequest.query.filter_by(professional_id = professional_id).delete()
        l.delete()
        db.session.commit()
        return redirect("/adminDashboard/deleted")
    
    elif code == "Reject":
        ServiceProfessional.query.filter_by(professional_id = professional_id).update({"status" : "Rejected"})
        db.session.commit()
        return redirect("/adminDashboard/rejected")
    else:
        ServiceProfessional.query.filter_by(professional_id = professional_id).update({"status" : "Approved"})
        db.session.commit()
        return redirect("/adminDashboard/approved")
    db.session.commit()
    return redirect("/adminDashboard/deleted")

@app.route('/professionalDashboard/<u>/<code1>', methods=["GET","POST"])
def professionalDashboard(u= None, code1=None):
    
    dataProfessional = ServiceProfessional.query.filter_by(username = u).first()
    servicesAssigned = []
    servicesRequest = []
    servicesRejected = []
    servicesClosed = []
    servicesRequested = []
    servicesRequestedPref = []
    pref_pincode = dataProfessional.preferred_pincode
    
    prof_id = dataProfessional.professional_id
    prof_name = u
    experience = dataProfessional.experience
    status = dataProfessional.status
    if status == "Approved":
        serviceIdlist = Service.query.filter_by(service_type = dataProfessional.service_type).all()
        #print(serviceIdlist[-1].service_type)
        
        for i in serviceIdlist:
            l = ServiceRequest.query.filter_by(service_id = i.service_id).first()
            
            if(l):
                t = Service.query.filter_by(service_id = l.service_id).first()
                
                e = Customer.query.filter_by(customer_id = l.customer_id).first()
                servicesRequest.append(l)
                if(servicesRequest[-1].professional_id == prof_id):
                    if(servicesRequest[-1].service_status == "Accepted"):
                        servicesRequest[-1].customer_details = e
                        servicesRequest[-1].service_details = t
                        servicesAssigned.append(servicesRequest[-1])
                    elif(servicesRequest[-1].service_status == "Closed"):
                        servicesRequest[-1].customer_details = e
                        servicesRequest[-1].service_details = t
                        servicesClosed.append(servicesRequest[-1])
                    elif(servicesRequest[-1].service_status == "Rejected"):
                        servicesRequest[-1].customer_details = e
                        servicesRequest[-1].service_details = t
                        servicesRejected.append(servicesRequest[-1])
                elif(not servicesRequest[-1].professional_id):
                    flg = 0
                    for j in servicesAssigned:
                        
                        if j.service_details.service_type == i.service_type and j.service_details.description == i.description:
                            flg = 1
                            break
                    if flg == 0:
                        if(Customer.query.filter_by(customer_id = servicesRequest[-1].customer_id).first().pincode == pref_pincode):
                            servicesRequest[-1].customer_details = e
                            servicesRequest[-1].service_details = t
                            servicesRequestedPref.append(servicesRequest[-1])
                        else:
                            servicesRequest[-1].customer_details = e
                            servicesRequest[-1].service_details = t
                            servicesRequested.append(servicesRequest[-1])
                    
        return render_template("professionalDashboard.html",
        servicesRequested=servicesRequested,
        servicesRequestedPref=servicesRequestedPref,
        servicesRejected= servicesRejected,
        servicesClosed=servicesClosed,
        servicesAssigned=servicesAssigned,
        prof_name = prof_name,
        prof_id = prof_id,
        experience=experience,
        #customer_details = e,
        #service_details = t
        )
    elif status == "Rejected":
        return render_template('RejectedAccount.html', code =  1)
    else:
        return render_template('RejectedAccount.html', code =  2)
            
            

@app.route('/customerDashboard/<id>/<code>', methods=["GET","POST"])
def customerDashboard(id = None, code= None):
    service_type = []
    service_history = []
    print("c",id, code)
    customer = Customer.query.filter_by(customer_id = int(id)).first()
    pincode = customer.pincode
    print(customer)
    for i in Service.query.all():
        print(type(i.service_id))
        pincodes = i.available_pincodes
        pincodes = pincodes.split(',')
        if i.service_type not in service_type and str(pincode) in pincodes:
            service_type.append(i.service_type)
    for j in ServiceRequest.query.filter_by(customer_id = id).all():
        prof_id = j.professional_id
        if prof_id and j.service_status == "Accepted":
            print(prof_id, "l")
            oo = j
            oo.professional_details = ServiceProfessional.query.filter_by(professional_id = prof_id).first()
            oo.service_details = Service.query.filter_by(service_id = j.service_id).first()
            oo.status = "Accepted"
            oo.prof_id = prof_id
            service_history.append(oo)
        elif prof_id and j.service_status == "Rejected":
            oo = j
            oo.professional_details = ServiceProfessional.query.filter_by(professional_id = prof_id).first()
            oo.service_details = Service.query.filter_by(service_id = j.service_id).first()
            oo.status = "Rejected"
            oo.prof_id = prof_id
            service_history.append(oo)
        elif prof_id and j.service_status == "Close":
            oo = j
            oo.professional_details = ServiceProfessional.query.filter_by(professional_id = prof_id).first()
            oo.service_details = Service.query.filter_by(service_id = j.service_id).first()
            oo.status = "Close"
            oo.prof_id = prof_id
            service_history.append(oo)
        else:
            oo = j
            oo.professional_details = {'username' : 'Pending', 'phone_number' : 'Pending'}
            oo.service_details = Service.query.filter_by(service_id = j.service_id).first()
            oo.status = "Pending"
            oo.prof_id = prof_id
            service_history.append(oo)
    return render_template("customerDashboard.html",
                           service_type = service_type,
                           service_history = service_history,
                           customer_id = id)
#not complete
@app.route('/professionalSearch/<professionalId>', methods=["GET","POST"])
def professionalSearch(professionalId = None):
    l=[]
    n = []
    if request.method == "POST":
        search = request.form['search']
        value = request.form['search-value']
        if search and value:
            if search == "date_of_start":
                nn = ServiceRequest.query.filter_by(professional_id = professionalId , date_of_start = value).all()
                nnn = ServiceRequest.query.filter_by(professional_id = None , date_of_start = value).all()
            elif search == "Pincode":
                nn = ServiceRequest.query.filter_by(professional_id = professionalId , pincode = value).all()
                nnn = ServiceRequest.query.filter_by(professional_id = None , pincode = value).all()
            elif search == "service_status":
                nn = ServiceRequest.query.filter_by(professional_id = professionalId , service_status = value).all()
                nnn = ServiceRequest.query.filter_by(professional_id = None , service_status = value).all()
            for i in nn:
                l.append(i)
                l.append(i.customer_details[Customer.query.filter_by(customer_id = l.customer_id).first()])
                l.append(i["service_details"][Service.query.filter_by(service_id = l.service_id).first()])
            for i in nnn:
                n.append(i)
                n.append(i["customer_details"][Customer.query.filter_by(customer_id = l.customer_id).first()])
                n.append(i["service_details"][Service.query.filter_by(service_id = l.service_id).first()])
    return render_template("professionalSearch.html",
                           prof_id = professionalId,
                           l = l,
                           n = n)
@app.route('/statAdmin/<code>')
def statAdmin(code = None):
    matplotlib.use('Agg')
    plt.figure(2)
    plt.rcParams["figure.figsize"] = [7.00, 3.50]
    plt.rcParams["figure.autolayout"] = True
    # Plot the histogram
    l = ServiceRequest.query.all()
    n = {}
    for i in l:
        if i.service_status in n:
            n[i.service_status]+= 1
        else:
            n[i.service_status] = 1
    l = n
    print("Keys ",n.keys())
    keys = list(n.keys())

    for i in range(len(keys)):
        if not keys[i]:
            keys[i] = "Pending"
    
    plt.pie(n.values(), labels = keys)

  
    # Save the histogram
    plt.savefig('./static/admin1.png')
    plt.figure(1)
    plt.rcParams["figure.figsize"] = [7.00, 3.50]
    plt.rcParams["figure.autolayout"] = True
    # Plot the histogram
    j = Service.query.all()
    n = {}
    for i in j:
        if i.service_type in n:
            n[i.service_type] = n[i.service_type]+1
        else:
            n[i.service_type] = 1
    j = n
    plt.hist(n)
    plt.savefig('./static/admin2.png')
    return render_template('stat.html', code = code, page = "admin")

@app.route('/statProf/<prof_id>/<code>')
def statProf(prof_id = None,code = None):
    matplotlib.use('Agg')
    plt.figure(2)
    plt.rcParams["figure.figsize"] = [7.00, 3.50]
    plt.rcParams["figure.autolayout"] = True
    # Plot the histogram
    l = ServiceRequest.query.filter_by(professional_id = prof_id).all()

    n = {}
    for i in l:
        if i.service_status in n:
            n[i.service_status]+= 1
        else:
            n[i.service_status] = 1
    l = n
    plt.pie(n.values(), labels = n.keys())

  
    # Save the histogram
    plt.savefig('./static/professional1.png')
    plt.figure(1)
    plt.rcParams["figure.figsize"] = [7.00, 3.50]
    plt.rcParams["figure.autolayout"] = True
    # Plot the histogram
    j = ServiceRequest.query.filter_by(professional_id = prof_id).all()
    n = {}
    for i in j:
        rating = Ratings.query.filter_by(reques_id = i.request_id).first()
        if rating:
            rating = rating.rating
            if rating in n:
                n[i.rating] = n[i.rating]+1
            else:
                n[i.rating] = 1
    j = n
    plt.hist(n)
    plt.savefig('./static/professional2.png')
    return render_template('stat.html', code = code, page ="professional")

@app.route('/statCostomer/<customer_id>/<code>')
def statCostmer(customer_id = None,code = None):
    matplotlib.use('Agg')
    plt.figure(2)
    plt.rcParams["figure.figsize"] = [7.00, 3.50]
    plt.rcParams["figure.autolayout"] = True
    # Plot the histogram
    l = ServiceRequest.query.filter_by(customer_id = customer_id).all()

    n = {}
    for i in l:
        if i.service_status in n:
            if i.service_status == "":
                n["Pending"]+= 1
            else:
                
                n[i.service_status]+= 1
        else:
            if i.service_status == "":
                n["Pending"] = 1
            else:
                n[i.service_status] = 1
    l = n
    plt.pie(n.values(), labels = n.keys())

  
    # Save the histogram
    plt.savefig('./static/customer1.png')
    plt.figure(1)
    plt.rcParams["figure.figsize"] = [7.00, 3.50]
    plt.rcParams["figure.autolayout"] = True
    # Plot the histogram
    j = ServiceRequest.query.filter_by(customer_id = customer_id).all()
    n = {}
    for i in j:
        rating = Service.query.filter_by(service_id = i.service_id).first()
        if rating.service_type in n:
            n[rating.service_type] = n[rating.service_type]+1
        else:
            n[rating.service_type] = 1
    j = n
    plt.hist(n)
    plt.savefig('./static/customer2.png')
    return render_template('stat.html', code = code, page = "customer", customer_id = customer_id)

@app.route('/viewService/<customerId>/<service_type>/<code>', methods=["GET","POST"])
def viewService(customerId, service_type = None, code = 0):
    print(service_type)
    l = Service.query.filter_by(service_type = service_type).all()
    
    services = []
    service_history = []
    print(l)
    for i in l:
        print(i.service_id)
        n = ServiceRequest.query.filter_by(service_id = i.service_id, customer_id = customerId)
        print(n.first(), type(n))
        print("outside if ",n.first())
        if not n == None:
            print("inside if", n.first())
            services.append(i)
        else:
            if n.first().service_status == "Close":
                services.append(i)
            
    print(services)
    #add a functionality to check if the service is already there in 
    for j in ServiceRequest.query.filter_by(customer_id = customerId).all():
        prof_id = j.professional_id
        print(prof_id, j.service_status, service_history)
        if prof_id and j.service_status == "Accepted":
            print(prof_id, "l")
            oo = j
            oo.professional_details = ServiceProfessional.query.filter_by(professional_id = prof_id).first()
            oo.service_details = Service.query.filter_by(service_id = j.service_id).first()
            oo.status = "Accepted"
            oo.prof_id = prof_id
            service_history.append(oo)
        elif prof_id and j.service_status == "Rejected":
            oo = j
            oo.professional_details = ServiceProfessional.query.filter_by(professional_id = prof_id).first()
            oo.service_details = Service.query.filter_by(service_id = j.service_id).first()
            oo.status = "Rejected"
            oo.prof_id = prof_id
            service_history.append(oo)
        elif prof_id and j.service_status == "Close":
            oo = j
            oo.professional_details = ServiceProfessional.query.filter_by(professional_id = prof_id).first()
            oo.service_details = Service.query.filter_by(service_id = j.service_id).first()
            oo.status = "Close"
            oo.prof_id = prof_id
            service_history.append(oo)
        else:
            oo = j
            oo.professional_details = {'username' : 'Pending', 'phone_number' : 'Pending'}
            oo.service_details = Service.query.filter_by(service_id = j.service_id).first()
            oo.status = "Pending"
            oo.prof_id = prof_id
            service_history.append(oo)
    return render_template("viewService.html",
                           prof_name = ServiceProfessional.query.filter_by(professional_id = customerId).first().username,
                           l = services,
                           service_history = service_history,
                           customer_id = customerId, code = code)
@app.route('/professionalRequestResponse/<requestId>/<professionalId>/<command>', methods=["GET","POST"])
def professionalRequestResponse(requestId, professionalId, command):
    
    service = ServiceRequest.query.filter_by(request_id = requestId)
    if command == "accept":
        service.update({'professional_id': professionalId, 'date_of_start' : '11/26/2024', 'service_status' : 'Accepted'})
        u = ServiceProfessional.query.filter_by(professional_id = int(professionalId)).first().username
    else:
        service.update({'professional_id': professionalId, 'date_of_start' : '11/26/2024', 'service_status' : 'Rejected'})
        print(professionalId, type(professionalId))
        u = ServiceProfessional.query.filter_by(professional_id = int(professionalId)).first().username
    db.session.commit()
    return redirect("/professionalDashboard/"+u+"/None") 
#code 1 = fields not filled
#code 2 = already exists
#code 3 = error
@app.route("/createNewService/<code>", methods=["GET","POST"])
def createNewService(code = 0):
    if request.method == "POST":
        service_type = request.form["service_type"]
        description = request.form["description"]
        duration = request.form["duration"]
        price = request.form["price"]
        available_pincodes = request.form["pincodes"]
        if service_type and description and duration and price and available_pincodes:
            try:
                a = Service(service_type = (service_type),
                price =  int(price),
                time_required = int(duration),
                description = description,
                banned_or_not = "No",
                available_pincodes = available_pincodes)
                db.session.add(a)
                db.session.commit()
            except IntegrityError  as error:
                print(error)
                return redirect("/createNewService/2") 
            except Exception as error:
                print(error)
                return redirect("/createNewService/3")
        else:
            return redirect("/createNewService/1")
        
    return render_template('createNewService.html', code =  code)


@app.route("/closeService/<reques_id>/<customer_id>/<page>", methods=["GET","POST"])
def closeService(reques_id = None, customer_id = None, page = None):
    s = ServiceRequest.query.filter_by(request_id = reques_id).first()
    if request.method == "POST":
        rating = request.form["rating"]
        remakrs = request.form["remarks"]
        if rating and remakrs:
            
            l = ServiceProfessional.query.filter_by(professional_id = int(s.professional_id)).first().avg_ratings
            if not l:
                l = 0
            l = (int(l) + int(rating)) // 2
            ServiceProfessional.query.filter_by(professional_id = s.professional_id).update({"avg_ratings" : l})
            ServiceRequest.query.filter_by(request_id = reques_id).update({'service_status': 'Close', 'remarks' : remakrs, 'date_of_completion' : '11-29-2024'})
            a = Ratings(reques_id = reques_id, rating = rating)
            db.session.add(a)
            db.session.commit()
        if page == "viewService":
            return redirect("/viewService/"+str(customer_id)+"/"+Service.query.filter_by(service_id = s.service_id).first().service_type)
        elif page == "customerDashboard":
                return redirect("/customerDashboard/"+str(customer_id)+"/None")
    else:
        return render_template("closeServiceForm.html",
                               customer_id = customer_id,
                               reques_id = reques_id,
                               page = page)

#
@app.route("/bookService/<ser_req_id>/<customer_id>/<page>", methods=["GET","POST"])
def bookService(ser_req_id = None, customer_id = None, page = None):
    
    l = ServiceRequest(service_id = ser_req_id, customer_id = customer_id, professional_id = None, service_status = "")
    ll = Service.query.filter_by(service_id = ser_req_id).first()
    if page == "viewService":
        if ServiceRequest.query.filter_by(service_id = ser_req_id, customer_id = customer_id).first():
            return redirect("/viewService/"+str(customer_id)+"/"+ll.service_type+"/"+str(1))
    db.session.add(l)
    db.session.commit()
    if page == "viewService":
        return redirect("/viewService/"+str(customer_id)+"/"+ll.service_type+"/"+str(0))

#Rg Page 
@app.route("/", methods=["GET","POST"]) #default page
@app.route("/professionalRg/<code>", methods=["GET","POST"])
def professionalRg(code = 0):
    if code == '1':
        code = "Empty field or fileds"
    elif code == '2':
        code = "Already exists"
    elif code == '3':
        code = "Some error occured, try filling appropriate data"
    else:
        code = ""
    l = []
    ll=[]
    n = Service.query.all()
    for i in n:
        pin = i.available_pincodes.split(',')
        vice = i.service_type
        if vice not in ll:
            ll.append(vice)
        for j in pin:
            if j not in l:
                l.append(j)
    return render_template("professionalRg.html",message = code, pincodes = l, service_type = ll)

@app.route('/customerRg/<code>', methods=["GET","POST"])
def customerRg(code = 0):
    if code == '1':
        code = "Empty field or fileds"
    elif code == '2':
        code = "Already exists"
    elif code == '3':
        code = "Some error occured, try filling appropriate data"
    else:
        code = ""
    return render_template("customerRg.html",message = code)

#Ln Page
@app.route('/professionalLn/<code>', methods=["GET", "POST"])
def professionalLn(code = 0):
    return render_template("professionalLn.html", code= code)

@app.route('/customerLn/<code>', methods=["GET", "POST"])
def customerLn(code = 0):
    return render_template("customerLn.html", code= code)

@app.route('/adminLn/<code>')
def adminLn(code = 0):
    return render_template('adminLn.html', code = code)


@app.post('/checkandlnadmin/<code>')
def checkandlnadmin(code):
    username = request.form['inputUsername']
    pasword = request.form['inputPassword']
    if pasword and username:
        data = AdminCred.query.all()
        if data[0].username == username:
            if data[0].pasword == pasword:
                return redirect("/adminDashboard/0")
            else:
                return render_template('adminLn.html', message = "Password is wrong")
        else:
            return render_template('adminLn.html', message = "Username is not found")
    else:
        return render_template('adminLn.html', message = "Fill all fields")

    
#Check if the user reg detials valid or not and then store them in database
@app.post('/checkandrgprofessional/<code>')
def CheckandRgProfessional(code):
    username = request.form['inputUsername']
    pasword = request.form['inputPassword']
    service_type = request.form['form-professional-service']
    pref_pincode = request.form["form-professional-pincode"]
    email = request.form["inputEmail"]
    phone_number = request.form["inputPhone"]
    description = request.form["inputDescription"]
    if pasword and username and service_type and pref_pincode:
        try:
            prof = ServiceProfessional(username = username,
                                       pasword = pasword,
                                       email = email,
                                       phone_number = phone_number,
                                       experience = 0,
                                       service_type = service_type,
                                       description = description,
                                       date_created = str(date.today()),
                                       status = "",
                                       preferred_pincode = pref_pincode,
                                       )
            print('Professional stored in var')
            db.session.add(prof)
            print('Professional added in session')
            db.session.commit()
            print("Professional commit")
            with open('Professional.txt', 'wb') as f:
                json.dump({'username': username}, codecs.getwriter('utf-8')(f), ensure_ascii=False)
            return redirect("/professionalDashboard/"+username+"/None")
        except IntegrityError as error:
            print(error)
            return redirect("/professionalRg/2")
        except Exception as err:
            print(err)
            return redirect("/professionalRg/3")
    return redirect("/professionalRg/1")

@app.post('/checkandrgcustomer/<code>')
def CheckandRgCustomer(code):
    username = request.form['inputUsername']
    pasword = request.form['inputPassword']
    email = request.form["inputEmail"]
    phone_number = request.form["inputPhone"]
    address = request.form["inputAddress"]
    pincode = request.form["inputPincode"]
    if pasword and username and pincode:
        try:
            custom = Customer(username=username,
                                       pasword=pasword,
                                       email = email,
                                       phone_number = phone_number,
                                       address = address,
                                       pincode = pincode,
                                       avg_rating = 0,
                                       number_of_services = 0,
                                       banned_or_not = "No"
                                       )
            print('Customer stored in var')
            db.session.add(custom)
            print('Customer added in session')
            db.session.commit()
            customer_id = Customer.query.filter_by(username = username).first().customer_id
            print("Customer commit")
            #to be checked
            with open('Customer.txt', 'wb') as f:
                json.dump({'username': username}, codecs.getwriter('utf-8')(f), ensure_ascii=False)
            return redirect("/customerDashboard/"+str(customer_id)+"/None")
        except IntegrityError as error:
            print(error)
            return redirect("/customerRg/2")
        except Exception as err:
            print(err)
            return redirect("/customerRg/3")
        
    return redirect("/customerRg/1")

@app.post('/checkandlncustomer/<code>')
def checkandlncustomer(code):
    username = request.form['inputUsername']
    pasword = request.form['inputPassword']
    if pasword and username:
        udata = Customer.query.filter_by(username = username).first()
        if udata:
            u = udata.username
            pd = udata.pasword
            if pd == pasword:
                with open('Customer.txt', 'wb') as f:
                    json.dump({'username': username}, codecs.getwriter('utf-8')(f), ensure_ascii=False)
                customer_id = Customer.query.filter_by(username = u).first().customer_id
                print("l ",customer_id)
                return redirect("/customerDashboard/"+str(customer_id)+"/None")
            else:
                return redirect("/customerLn/3")
        else:
            return redirect("/customerLn/2")
    else:
        return redirect("/customerLn/1")
@app.post('/checkandlnprofessional/<code>')
def checkandlnprofessional(code):
    username = request.form['inputUsername']
    pasword = request.form['inputPassword']
    if pasword and username:
        udata = ServiceProfessional.query.filter_by(username = username).first()
        if udata:
            u = udata.username
            pd = udata.pasword
            if pd == pasword:
                with open('ServiceProfessional.txt', 'wb') as f:
                    json.dump({'username': username}, codecs.getwriter('utf-8')(f), ensure_ascii=False)
                return redirect("/professionalDashboard/"+u+"/None")
            else:
                return redirect("/professionalLn/3")
        else:
            return redirect("/professionalLn/2")
    else:
        return redirect("/professionalLn/1")
app.run(debug=True)