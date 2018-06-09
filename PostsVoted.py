from steem import Steem
from steem.blockchain import Blockchain
import time
import MySQLdb

steem = Steem(nodes=["https://httpsnode.steem.place"])
chain = Blockchain(steemd_instance=steem, mode='head')

MySQLHost = 'address'
MySQLDB = 'database'
MySQLUsername = 'username'
MySQLPassword = 'password'

while True:
    try:
        for op in chain.stream(filter_by=["vote"]):
            link = op["permlink"]
            author = op["author"]
            voter = op["voter"]
            weight = op["weight"] / 100
            conn = MySQLdb.connect(host=MySQLHost,db=MySQLDB,user=MySQLUsername,passwd=MySQLPassword)
            query = "INSERT INTO votes (author, permlink, voter, weight, date) VALUES (%s, %s, %s, %s, %s)"
            cursor = conn.cursor()
            cursor.execute(query, (author, link, voter, str(weight), time.strftime("%Y/%m/%d %H:%M:%S")))
            conn.commit()
            conn.close()
            print(time.ctime() + ": New vote from " + voter + " on post " + link + " from " + author + ". Voted with " + str(weight) + "%")
    except:
        print("Error occurred reading blockchain\n")
