#!/usr/bin/python
# -*- coding: latin-1 -*-
from flask import Flask, render_template
from flask import request
import hashlib
import hmac
import base64

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('pay.html')

# secretKey = "<ENTER_YOUR_SECRETKEY_HERE>"
secretKey = "8b8472e354fd3f815f48c0673e70df83"
@app.route('/request', methods=["POST"])
def handlerequest():
  mode = "TEST" # <-------Change to TEST for test server, PROD for production
  postData = {
      "account_id" : request.form['account_id'], 
      "return_url" : request.form['return_url'], 
      "reference_no" : request.form['reference_no'], 
      "amount" : request.form['amount'], 
      "description" : request.form['description'], 
      "name" : request.form['name'], 
      "address" : request.form['address'], 
      "city" : request.form['city'], 
      "state" : request.form['state'], 
      "postal_code" : request.form['postal_code'], 
      "phone" : request.form['phone'], 
      "email" : request.form['email'], 
      "udf1" : request.form['udf1'], 
      "udf2" : request.form['udf2'], 
      "udf3" : request.form['udf3'], 
      "udf4" : request.form['udf4'],
      "udf5" : request.form['udf5']
  }

  signatureData = secretKey+"|"+request.form['account_id']+"|"+request.form['amount']+"|"+request.form['reference_no']+"|"+request.form['return_url']
  result = hashlib.md5(signatureData.encode()) 
  signature = result.hexdigest()

  if mode == 'PROD': 
    url = "https://www.swipez.in/xway/secure"
  else: 
    url = "https://h7sak8am43.swipez.in/xway/secure"
  return render_template('request.html', postData = postData,signature= signature,url = url)

@app.route('/response', methods=["GET","POST"])
def handleresponse():

  print("FORM", request.form)

  postData = {
    "orderId" : request.form['reference_no'], 
    "orderAmount" : request.form['amount'], 
    "txStatus" : request.form['status'], 
    "refno" : request.form['bank_ref_no'], 
    "mode" : request.form['mode'], 
    "email" : request.form['billing_email'], 
    "signature" : request.form['checksum']
   }
  

  signatureData = ""
  signatureData = secretKey+"|"+request.form['amount']+"|"+request.form['reference_no']+"|"+request.form['billing_email']
  result = hashlib.md5(signatureData.encode()) 
  signature = result.hexdigest()

  return render_template('response.html', postData = postData,computedsignature = signature)

if __name__ == '__main__':
  app.run("",5000,debug='true')
