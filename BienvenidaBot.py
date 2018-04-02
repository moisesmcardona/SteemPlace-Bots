from steem import Steem
from steem.blockchain import Blockchain
from steem.post import Post
from steem.account import Account
import MySQLdb
import time

pk = ["key"]  # posting key

MySQLHost = 'address'
MySQLDatabase = 'database'
MySQLUsername = 'username'
MySQLPassword = 'password'

steem = Steem(keys=pk[0], nodes=["https://api.steemit.com"])
chain = Blockchain(steemd_instance=steem, mode='head')
BienvenidaAccount = "bienvenida"  # nombre de la cuenta
texto = "## Te doy la bienvenida a Steemit, @{steemuser}\n\nPara ayudarte en la plataforma, he votado en este post y te estoy siguiendo 🙂.\n\nEn esta red existen varias iniciativas que te ayudarán a crecer. [Puedes verlas presionando aquí](https://steem.place/es/Iniciativas)\n\n¡Te deseamos mucho éxito y que disfrutes estar por aquí!\n\n---\n\n<sub>Este bot fue creado por @moisesmcardona. [Si este comentario te ha parecido útil, vótalo como Witness presionando aquí](https://v2.steemconnect.com/sign/account-witness-vote?witness=moisesmcardona&approve=1)</sub>"

already_commented = []  # variable tipo Array que tendrá los usuarios a los que ya hemos contestado
try:
    with open("BienvenidaLogged.txt", "r") as f:  # Aquí van a estar los usuarios que ya hemos contestado
        data = f.read().splitlines()
        f.close()

    for line in data:
        print("loaded user: " + line + " to list")
        already_commented.append(line)
except:
    pass

while True:
    try:
        for op in chain.stream(filter_by=["comment"]):
            permlink = op["permlink"]
            user = op["author"]
            full_link = ("https://steemit.com/tag/@" + user + "/" + permlink)
            comment = Post("@" + user + "/" + permlink, steem)
            if comment.is_main_post():
                tags = (comment["json_metadata"].get("tags", []))
                category = comment.category
                if ('introduceyourself' in tags or 'introducemyself' in tags or 'introduction' in tags or 'bienvenida' in tags) and ('spanish' in tags or 'espanol' in tags or 'castellano' in tags or 'venezuela' in tags):
                    print(time.ctime() + ': New user found:' + user)
                    if (not user in already_commented):
                        try:
                            print(time.ctime() + ': ' + user + ' es un usuario nuevo!')
                            conn = MySQLdb.connect(host=MySQLHost, db=MySQLDatabase, user=MySQLUsername, passwd=MySQLPassword)
                            query = "INSERT INTO bienvenida (username, link, posted) VALUES (%s, %s, %s)"
                            cursor = conn.cursor()
                            cursor.execute(query, (user, "@" + user + "/" + permlink, time.strftime("%Y/%m/%d %H:%M:%S")))
                            conn.commit()
                            conn.close()
                            print(time.ctime() + ': Post insertado en MySQL')
                            comment.reply(body=texto.format(steemuser=user), author=BienvenidaAccount)
                            print(time.ctime() + ': Comentario escrito')
                            steem.vote("@" + user + "/" + permlink, 10.0, account=BienvenidaAccount)
                            print(time.ctime() + ': Post votado')
                            steem.follow(user, what=['blog'], account=BienvenidaAccount)
                            print(time.ctime() + ': Siguiendo')
                            with open("BienvenidaLogged.txt", "a") as f:
                                f.write(user + "\n")  # una linea por usuario contestado
                                f.close()
                            already_commented.append(user)
                            print(time.ctime() + ': Comentario de bienvenida ha sido escrito con éxito:' + user)
                        except Exception as ex:
                            print(ex)
                        else:
                            print(time.ctime() + " Not replying. Already replied.")
                elif ('spanish' in tags or 'espanol' in tags or 'venezuela' in tags or 'bienvenida' in tags or 'castellano' in tags) or ('spanish' in category or 'espanol' in category or 'venezuela' in category or 'bienvenida' in category or 'castellano' in category):
                    user_posted_before = 0  # counter para saber si es el primer post por el usuario
                    account = Account(user, steem)  # se guarda el nombre del usuario aquí
                    if not user in already_commented:
                        print(time.ctime() + ': Verificando el usuario ' + user)
                        for i in account.history(filter_by="comment"):  # Para ver si el user tiene más posts
                            if user_posted_before < 2:
                                d_link = str("@" + i["author"] + "/" + i[
                                    "permlink"])  # link solo desde que se muestra author y link del post
                                d_full_link = ("https://steemit.com/tag/" + d_link)  # link del post completo
                                try:
                                    d_post = Post(d_link, steem)
                                    d_tags = (d_post["json_metadata"].get("tags", []))
                                    d_category = comment.category
                                except:
                                    d_tags = ""
                                if ('spanish' in tags or 'espanol' in tags or 'venezuela' in tags or 'bienvenida' in tags or 'castellano' in tags) or ('spanish' in category or 'espanol' in category or 'venezuela' in category or 'bienvenida' in category or 'castellano' in category):
                                    user_posted_before = user_posted_before + 1
                            else:
                                break
                        if user_posted_before > 1:  # si el counter es mayor de uno significa que no es nuevo
                            print(time.ctime() + ': ' + user + ' no es un usuario nuevo.')
                        else:  # significa que el usuario sólo tiene un post y por lo tanto, es nueva:
                            try:
                                # esta es la función de postear el comentario al post
                                print(time.ctime() + ': ' + user + ' es un usuario nuevo!')
                                conn = MySQLdb.connect(host=MySQLHost, db=MySQLDatabase, user=MySQLUsername,passwd=MySQLPassword)
                                query = "INSERT INTO bienvenida (username, link, posted) VALUES (%s, %s, %s)"
                                cursor = conn.cursor()
                                cursor.execute(query, (user, "@" + user + "/" + permlink, time.strftime("%Y/%m/%d %H:%M:%S")))
                                conn.commit()
                                conn.close()
                                comment.reply(body=texto.format(steemuser=user), author=BienvenidaAccount)
                                steem.vote("@" + user + "/" + permlink, 10.0, account=BienvenidaAccount)
                                steem.follow(user, what=['blog'], account=BienvenidaAccount)
                                with open("BienvenidaLogged.txt", "a") as f:
                                    f.write(user + "\n")
                                    f.close()
                                already_commented.append(user)
                                print(time.ctime() + ': Comentario de bienvenida ha sido escrito con éxito:' + user)
                            except Exception as ex:
                                print(ex)  # ": Ha ocurrido un error. Si ves este mensaje luego del de Comentario de Bienvenida ha sido escrito con éxito, puedes ignorar este mensaje")
    except Exception as ex:
        print(ex)  # "Ha ocurrido un error leyendo el post del user. El programa seguira funcionando")
