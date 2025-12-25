from pymongo import MongoClient
from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv
import os

mongo_uri = os.getenv("MONGODB_URI")
db_name = os.getenv("DB_NAME")
collection_name = os.getenv("COLLECTION_NAME")

# mongodb connections 
# Connect to MongoDB
client = MongoClient(mongo_uri)
# Access database
db = client[db_name]
# Access collection
collection = db[collection_name]
print("Connected to MongoDB")


url = "https://smccity.solapurcorporation.org/counter_receipt_online.aspx/"

response = requests.get(url)
# print(response.text)
soup = BeautifulSoup(response.text,"lxml")
# print(soup.prettify())
form = soup.find('form')
action = form.get("action")
method = form.get("method", "get").lower()

# print(f"form : {form}")
# print(f"action :  {action}")
# print(f"method : {method}")
select = form.find("select",{'name' : "ctl00$ContentPlaceHolder1$ddlpeth"})
# print(select)

options = {}
for option in select.find_all('option'):
    options[option.text] = option.get('value')

# print(options)
viewstate = soup.find('input').get("value")
# print(viewstate)
viewstategenerator = soup.find("input",{'name':'__VIEWSTATEGENERATOR'}).get("value")
# print(type(viewstategenerator))



base_form_data = {
     "__EVENTTARGET" : '',
     "__EVENTARGUMENT":'',
    "__VIEWSTATE": viewstate,
    "__VIEWSTATEGENERATOR": viewstategenerator,
    'ctl00$ContentPlaceHolder1$txtptn':'',
    'ctl00$ContentPlaceHolder1$txtname':"",
    'ctl00$ContentPlaceHolder1$txtaddress':'',
    'ctl00$ContentPlaceHolder1$btnsearch' : 'search',
    "ctl00$ContentPlaceHolder1$pre_print":'',

}

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'cache-control': 'no-cache',
    'content-type': 'application/x-www-form-urlencoded',
    'origin': 'https://smccity.solapurcorporation.org',
    'pragma': 'no-cache',
    'priority': 'u=0, i',
    'referer': 'https://smccity.solapurcorporation.org/counter_receipt_online.aspx',
    'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36',
   
}
 
url_post = 'https://smccity.solapurcorporation.org/counter_receipt_online.aspx/'

for value in options.values():
    form_data = base_form_data.copy()
    form_data["ctl00$ContentPlaceHolder1$ddlpeth"] = value
    res = requests.post(url_post,headers = headers ,data = form_data)
    # print(f"Sent ddlpeth={value} → {response.status_code}")
    soup = BeautifulSoup(res.text,'lxml')
    table = soup.find("table",{"id" : 'ContentPlaceHolder1_Grdfile'})
    # print(table)
    result =  []
    if table is None: 
        continue
    # print(type(table))
    rows = table.find_all('tr')[1:]
    # print(rows)
    for row in rows: 
        # print(row)
        tdata = row.find_all('td')
        if len(tdata) >= 7:
            result.append({
            'view' : tdata[0].text.strip(),
            'proper' : tdata[1].text.strip(),
            'owner' : tdata[2].text.strip(),
            'house' : tdata[3].text.strip(),
            'area' : tdata[4].text.strip(),
            'city' : tdata[5].text.strip(),  
            'types' : tdata[6].text.strip()
            })


    if result:
        collection.insert_many(result)


# form_data ={
# "ctl00$ContentPlaceHolder1$ddlpeth": list(options.values())
# }

# tags = soup.find('select', id='ContentPlaceHolder1_ddlpeth')
# data = tags.find_all('option')
# for i in data:
#     select_name = i.name
#     print(i)
#     data = {
#     "ctl00$ContentPlaceHolder1$ddlpeth":i.text,
#     }

#     res = requests.post('https://smccity.solapurcorporation.org/counter_receipt_online.aspx/',data=data , headers=headers)
#     table = res.find('tbody')
#     print(table)
#     result =  []
#     for row in table.find_all('tr'):
#         col = row.find_all('td')
#         if not col:
#             continue
#         view = col[0].text.strip()
#         proper = col[1].text.strip()
#         owner = col[2].text.strip()
#         house = col[3].text.strip()
#         area = col[4].text.strip()
#         city = col[5].text.strip()
#         types = col[6].text.strip()
#           result.append({
#             "view" : view,
#             "proper" : proper,
#             "owner" : owner,
#             "house" : house,
#             "area" : area,
#             "city" : city,
#             "types" : types,

#           }) 
#         print(view,proper,owner,house,area,city,types)
# collection.insert_many(result)




