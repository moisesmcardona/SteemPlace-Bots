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

def checkIfUserIsInPostNotificationDatabase(post_author):
    conn = MySQLdb.connect(host=MySQLHost, db=MySQLDB, user=MySQLUsername, passwd=MySQLPass)
    query = "SELECT DISTINCT drupalkey, user, account FROM postnotification WHERE enabled = 1 AND account = '%s'" % (post_author)
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

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
        messagetitle = "@" + user + ", ¡@" + post_author + " ha escrito un nuevo post!"
        messagetosend = "Hola, <a href=https://steemit.com/@" + user + ">@" + user + "</a><br><br><a href=https://steemit.com/@" + post_author + ">@" + post_author + "</a> ha escrito un nuevo post. Míralo aquí:<br><br><a href=" + full_link + ">" + full_link + "</a><br><br>Atentamente,<br>Steem.Place"
    else:
        print("sending email in english")
        messagetitle = "@" + user + ", @" + post_author + " has written a new post!"
        messagetosend = "Hi, <a href=https://steemit.com/@" + user + ">@" + user + "</a><br><br><a href=https://steemit.com/@" + post_author + ">@" + post_author + "</a> has written a new post. See it here:<br><br><a href=" + full_link + ">" + full_link + "</a><br><br>Sincerely,<br>Steem.Place"
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
            if parent_author == '':
                print("checking", post_author)
                user_in_table = checkIfUserIsInPostNotificationDatabase(post_author)
                for user in user_in_table:
                    print("Sending email for user", user[1])
                    key_to_use = user[0]
                    get_email_address = getSteemPlaceUserEmailAndLanguage(key_to_use)
                    if get_email_address is not None:
                        sendMail(get_email_address, user[1], post_author, post_link)
                    else:
                        print("Email address not found")
    except Exception as ex:
        print(ex)

