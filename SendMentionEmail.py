from steem import Steem
from steem.blockchain import Blockchain
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import MySQLdb

steem = Steem(nodes=["https://httpsnode.steem.place"])
chain = Blockchain(steemd_instance=steem, mode='head')

MySQLHost = 'address'
MySQLDB = 'database'
MySQLDB2 = 'drupal_database'
MySQLUsername = 'username'
MySQLPass = 'password'

def insertMentionInMySQL(post_author, post_link, mention_string):
    conn = MySQLdb.connect(host=MySQLHost, db=MySQLDB, user=MySQLUsername, passwd=MySQLPass)
    query = "INSERT INTO mentions (author, link, username, time) VALUES (%s, %s, %s, %s)"
    cursor = conn.cursor()
    cursor.execute(query, (post_author, post_link, mention_string, time.strftime("%Y/%m/%d %H:%M:%S")))
    conn.commit()
    conn.close()
    print(mention_string)

def getSteemPlaceUserFromMentionString(mention_string):
    conn = MySQLdb.connect(host=MySQLHost, db=MySQLDB, user=MySQLUsername, passwd=MySQLPass)
    query = "SELECT DISTINCT drupalkey, notifyenabled FROM settings WHERE username = '%s'" % (mention_string)
    print("query set")
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchone()

def getSteemPlaceUserEmailAndLanguage(key_to_use):
    conn = MySQLdb.connect(host=MySQLHost, db=MySQLDB2, user=MySQLUsername, passwd=MySQLPass)
    query = "SELECT DISTINCT mail, language FROM users WHERE uid = %d" % (key_to_use)
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchone()

def getPostOrComment(parent_author):
    if parent_author == '':
        postOrComment = "post"
    else:
        postOrComment = "comentario"
    return postOrComment

def sendMail(record2, mention_string, post_author, post_link):
    mailtouse = record2[0]
    languagetosend = record2[1]
    print("Email found")
    print("begin email")
    msg = MIMEMultipart()
    # Send email
    msg['From'] = 'noreply@steem.place'
    msg['To'] = mailtouse
    full_link = "https://steemit.com/tag/@" + post_author + "/" + post_link
    print(languagetosend)
    if "es" in languagetosend:
        print("sending email in spanish")
        postOrComment = getPostOrComment(parent_author)
        messagetitle = "@" + mention_string + ", has sido mencionado en un " + postOrComment + " de @" + post_author
        messagetosend = "Hola, <a href=https://steemit.com/@" + mention_string + ">@" + mention_string + "</a><br><br>Has sido mencionado en el siguiente " + postOrComment + " de <a href=https://steemit.com/@" + post_author + ">@" + post_author + "</a>:<br><br><a href=" + full_link + ">" + full_link + "</a><br><br>Atentamente,<br>Steem.Place"
    else:
        print("sending email in english")
        postOrComment = getPostOrComment(parent_author)
        messagetitle = "@" + mention_string + ", you have been mentioned in a " + postOrComment + " by @" + post_author
        messagetosend = "Hi, <a href=https://steemit.com/@" + mention_string + ">@" + mention_string + "</a><br><br>You have been mentioned in the following " + postOrComment + " by <a href=https://steemit.com/@" + post_author + ">@" + post_author + "</a>:<br><br><a href=" + full_link + ">" + full_link + "</a><br><br>Sincerely,<br>Steem.Place"
    msg['Subject'] = messagetitle
    message = messagetosend
    msg.attach(MIMEText(message, 'html'))
    mailserver = smtplib.SMTP('smtp-relay.gmail.com', 587)
    # identify ourselves to smtp gmail client
    mailserver.ehlo()
    # secure our email with tls encryption
    mailserver.starttls()
    # re-identify ourselves as an encrypted connection
    mailserver.ehlo()
    # mailserver.login('me@gmail.com', 'mypassword')
    mailserver.sendmail('noreply@steem.place', mailtouse, msg.as_string())
    mailserver.quit()
    print("Email sent")

while True:
    try:
        for op in chain.stream(filter_by=["comment"]):
            parent_author = op["parent_author"]
            post_author = op["author"]
            post_link = op["permlink"]
            wordarray = op["body"].split(' ')
            mentionlist = []
            for word in wordarray:
                mention_string = ""
                getstring = False
                for i in range(0, len(word)):
                    letters = set("<>|/\!#$%^&*()=+,'?")
                    if letters & set(word[i]):
                        break
                    if "\n" in word[i]:
                        break
                    if getstring == True:
                        mention_string = mention_string + word[i]
                    if "@" in word[i]:
                        getstring = True
                if mention_string != "":
                    if not "@" in mention_string:
                        mention_string = mention_string.lower()
                        if mention_string.endswith('.'):
                            mention_string = mention_string[:-1]
                        if not mention_string in mentionlist:
                            insertMentionInMySQL(post_author, post_link, mention_string)
                            try:
                                record1 = getSteemPlaceUserFromMentionString(mention_string)
                                found = False
                                print("query executed. Getting Record")
                                if record1 is not None:
                                    found = True
                                    print("checking")
                                    key_to_use = record1[0]
                                    enabled = record1[1]
                                if found:
                                    print("user found 1")
                                    if enabled == 1:
                                        print("email enabled")
                                        record2 = getSteemPlaceUserEmailAndLanguage(key_to_use)
                                        if record2 is not None:
                                            sendMail(record2, mention_string, post_author, post_link)
                                        else:
                                            print("Email address not found")
                                    else:
                                        print("not enabled")
                                else:
                                    print("Record not found")
                            except Exception as inst:
                                print(inst)
                        mentionlist.append(mention_string)
            mentionlist.clear()
    except Exception as inst:
        print(inst)
