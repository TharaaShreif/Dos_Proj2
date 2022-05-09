from flask_marshmallow import Marshmallow
from flask import request
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, json, jsonify ,render_template
import requests
from datetime import date
from datetime import datetime
import sqlite3

app = Flask(__name__)


#purchase (order_server send to catalog_server)
catlog1="192.168.1.106:3000"
catlog2="192.168.1.106:4000"


load_balance=0
@app.route('/purchase/<int:book_ID>', methods=['PUT'])
def purchase_book(book_ID):
    global load_balance
    if load_balance==0:
        load_balance+=1
        r=requests.put("http://"+catalog1+"/decrease_quantity/"+str(book_ID),{'new_amount':1})
    if load_balance==1:
        load_balance+=1
        r=requests.put("http://"+catalog2+"/decrease_quantity/"+str(book_ID),{'new_amount':1})
    
    y=r.json()
    message= str(y.get('message'))


    if message.find("enough")!=-1 or message == 'None'   :

        return(r.content)
    else: 
        global load_balance
        r2=''
        if load_balance==0:
            load_balance+=1
            r2=requests.put("http://"+catalog1+"/info/"+str(book_ID))
        if load_balance==1:
            load_balance+=1
            r2=requests.put("http://"+catalog2+"/info/"+str(book_ID))
        if load_balance==2:
            load_balance=10
            r2=requests.put("http://"+catalog3+"/info/"+str(book_ID))
        info=r2.json()
        return {"message":f"bought book '{info.get('title')}'"}
      



if __name__=="__main__":
    app.run(debug=True)
