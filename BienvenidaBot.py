import json
import time
import MySQLdb
import os
from steem import Steem
from steem.blockchain import Blockchain

pk = ["key"]  # posting key

MySQLHost = 'address'
MySQLDatabase = 'database'
MySQLUsername = 'username'
MySQLPassword = 'password'

steem = Steem(keys=pk[0], nodes=["https://httpsnode.steem.place"])
chain = Blockchain(steemd_instance=steem, mode='head')
BienvenidaAccount = "bienvenida"  # nombre de la cuenta
texto = "## Te doy la bienvenida a Steemit, @{steemuser}\n\nPara ayudarte en la plataforma, he votado en este post y te estoy siguiendo 🙂\n\n[Te recomiendo la siguiente lista de iniciativas y comunidades de la comunidad hispana que puedes ver presionando aquí](https://steem.place/es/Iniciativas?usuario={steemuser}) las cuales pueden ser de tu interés y están a la mayor disposición de ayudar a gente nueva como tú.\n\n¡Te deseamos mucho éxito y que disfrutes estar por aquí!\n\n---\n\n<sub>Este bot fue creado por @moisesmcardona. [Si este comentario te ha parecido útil, vótalo como Witness presionando aquí](https://v2.steemconnect.com/sign/account-witness-vote?witness=moisesmcardona&approve=1)</sub>"

already_commented = []  # variable tipo Array que tendrá los usuarios a los que ya hemos contestado

if os.path.exists("BienvenidaLogged.txt"):
    with open("BienvenidaLogged.txt", "r") as f:  # Aquí van a estar los usuarios que ya hemos contestado
        data = f.read().splitlines()
        f.close()
    for line in data:
        print("loaded user: " + line + " to list")
        already_commented.append(line)

while True:
    try:
        for op in chain.stream(filter_by=["comment"]):
            permlink = op["permlink"]
            user = op["author"]
            if op["parent_author"] == '':
                print(time.ctime() + ": Verificando usuario", user)
                tags = json.loads(op['json_metadata'])
                tags = tags['tags']
                if ('introduceyourself' in tags or 'introducemyself' in tags or 'introduction' in tags or 'bienvenida' in tags or 'gentenueva' in tags or 'introduccion' in tags) and ('spanish' in tags or 'espanol' in tags or 'castellano' in tags or 'venezuela' in tags or 'cervantes' in tags):
                    print(time.ctime() + ': Post de introducción encontrado:' + user)
                    if not user in already_commented:
                        try:
                            print(time.ctime() + ': ' + user + ' es un usuario nuevo!')
                            conn = MySQLdb.connect(host=MySQLHost, db=MySQLDatabase, user=MySQLUsername, passwd=MySQLPassword)
                            query = "INSERT INTO bienvenida (username, link, posted) VALUES (%s, %s, %s)"
                            cursor = conn.cursor()
                            cursor.execute(query, (user, "@" + user + "/" + permlink, time.strftime("%Y/%m/%d %H:%M:%S")))
                            conn.commit()
                            conn.close()
                            print(time.ctime() + ': Post insertado en MySQL')
                            steem.post("Mensaje de Bienvenida a " + user, texto.format(steemuser=user), BienvenidaAccount, permlink="bienvenida-" + str(user).replace(".", "") + "-" + permlink, reply_identifier="@" + user + "/" + permlink, self_vote=False)
                            print(time.ctime() + ': Comentario escrito')
                            steem.vote("@" + user + "/" + permlink, 10.0, account=BienvenidaAccount)
                            print(time.ctime() + ': Post votado')
                            steem.follow(user, what=['blog'], account=BienvenidaAccount)
                            print(time.ctime() + ': Siguiendo')
                            with open("BienvenidaLogged.txt", "a") as f:
                                f.write(user + "\n")  # una linea por usuario contestado
                                f.close()
                            already_commented.append(user)
                            print(time.ctime() + ': Comentario de bienvenida ha sido escrito con éxito: ' + user)
                        except Exception as ex:
                            print(ex)
                    else:
                        print(time.ctime() + ": Ya se había comentado este post de bienvenida")
    except Exception as ex:
        print(ex)  # "Ha ocurrido un error leyendo el post del user. El programa seguira funcionando")
