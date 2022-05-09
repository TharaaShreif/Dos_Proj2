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
#==============================================================================================
#============================ Catalog server requests ===========================================
#==============================================================================================
catalog1="192.168.1.106:3000"
catalog2="192.168.1.106:4000"
# catalog3="172.19.2.60:5000"
cache="192.168.1.220:2000"
order1="192.168.1.220:3000"
order2="192.168.1.220:4000"
# order3="172.19.2.50:5000"
# 172.19.19.157  
#============================= 1- search operation ====================================
#getting the books info which have the topic s_topic #request to catalogServer
@app.route('/search/<topic>', methods=['GET']) # wait for requist http://192.168.1.84:5000/search/ operation type Get
def search(topic): # this function for response
    global load_balanc_catalog
    cResult = requests.get("http://"+cache+"/search/"+str(topic)) # send request to cache server
    
    cachRes = cResult.json()
    result=''
    # msg= str(cachRes.get('msg'))
    print(cachRes)
    if (len(cachRes)<4 and topic=='Undergraduat school') or( len(cachRes)<3 and topic=='Distributed systems'):
        if load_balanc_catalog == 0:
            load_balanc_catalog += 1
            result = requests.get("http://"+catalog1+"/search/"+str(topic)) # send request to catalog_server1
            
        elif load_balanc_catalog == 1:
            load_balanc_catalog = 0
            result = requests.get("http://"+catalog2+"/search/"+str(topic)) # send request to catalog_server1
            
        # elif load_balanc_catalog == 2:
        #     load_balanc_catalog = 0
        #     result = requests.get("http://"+catalog3+"/search/"+str(topic)) # send request to catalog_server1
            
        catRes=result.json()
        # dectCat=json.loads(catRes)
        # dectCach=json.loads(cachRes)
        for catItem in catRes:
            # print("========================="+catItem+"=================")
            book=get_info(catItem.get('id'))
            # requests.post("http://"+cache+"/addBook/",data={'id':catItem.get('id'),'title':book[1],'price':book[2],'quantity':book[3],'topic':book[4]})
        return (result.content)
    else:
        return(cachRes)

        

#============================== 2- info operation ====================================
#send request to the cataloge server to get information about id book
@app.route('/info/<int:bookID>', methods=['GET'])
def get_info(bookID):
  global load_balanc_catalog
  #this is the request to be sent to the catalog server
  cResult = requests.get("http://"+cache+"/info/"+str(bookID)) # send request to cache server
  print("=============================="+cResult.text+"=================================")
  res =cResult.json()
  msg= str(res.get('msg'))
  if msg == 'None': # there is a book in cache
      print("========== there is abook in cache")
      return(cResult.content)
  else:  # the book dose not exisit in the cache 
      if load_balanc_catalog == 0:
          load_balanc_catalog += 1
          result = requests.get("http://"+catalog1+"/info/"+str(bookID)) # send request to catalog_server1
          
      elif load_balanc_catalog == 1:
          load_balanc_catalog =0
          result = requests.get("http://"+catalog2+"/info/"+str(bookID)) # send request to catalog_server2
          
    #   elif load_balanc_catalog == 2:
    #       load_balanc_catalog = 0
    #       result = requests.get("http://"+catalog3+"/info/"+str(bookID)) # send request to catalog_server3
          
      res=result.json()
      resul =requests.post("http://"+cache+"/addBook/",data={'id':bookID,'title':res.get('title'),'price':res.get('price'),'quantity':res.get('quantity'),'topic':res.get('topic')})
  return (res)


# @app.route('/addBook/', methods=['POST'])
# def addBook():
#     resul =requests.post("http://192.168.1.84:2000/addBook/",data={'id':1,'title':'hi','price':2,'quantity':3,'topic':'ffff'})
#     return (resul.content)


#============================= 3- update price ========================================

#update the price of a book 
@app.route('/update_price/<int:bookID>', methods=['PUT'])
def update_book_price(bookID):
    global load_balanc_catalog
    price = request.json['price']
    result=''
    if load_balanc_catalog == 0:
            load_balanc_catalog += 1
            result = requests.put("http://"+catalog1+"/update_price/"+str(bookID),data={'price':price}) # send request to catalog_server1
    elif load_balanc_catalog == 1:
        load_balanc_catalog = 0
        result = requests.put("http://"+catalog2+"/update_price/"+str(bookID),data={'price':price}) # send request to catalog_server2
    # elif load_balanc_catalog == 2:
    #     load_balanc_catalog = 0
    #     result = requests.put("http://"+catalog3+"/update_price/"+str(bookID),data={'price':price}) # send request to catalog_server3
    
    return (result.content)

#============================= 4- update quantity ========================================

            #=================== increease quantity =================
 
@app.route('/increase_quantity/<int:bookID>', methods=['PUT'])
def increase_book_quantity(bookID):
    new_amount = request.json['new_amount']
    global load_balanc_catalog
    result=''
    if load_balanc_catalog == 0:
            load_balanc_catalog += 1
            result = requests.put("http://"+catalog1+"/increase_quantity/"+str(bookID),data={'new_amount':new_amount}) # send request to catalog_server1
    elif load_balanc_catalog == 1:
        load_balanc_catalog = 0
        result = requests.put("http://"+catalog2+"/increase_quantity/"+str(bookID),data={'new_amount':new_amount}) # send request to catalog_server2
    # elif load_balanc_catalog == 2:
    #     load_balanc_catalog = 0
    #     result = requests.put("http://"+catalog3+"/increase_quantity/"+str(bookID),data={'new_amount':new_amount}) # send request to catalog_server3

    return(result.content)

            #=================== decreease quantity =================
 
@app.route('/decrease_quantity/<int:bookID>', methods=['PUT'])
def decrease_book_quantity(bookID):
    new_amount = request.json['new_amount']
    global load_balanc_catalog
    result=''
    if load_balanc_catalog == 0:
            load_balanc_catalog += 1
            result = requests.put("http://"+catalog1+"/decrease_quantity/"+str(bookID),data={'new_amount':new_amount}) # send request to catalog_server1
    elif load_balanc_catalog == 1:
        load_balanc_catalog = 0
        result = requests.put("http://"+catalog2+"/decrease_quantity/"+str(bookID),data={'new_amount':new_amount}) # send request to catalog_server2
    # elif load_balanc_catalog == 2:
    #     load_balanc_catalog = 0
    #     result = requests.put("http://"+catalog3+"/decrease_quantity/"+str(bookID),data={'new_amount':new_amount}) # send request to catalog_server3

    return(result.content)


#==============================================================================================
#============================ Order server requests ===========================================
#==============================================================================================

#====================== purchase ====================================================
@app.route('/purchase/<int:bookID>', methods=['PUT'])
def purchase(bookID):
    global load_balanc_order
    result=''
    if load_balanc_order == 0:
        load_balanc_order += 1
        result = requests.get("http://"+order1+"/purchase/"+str(bookID)) # send request to catalog_server1
    elif load_balanc_catalog == 1:
        load_balanc_order += 1
        result = requests.get("http://"+order2+"/purchase/"+str(bookID)) # send request to catalog_server2
    # elif load_balanc_order== 2:
    #     load_balanc_order = 0
    #     result = requests.get("http://"+order3+"/purchase/"+str(bookID)) # send request to catalog_server3

    return(result.content)


# =========================== invalidate =================================== 
@app.route('/invalidate/<int:bookID>', methods=['DELETE'])
def invalidate_Book(bookID):
    r = requests.delete("http://"+cache+"/invalidate/"+str(bookID)) 
    return (r.content)

if __name__=="__main__":
    app.run(debug=True)