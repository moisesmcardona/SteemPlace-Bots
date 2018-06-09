from steem import Steem
from steem.blockchain import Blockchain
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

def checkIfUserHasReplyEnabled(parent_author):
    conn = MySQLdb.connect(host=MySQLHost, db=MySQLDB, user=MySQLUsername, passwd=MySQLPass)
    query = "SELECT DISTINCT drupalkey, replyenabled FROM settings WHERE username = '%s'" % (parent_author)
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchone()

def getSteemPlaceUserEmailAndLanguage(key_to_use):
    conn = MySQLdb.connect(host=MySQLHost, db=MySQLDB2, user=MySQLUsername, passwd=MySQLPass)
    query = "SELECT DISTINCT mail, language FROM users WHERE uid = %d" % (key_to_use)
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchone()

def sendMail(record2, user, post_author, post_link):
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
        messagetitle = "@" + user + ", tienes un nuevo comentario de @" + post_author
        messagetosend = "Hola, <a href=https://steemit.com/@" + user + ">@" + user + "</a><br><br>tienes un nuevo comentario de <a href=https://steemit.com/@" + post_author + ">@" + post_author + "</a>:<br><br><a href=" + full_link + ">" + full_link + "</a><br><br>Atentamente,<br>Steem.Place"
    else:
        print("sending email in english")
        messagetitle = "@" + user + ", you have a new comment by @" + post_author
        messagetosend = "Hi, <a href=https://steemit.com/@" + user + ">@" + user + "</a><br><br>You have a new comment by <a href=https://steemit.com/@" + post_author + ">@" + post_author + "</a>:<br><br><a href=" + full_link + ">" + full_link + "</a><br><br>Sincerely,<br>Steem.Place"
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
            try:
                if parent_author != '':
                    print("checking", parent_author)
                    user_requested_reply_email = checkIfUserHasReplyEnabled(parent_author)
                    if user_requested_reply_email is not None:
                        found = True
                        key_to_use = user_requested_reply_email[0]
                        enabled = user_requested_reply_email[1]
                        if found:
                            print("user found!")
                            if enabled == 1:
                                print("email enabled")
                                get_user_address = getSteemPlaceUserEmailAndLanguage(key_to_use)
                                if get_user_address is not None:
                                    sendMail(get_user_address, parent_author, post_author, post_link)
                                else:
                                    print("Email address not found")
                            else:
                                print("not enabled")
                        else:
                            print("Record not found")
            except Exception as ex:
                print(ex)
    except Exception as ex:
        print(ex)
