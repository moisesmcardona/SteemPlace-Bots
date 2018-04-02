from steem import Steem
from steem.blockchain import Blockchain
from steem.post import Post
import time
import MySQLdb

MySQLHost = 'address'
MySQLDatabase = 'database'
MySQLUsername = 'username'
MySQLPassword = 'password'

steem = Steem(nodes=["https://api.steemit.com"])
chain = Blockchain(steemd_instance=steem, mode='head')

already_commented = []
data = []

try:
    with open("IntroduceYourselfLogged.txt", "r") as f:
        data = f.read().splitlines()
        f.close()

    for line in data:
        print(time.ctime() + " loaded user: " + line + " to list")
        already_commented.append(line)
except:
    pass

while True:
    try:
        for op in chain.stream(filter_by=["comment"]):
            permlink = op["permlink"]
            author = op["author"]
            post = Post("@" + author + "/" + permlink, steem)
            tags = (post["json_metadata"].get("tags", []))
            if post.is_main_post():
                if 'introduceyourself' in tags or 'introducemyself' in tags or 'introduction' in tags:
                    print(time.ctime() + ' New IntroduceYourself Post found:' + author)
                    if not author in already_commented:
                        print(time.ctime() + ' Adding post from ' + author + ' to database')
                        conn = MySQLdb.connect(host=MySQLHost, db=MySQLDatabase, user=MySQLUsername,passwd=MySQLPassword)
                        query = "INSERT INTO introduceyourself (username, link, posted) VALUES (%s, %s, %s)"
                        cursor = conn.cursor()
                        cursor.execute(query,(author, "@" + author + "/" + permlink, time.strftime("%Y/%m/%d %H:%M:%S")))
                        conn.commit()
                        conn.close()
                        with open("IntroduceYourselfLogged.txt", "a") as f:
                            f.write(author + "\n")
                            f.close()
                            already_commented.append(author)
                        print(time.ctime() + ': Post from ' + author + ' added to database successfully')
                    else:
                        print(time.ctime() + " User Already Added to Database.")
            else:
                print(time.ctime() + ' Post is comment')
    except Exception as ex:
        print(ex)
