from flask import Flask, session, request, render_template, flash, redirect, url_for
from codes.config import DefaultConfig
import boto3
from botocore.exceptions import ClientError
from werkzeug.security import check_password_hash

CONFIG = DefaultConfig
app = Flask(__name__)
app.config['SECRET_KEY'] = CONFIG.FLASK_SECRET_KEY

dynamodb = boto3.resource('dynamodb', endpoint_url=CONFIG.ENDPOINT_URL)
managers = dynamodb.Table('Managers')


@app.route("/home", methods=['GET', 'POST'])
def home():
    if ('user_in_session' not in session):
        flash('You need to log in!', category='errorLogin')
        return redirect(url_for('login'))
    else:
        trucks = dynamodb.Table('Trucks').scan()["Items"]
        errors = dynamodb.Table('Errors').scan()["Items"]
        errDate = []
        
        arrx = []
        arry = []
        current=0
        for error in errors:
            errDate.append(error['dateTime'])
        
        for date in errDate:
            current += 1
            if date in arrx:#Check if element is already in arrx
                index = arrx.index(date)
                arry[index] = arry[index]+1#Increment number of occurrency
            else:
                arrx.append(date)
                arry.append(1)
        print(arrx)
        print(arry) 
        return render_template("index.html", trucks=trucks, arrX = arrx, arrY = arry)


@app.route('/', methods=['GET', 'POST'])
def login():
    if ('user_in_session' in session):
        flash('Are already logged in', category='successLogin')
        return redirect(url_for('home'))
    if (request.method == 'POST'):
        email = request.form['email']
        password = request.form['password']
        try:
            manager = managers.get_item(Key={'email': email})
            if len(manager)>1:
                manager = manager['Item']
                if check_password_hash(manager['password'], password):
                    flash('Welcome back ' +
                          manager['managerName'], category='successLogin')
                    session['user_in_session'] = manager
                    return redirect(url_for('home', user=manager))
                else:
                    flash('Incorrect password', category='errorLogin')
            else:
                flash('Email not found', category='errorLogin')
        except ClientError as e:
            print(e.response['Error']['Message'])
    
    return render_template("login.html")


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/shipmentStatus')
def shipmentStatus():
    trucksList = dynamodb.Table('Trucks').scan()["Items"]
    return render_template("shipmentStatus.html", trucksList=trucksList)


@app.route('/shipmentConfirm', methods=['GET', 'POST'])
def shipmentConfirm():
    if (request.method == 'POST'):
        trucksList = dynamodb.Table('Trucks')

        dateTimeDeparture = request.form["dateTimeDeparture"]
        dateTimeArrival = request.form["dateTimeArrival"]
        truckSelected = request.form["truckSelected"]
        print(dateTimeArrival)
        if truckSelected:
            if dateTimeArrival and dateTimeDeparture:
                trucksList.update_item(Key={'truckID': truckSelected}, 
                               UpdateExpression="set dateTimeDeparture = :val1, dateTimeArrival = :val2", 
                               ExpressionAttributeValues={':val1': dateTimeDeparture,':val2': dateTimeArrival})
            elif dateTimeArrival:
                trucksList.update_item(Key={'truckID': truckSelected}, 
                               UpdateExpression="set dateTimeArrival = :val2", 
                               ExpressionAttributeValues={':val2': dateTimeArrival})
            elif dateTimeDeparture:
                trucksList.update_item(Key={'truckID': truckSelected}, 
                               UpdateExpression="set dateTimeDeparture = :val1", 
                               ExpressionAttributeValues={':val1': dateTimeDeparture})
            else:
                flash('You must select a Departure/Arrival', category='errorUpdate')
        flash('Departure/Arrival updated with success', category='successUpdate')
        return redirect(url_for('shipmentStatus'))


if __name__ == "__main__":
    app.run(debug=True)
