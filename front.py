from flask import Flask, json, jsonify ,render_template
from flask import request
import requests
from flask_sqlalchemy import SQLAlchemy
import html_to_json
from requests.api import get

#initial app
app = Flask(__name__)
load_balanc_order=0
load_balanc_catalog=0
catalog1="172.19.5.60:2000"
catalog2="172.19.5.60:3000"
cache="172.19.5.183:2000"
order1="172.19.5.50:3000"
order2="172.19.5.50:4000"

#(search operation )request to catalogServer

@app.route('/search/<topic>', methods=['GET']) 
def search(topic): 
      #this is the request to be sent to the catalog server //tharaa pc
    global load_balanc_catalog
    #this send request to cache server
    send_rs = requests.get("http://"+cache+"/search/"+str(topic)) 
    
    cashe_result = send_rs.json()
    result=''
    if (len(cashe_result)<4 and topic=='Undergraduat school') or( len(cashe_result)<3 and topic=='Distributed systems'):
        if load_balanc_catalog == 0:
            load_balanc_catalog += 1
            result = requests.get("http://"+catalog1+"/search/"+str(topic)) 
            
        elif load_balanc_catalog == 1:
            load_balanc_catalog = 0
            result = requests.get("http://"+catalog2+"/search/"+str(topic)) 
            
            
        catalog_result=result.json()
   
        for catItem in catalog_result:
            book=get_info(catItem.get('id'))
        return (result.content)
    else:
        return(cashe_result)

        

#(info operation )send request to the cataloge server 
@app.route('/info/<int:book_ID>', methods=['GET'])
def get_info(book_ID):
  global load_balanc_catalog
  # here will send request to cache server
  send_rs = requests.get("http://"+cache+"/info/"+str(book_ID))

  res =send_rs.json()
  message= str(res.get('message'))
  if message == 'None': #so there exit book in cache
 
      return(send_rs.content)
  else: 
       # has not book exisit
      if load_balanc_catalog == 0:
          load_balanc_catalog += 1
          result = requests.get("http://"+catalog1+"/info/"+str(book_ID)) 
          
      elif load_balanc_catalog == 1:
          load_balanc_catalog =0
          result = requests.get("http://"+catalog2+"/info/"+str(book_ID)) 
          
      r1=result.json()
      r2=requests.post("http://"+cache+"/addBook/",data={'id':book_ID,'title':r1.get('title'),'price':r1.get('price'),'quantity':r1.get('quantity'),'topic':r1.get('topic')})


#update the price of a book 
@app.route('/update_price/<int:book_ID>', methods=['PUT'])
def update_book_price(book_ID):
    global load_balanc_catalog
    price = request.json['price']
    result=''
    if load_balanc_catalog == 0:
            load_balanc_catalog += 1
            result = requests.put("http://"+catalog1+"/update_price/"+str(book_ID),data={'price':price}) 
    elif load_balanc_catalog == 1:
        load_balanc_catalog = 0
        result = requests.put("http://"+catalog2+"/update_price/"+str(book_ID),data={'price':price}) 
    
    return (result.content)

#update quantity
#1increease

 
@app.route('/increase_quantity/<int:book_ID>', methods=['PUT'])
def increase_book_quantity(book_ID):
    new_amount = request.json['new_amount']
    global load_balanc_catalog
    result=''
    if load_balanc_catalog == 0:
            load_balanc_catalog += 1
            result = requests.put("http://"+catalog1+"/increase_quantity/"+str(book_ID),data={'new_amount':new_amount})
    elif load_balanc_catalog == 1:
        load_balanc_catalog = 0
        result = requests.put("http://"+catalog2+"/increase_quantity/"+str(book_ID),data={'new_amount':new_amount})
    return(result.content)

#2decrease
 
@app.route('/decrease_quantity/<int:book_ID>', methods=['PUT'])
def decrease_book_quantity(book_ID):
    new_amount = request.json['new_amount']
    global load_balanc_catalog
    result=''
    if load_balanc_catalog == 0:
            load_balanc_catalog += 1
            result = requests.put("http://"+catalog1+"/decrease_quantity/"+str(book_ID),data={'new_amount':new_amount})
    elif load_balanc_catalog == 1:
        load_balanc_catalog = 0
        result = requests.put("http://"+catalog2+"/decrease_quantity/"+str(book_ID),data={'new_amount':new_amount})

    return(result.content)



#purchase (Order server requests)
@app.route('/purchase/<int:book_ID>', methods=['PUT'])
def purchase(book_ID):
    global load_balanc_order
    result=''
    if load_balanc_order == 0:
        load_balanc_order += 1
        result = requests.get("http://"+order1+"/purchase/"+str(book_ID)) 
    elif load_balanc_catalog == 1:
        load_balanc_order += 1
        result = requests.get("http://"+order2+"/purchase/"+str(book_ID)) 

    return(result.content)


@app.route('/invalidate/<int:book_ID>', methods=['DELETE'])
def invalidate_Book(book_ID):
    r = requests.delete("http://"+cache+"/invalidate/"+str(book_ID)) 
    return (r.content)

if __name__=="__main__":
    app.run(debug=True)
