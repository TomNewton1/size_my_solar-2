import os

from flask import Flask, redirect, url_for, render_template, flash, request, json, jsonify, Response, abort, session
from flask_googlemaps import GoogleMaps, Map
from flask_sqlalchemy import SQLAlchemy
from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin, AdminIndexView, BaseView, expose
from flask_login import UserMixin, LoginManager, current_user, login_user, logout_user
from flask_mail import Mail, Message
from flask_uploads import configure_uploads, IMAGES, UploadSet, ALL
from flask_talisman import Talisman
from datetime import datetime
import time
from werkzeug.utils import secure_filename
import urllib.request
import urllib
import requests
import stripe
import boto3


app = Flask(__name__)

# AWS S3 Connecttion and boto3 config

#app.config['AWS_ACCESS_KEY_ID'] = ""
#app.config['AWS_SECRET_ACCESS_KEY'] = ""
#app.config['AWS_STORAGE_BUCKET_NAME'] = ""

client = boto3.client(
    's3',
    aws_access_key_id='',
    aws_secret_access_key=''
)


# Forcesj HTTPS by default 
Talisman(app, content_security_policy=None)

#App Secret key for passing data between sessions
app.secret_key = 'secretkey'

#Google Maps API KEY
app.config['GOOGLEMAPS_KEY'] = ""

#Directory for temporary pdfs. 

app.config['UPLOADED_IMAGE_DEST'] = ''

images = UploadSet('image', ALL)
configure_uploads(app, images)

# Flask Mail
app.config['DEBUG'] = False
app.config['TESTING'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
#app.config['MAIL_DEBUG'] = False
app.config['MAIL_USERNAME'] = 'sizemysolar@gmail.com'
app.config['MAIL_PASSWORD'] = ''
app.config['MAIL_DEFAULT_SENDER'] = 'sizemysolar@gmail.com'
app.config['MAIL_MAX_EMAILS'] = None
#app.config['MAIL_SUPPRESS_SEND'] = False
app.config['MAIL_ASCII_ATTACHMENTS'] = False 

mail = Mail(app)

# Testing emal sending


@app.route("/email")
def email():
    msg = Message("Hello", sender="sizemysolar@gmail.com", recipients=["povij73768@heroulo.com"])
    
    with app.open_resource("static/images/2dlayout.png") as fp:
        msg.attach("2dlayout.png", "2dlayout/png", fp.read())

    mail.send(msg)
    
    return "Message was sent"

# SQLA database link 

#SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
#SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sizemysolar.db'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
db = SQLAlchemy(app)

# Login view 
login = LoginManager(app)

# Stripe Payment Keys
app.config['STRIPE_PUBLIC_KEY'] = ''
app.config['STRIPE_SECRET_KEY'] = ''

# Stripe Payment Keys (development)
#app.config['STRIPE_PUBLIC_KEY'] = ''
#app.config['STRIPE_SECRET_KEY'] = ''

# This is your real test secret API key.
stripe.api_key = app.config['STRIPE_SECRET_KEY']

# My customer table showing the details of the form they submited, their associated purchase. 
class Customer(db.Model):
    # Data from form
    id = db.Column('id', db.Integer, primary_key=True)
    firstname = db.Column('firstname', db.String(20), nullable= False)
    secondname = db.Column('secondname', db.String(20), nullable= False)
    email = db.Column('email', db.String(120), nullable= False)
    address = db.Column('address', db.String(120), nullable= False)
    latitude = db.Column('latitude', db.Float(20), nullable= False)
    longitude = db.Column('longitude', db.Float(20), nullable= False)
    date_created = db.Column('date_created', db.DateTime, nullable=False, default=datetime.utcnow)
    drawing = db.Column('drawing', db.String(120), nullable=False)

    # Data from stripe
    stripe_email = db.Column('stripe_email', db.String(120), nullable= True)
    payment_confirmation = db.Column('payment_confirmation', db.String(120), nullable= True)
   
    # Project Status
    status = db.Column('status', db.String(120), nullable=False, default="Idle")

    # Allocated designer
    designer = db.Column('designer', db.String(120), nullable=False, default="NA")



# My orders table showing the 

# Admin User login

@login.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class User(db.Model, UserMixin):
    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column('name', db.String(20))
    password = db.Column('password', db.String(20))

# Returns the User model view in the admin page only to the person who is loggedn in. 
class MyModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

class MyAdminIndexView(AdminIndexView):
    @expose('/', methods = ['GET', 'POST'])
    def index(self):

        if request.method == 'POST':

            client_id = request.form.get("client_id")
            print("the client id is:", client_id)

            if request.form.get('action') == "submit":

                # Check if a file was attached. 

                if request.files:
                    
                    files = request.files["file"]

                    if files.filename != '':

                        print ("There is a file on system called: ", files)
                        
                        # Get the file name

                        file_name = files.filename

                        print ("The file name is: ", file_name)

                        # Upload the file to AWS3

                        s3 = boto3.resource('s3')
 
                        s3.Bucket('sizemysolar-files').put_object(Key=file_name, Body=request.files['file'])

                        time.sleep(5)


                        # Save Temporary file 

                        #filename = images.save(files)

        
                        # Send email with attachement. 

                        client = db.session.query(Customer).get(client_id)
                        client_email = client.email
                        client_drawing = client.drawing
                        client_name = client.firstname

                        print("Customer email is: ", client_email)

                        msg = Message("Your "+ client_drawing + " from SizeMySolar UK Ltd.", body="Dear "+ client.firstname +", \nThank you for purchasing a design from SizeMySolar UK Ltd. Please see attached the design that you purchased. If you have any questions please contact us at sizemysolar@gmail.com", recipients=[client_email])
    
                        
                        # Get the file from s3 again (this means that other designers upload regardless of where they are)

                        s3 = boto3.client('s3')
                        
                        with open(file_name, 'wb') as f:
                            s3.download_fileobj('sizemysolar-files', file_name, f)

                        #with open(file_name, 'wb') as z:
                            #msg.attach(file_name, "/png", fp.read())
                        
                        with app.open_resource(file_name) as fp:
                            msg.attach(file_name, "/png", fp.read())

                        mail.send(msg)

                        # Delete file from system 

                        try:
                            os.unlink(os.path.join(os.getcwd(),file_name))
                        except OSError as e: 
                            print(e)


                        # Update the project status
                        
                        selected_job = db.session.query(Customer).get(client_id)

                        selected_job.status = "Completed"
                        db.session.commit()

                        # Flash a message saying file was sent to client. 

                        flash("File was sent to client.", "success")

                        selected_jobs = db.session.query(Customer).filter(Customer.designer.like(current_user.name), Customer.status.like("Assigned"))

                        return self.render('admin/index.html', selected_jobs=selected_jobs)
                
                    else:

                        # Flash a message saying file was not attached. 

                        flash("No file was attached.", "error")

                        selected_jobs = db.session.query(Customer).filter(Customer.designer.like(current_user.name), Customer.status.like("Assigned"))

                        return self.render('admin/index.html', selected_jobs=selected_jobs)


            elif request.form.get('action') == "delete":

                selected_job = db.session.query(Customer).get(client_id)

                selected_job.status = "Idle"
                selected_job.designer = "NA"
                db.session.commit()

                flash("Project was deleted and sent to available jobs.", "error")

                selected_jobs = db.session.query(Customer).filter(Customer.designer.like(current_user.name), Customer.status.like("Assigned"))

                return self.render('admin/index.html', selected_jobs=selected_jobs)          

        else: 

            selected_jobs = db.session.query(Customer).filter(Customer.designer.like(current_user.name), Customer.status.like("Assigned"))

            return self.render('admin/index.html', selected_jobs=selected_jobs)

    def is_accessible(self):
        return current_user.is_authenticated

class AvailableJobsView(BaseView):
    @expose('/', methods=['GET', 'POST'])
    def index(self):

        if request.method == 'POST':

            client_id = request.form['submit']

            # Update status from in progress to active

            # Fetch the object from the table based on the required primary key (Example: Returns <Cutomer(34)>)
            selected_job = db.session.query(Customer).get(client_id)

            # Update status and the designer assigned to the project. 
            selected_job.status = "Assigned"
            selected_job.designer = current_user.name

            print("The Designer Assigned to this job is: ", current_user.name)
            db.session.commit()

            # Variables for available Jobs (filter by if the payment was successful and if status=idle )
            available_jobs = db.session.query(Customer).filter_by(status="Idle", payment_confirmation="Success")

            flash("You selected a new project.", "success")

            return self.render('admin/jobs.html', available_jobs=available_jobs)

        else: 
     
            # Variables for available Jobs (filter by if the payment was successful and if status=idle )
            available_jobs = db.session.query(Customer).filter_by(status="Idle", payment_confirmation="Success")

            return self.render('admin/jobs.html', available_jobs=available_jobs)


# Create the admin view
admin = Admin(app, index_view=MyAdminIndexView())


admin.add_view(MyModelView(User, db.session))
admin.add_view(AvailableJobsView(name='Available Jobs', endpoint='jobs'))

@app.route('/login', methods=['GET','POST'])
def login():

    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]

        # Check if username is in the table
        if db.session.query(db.exists().where(User.name == username)).scalar() and db.session.query(db.exists().where(User.password == password)).scalar():

                #If true, get the usernames id and logg them in. 
                user = User.query.filter_by(name=username).first()

                login_user(user)
                print("You are logged in as: ", user.name)
                return redirect('/admin')

        else: 

            flash("Invalid Username or Password", "error")

            print("Invalid Email or Password")

            return redirect('/login')

    
    else:
        return render_template("login.html")


@app.route('/logout')
def logout():
    logout_user()
    return 'Logged Out'

# A list of Dictionaries containing my products and their prices (live).
product_prices = [
    {'2D':''},
    {'3D':''},
    {'Bespoke Drawing':''}
]

# A list of Dictionaries containing my products and their prices (test keys).
#product_prices = [
    #{'2D':''},
    #{'3D':''},
    #{'Bespoke Drawing':''}
#]


# Not sure, think this enables the google maps connection 
GoogleMaps(app)

# Can probably remove this eventually. 
@app.route('/index')
def index():
    '''
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': '',
            'quantity': 1,
        }],
        mode='payment',
        success_url=url_for('thanks', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('index', _external=True),
    )
    '''
    
    return render_template(
        'index.html', 
        #checkout_session_id=session['id'], 
        #checkout_public_key=app.config['STRIPE_PUBLIC_KEY']
    )




@app.route('/', methods=["GET", "POST"])
def homepage():
    return render_template('homepage.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/privacy')
def privacy():
    return render_template('privacypolicy.html')

@app.route('/terms')
def terms():
    return render_template('termsandconditions.html')

@app.route('/checkmyroof', methods=["GET","POST"])

def checkmyroof():

    if request.method == "POST":

        #print(request.form)
      
        try:

            firstname = request.form["firstname"]
            secondname = request.form["secondname"]
            email = request.form["email"]
            address = request.form["address"]
            latitude = float(request.form["currentLatitude"])
            longitude = float(request.form["currentLongitude"])

            #Pass the product name to get the product price for stripe. Also puts product name in customer order. 
            drawing = request.form["drawing"]

            product_PRICE = [dict[drawing] for dict in product_prices if drawing in dict]
            product_PRICE = " ".join(str(x) for x in product_PRICE)

            #Pass vairbale to the strip_pay function
            session['product_PRICE'] = product_PRICE

            # Commit form values to the Customer table
            customer = Customer(firstname=firstname,secondname=secondname,email=email,address=address,latitude=latitude,longitude=longitude,drawing=drawing)

            db.session.add(customer)
            db.session.commit()

            # Call stripe_pay
            json_data = stripe_pay(product_PRICE)
            
            return jsonify(json_data)

        except ValueError as e:

            print(e)
            #message = "Please move the marker ontop of the property"
            flash("Please move the marker ontop of the property")
            #flash("Please move the marker ontop of the property")
            print("Flashing message")

            return render_template('checkmyroof.html')


    else: 
        # If the user requests the checkmyroof page then take them to the checkmyroof page. 
        return render_template('checkmyroof.html')

# Stipe Payment Page

def stripe_pay(product_PRICE):

    #Get the neccessary variables from 
    product_PRICE = session.get('product_PRICE', None)
    

    stripe_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': product_PRICE,
            'quantity': 1,
        }],
        mode='payment',
        success_url=url_for('thanks', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('index', _external=True),
    )

    return {
        'checkout_session_id': stripe_session['id'], 
        'checkout_public_key': app.config['STRIPE_PUBLIC_KEY']
    }

# Stripe Payment Thankyou page 
@app.route('/thanks')
def thanks():
    return render_template('thanks.html')

# Webhoooks are used to get information about the payment 
@app.route('/stripe_webhook', methods=['POST'])
def stripe_webhook():
    print('WEBHOOK CALLED')

    if request.content_length > 1024 * 1024:
        print('REQUEST TOO BIG')
        abort(400)
    payload = request.get_data()
    sig_header = request.environ.get('HTTP_STRIPE_SIGNATURE')
    #endpoint_secret = '' (live)
    endpoint_secret = ''
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        print('INVALID PAYLOAD')
        return {}, 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        print('INVALID SIGNATURE')
        return {}, 400

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        #session = event['data']['object']
        #print("This is the session :", session)

        #line_items = stripe.checkout.Session.list_line_items(session['id'], limit=1)
        #print("This is all the line items: ", line_items)
        
        # Gets the item within the data, where the value is description. 
        #print("Individual line item: ", line_items['data'][0]['description'])
        
        # Get stripe payment email
        stripe_email = event['data']['object']['customer_details']['email']

        # Check if payment was success
        payment_confirmation = "Success"

        # Fetch the object from the table based on the last primary key (Example: Returns <Cutomer(34)>)
        last_customer = db.session.query(Customer).order_by(Customer.id.desc()).first()

        # Update stripe email
        last_customer.stripe_email = stripe_email
        
        # Update if it was a successful payment. 
        last_customer.payment_confirmation = payment_confirmation

        db.session.commit()

        return ""

    
    else:

        # Payment was unsuccessful and commit to database
        payment_confirmation = "Incomplete"

        # Fetch the object from the table based on the last primary key (Example: Returns <Cutomer(34)>)
        last_customer = db.session.query(Customer).order_by(Customer.id.desc()).first()

        last_customer.payment_confirmation = payment_confirmation

        db.session.commit()

        return ""



# Can remove this page 
@app.route('/payments', methods=["GET", "POST"])
def payments():
    return render_template('payments.html')


# Boto 3 uploading files to AWS S3

BUCKET_NAME=''



@app.route('/upload', methods=["POST"])
def upload(): 

    s3 = boto3.resource('s3')
 
    s3.Bucket('sizemysolar-files').put_object(Key='test.pdf', Body=request.files['file'])

    return "<h1>File Saved to S3</h1>"



if __name__ == "__main__":
    app.run(debug=False)


