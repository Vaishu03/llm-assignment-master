from pymongo import MongoClient
# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['Cluster0']
collection = db['coll']
data = {'name':'Vaishnavi'}
check = collection.insert_one(data)
print(check.inserted_id)
client.close()