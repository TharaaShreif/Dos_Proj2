from datetime import time
import re
from flask import request
from flask.sessions import NullSession
from flask import Flask, json, jsonify ,render_template
from flask import request
import requests
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///CacheBooksInfo_DB.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

MAX_SIZE=10
counter=0



class Cache_Server_DB(db.Model):#we create class for Database
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(500))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Float)
    topic = db.Column(db.String(500))
    time = db.Column(db.Integer)
    req =db.Column(db.Integer)
     
    def __init__(self,id,title,quantity,price,topic,time,req):
        self.id=id
        self.title=title
        self.quantity=quantity
        self.price=price
        self.topic=topic
        self.time=time
        self.req=req



#Add new book
@app.route('/add_Book/', methods=['POST'])
def add_book():

    book = Cache_Server_DB.query.get(request.form.get('id'))
    if book:
        book.req = book.req + 1
        books= Cache_Server_DB.query.all()
        for bs in books:
            bs.time = bs.time + 1
        db.session.commit()
        return jsonify({request.form.get('title'):" in cache " })
    else:
        global counter
        if counter>1000:
            req_Priority={}
            time_Priority={}
            books = Cache_Server_DB.query.with_entities(Cache_Server_DB.id,Cache_Server_DB.req,Cache_Server_DB.time).all()
            for bs in books:
                req_Priority[bs[0]]=bs[1]
                time_Priority[bs[0]]=bs[2]
                
            
            mid = min(req_Priority, key=req_Priority.get)
            for key in time_Priority:
                if req_Priority[key] == req_Priority[mid]:
                    if time_Priority[key] > time_Priority[mid] :
                        mid=key

            
            db.query.filter_by(id=mid).delete()
            db.session.commit()
            counter -= 1 

        newBook=Cache_Server_DB(request.form.get('id'),request.form.get('title'),request.form.get('quantity'),request.form.get('price'),request.form.get('topic'),1,1)
        db.session.add(newBook)
        db.session.commit()
        counter += 1
        return jsonify({request.form.get('title'):" Added_successfully" })


@app.route("/info/<book_ID>", methods=['GET'])#get from cashe
def get_info_forID(book_ID):
    book = Cache_Server_DB.query.with_entities(Cache_Server_DB.title,Cache_Server_DB.quantity,Cache_Server_DB.price,Cache_Server_DB.topic,Cache_Server_DB.req,Cache_Server_DB.time).filter_by(id = book_ID).first()
    if book :
        book2={'title':book[0],'quantity':book[1],'price':book[2],'topic':book[3]}
        re = json.dumps(book2,indent=4)
        books= Cache_Server_DB.query.all()
        for bs in books:
            if bs.id== book_ID:
                bs.id += 1 
            bs.time = bs.time + 1
        db.session.commit()
        return (re)
    else: 

        return jsonify({'msg':" please try another id this not exist" })


@app.route("/invalidate/<int:book_ID>", methods=['DELETE'])
def invalidate_Book(book_ID):
    global order_counter
    book = Cache_Server_DB.query.get(book_ID)
    if book:
        db.session.delete(book)
        db.session.commit()
        return jsonify({book_ID :"Delete_successfully"})
    else:
        return jsonify({'msg':"please try another id this not exist"})
  
#search by topic

@app.route("/search/<topic>", methods=['GET'])
def search_by_topic(topic):
    book = Cache_Server_DB.query.with_entities(Cache_Server_DB.id,Cache_Server_DB.title).filter_by(topic=topic.replace("%20"," ")).all()
    books={}
    for bs in book:
        
        books[bs[0]]={'id':bs[0],'title':bs[1]}
    
    res=json.dumps(books)
   
    return (res)


if __name__=="__main__":
    app.run(debug=True)

