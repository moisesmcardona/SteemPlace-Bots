from steem import Steem
from steem.blockchain import Blockchain
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import MySQLdb

steem = Steem(nodes=["https://api.steemit.com"])
chain = Blockchain(steemd_instance=steem, mode='head')

MySQLHost = 'address'
MySQLDB = 'database'
MySQLDB2 = 'drupal_database'
MySQLUsername = 'username'
MySQLPass = 'password'

while True:
    try:
        for op in chain.stream(filter_by=["comment"]):
            postauthor = op["author"]
            postlink = op["permlink"]
            wordarray = op["body"].split(' ')
            mentionlist = []
            for word in wordarray:
                mentionstring = ""
                getstring = False
                for i in range(0, len(word)):
                    letters = set("<>|/\!#$%^&*()=+,'?")
                    if letters & set(word[i]):
                        break
                    if "\n" in word[i]:
                        break
                    if getstring == True:
                        mentionstring = mentionstring + word[i]
                    if "@" in word[i]:
                        getstring = True
                if mentionstring != "":
                    if not "@" in mentionstring:
                        mentionstring = mentionstring.lower()
                        if mentionstring.endswith('.'):
                            mentionstring = mentionstring[:-1]
                        if not mentionstring in mentionlist:
                            conn = MySQLdb.connect(host=MySQLHost, db=MySQLDB, user=MySQLUsername, passwd=MySQLPass)
                            query = "INSERT INTO mentions (author, link, username, time) VALUES (%s, %s, %s, %s)"
                            cursor = conn.cursor()
                            cursor.execute(query,(postauthor, postlink, mentionstring, time.strftime("%Y/%m/%d %H:%M:%S")))
                            conn.commit()
                            conn.close()
                            print(mentionstring)
                            try:
                                conn = MySQLdb.connect(host=MySQLHost, db=MySQLDB, user=MySQLUsername, passwd=MySQLPass)
                                query = "SELECT DISTINCT drupalkey, notifyenabled FROM settings WHERE username = '%s'" % (mentionstring)
                                print("query set")
                                cursor = conn.cursor()
                                cursor.execute(query)
                                record1 = cursor.fetchone()
                                keytouse = 0
                                enabled = 0
                                found = False
                                print("query executed. Getting Record")
                                if record1 is not None:
                                    found = True
                                    print("checking")
                                    keytouse = record1[0]
                                    enabled = record1[1]
                                if found == True:
                                    print("user found 1")
                                    if enabled == 1:
                                        print("email enabled")
                                        conn = MySQLdb.connect(host=MySQLHost, db=MySQLDB2, user=MySQLUsername,passwd=MySQLPass)
                                        query = "SELECT DISTINCT mail, language FROM users WHERE uid = %d" % (keytouse)
                                        cursor = conn.cursor()
                                        cursor.execute(query)
                                        record2 = cursor.fetchone()
                                        mailtouse = ""
                                        languagetosend = ""
                                        if record2 is not None:
                                            mailtouse = record2[0]
                                            languagetosend = record2[1]
                                            print("Email found")
                                            print("begin email")
                                            msg = MIMEMultipart()
                                            # Send email
                                            msg['From'] = 'noreply@steem.place'
                                            msg['To'] = mailtouse
                                            messagetosend = ""
                                            messagetitle = ""
                                            print("1")
                                            fulllink = "https://steemit.com/tag/@" + postauthor + "/" + postlink
                                            print("1 1/2")
                                            print(languagetosend)
                                            if "es" in languagetosend:
                                                print("setting message spanish")
                                                messagetitle = "@" + mentionstring + ", has sido mencionado en un post"
                                                messagetosend = "Hola, <a href=https://steemit.com/@" + mentionstring + ">@" + mentionstring + "</a><br><br>Has sido mencionado en el siguiente post de <a href=https://steemit.com/@" + postauthor + ">@" + postauthor + "</a>:<br><br><a href=" + fulllink + ">" + fulllink + "</a><br><br>Atentamente,<br>Steem.Place"
                                            else:
                                                print("setting message english")
                                                messagetitle = "@" + mentionstring + ", you have been mentioned in a post"
                                                messagetosend = "Hi, <a href=https://steemit.com/@" + mentionstring + ">@" + mentionstring + "</a><br><br>You have been mentioned in the following post by <a href=https://steemit.com/@" + postauthor + ">@" + postauthor + "</a>:<br><br><a href=" + fulllink + ">" + fulllink + "</a><br><br>Sincerelly,<br>Steem.Place"
                                            print("1 1/3")
                                            msg['Subject'] = messagetitle
                                            print("1 1/4")
                                            message = messagetosend
                                            print("2")
                                            msg.attach(MIMEText(message, 'html'))
                                            mailserver = smtplib.SMTP('smtp-relay.gmail.com', 587)
                                            print("3")
                                            # identify ourselves to smtp gmail client
                                            mailserver.ehlo()
                                            print("4")
                                            # secure our email with tls encryption
                                            mailserver.starttls()
                                            print("5")
                                            # re-identify ourselves as an encrypted connection
                                            mailserver.ehlo()
                                            print("6")
                                            # mailserver.login('me@gmail.com', 'mypassword')
                                            mailserver.sendmail('noreply@steem.place', mailtouse, msg.as_string())
                                            print("7")
                                            mailserver.quit()
                                            print("Email sent")
                                        else:
                                            print("Email address not found")
                                    else:
                                        print("not enabled")
                                else:
                                    print("Record not found")
                            except Exception as inst:
                                print(inst)
                        mentionlist.append(mentionstring)
            mentionlist.clear()
    except Exception as inst:
        print(inst)
