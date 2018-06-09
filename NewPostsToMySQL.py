from steem import Steem
from steem.blockchain import Blockchain
import MySQLdb
import json

def sendToMySQL(username, link, permlink, server):
    try:
        MySQLHost = 'address'
        MySQLDB = 'database'
        MySQLUsername = 'username'
        MySQLPassword = 'password'
        print('Nuevo post para {servidor} detectado: {usuario}/{permlink}'.format(servidor=server, usuario=username, permlink=permlink))
        print("Intentando insertar en MySQL")
        conn = MySQLdb.connect(host=MySQLHost, db=MySQLDB, user=MySQLUsername, passwd=MySQLPassword)
        query = "INSERT INTO newposts (username, link, channel) VALUES (%s, %s, %s)"
        cursor = conn.cursor()
        cursor.execute(query, (username, link, server))
        conn.commit()
        conn.close()
        save = True
        print('Nuevo post para {servidor} insertado en MySQL: {usuario}/{permlink}'.format(servidor=server, usuario=username, permlink=permlink))
    except:
        save = False
        print("Error insertando post")
    return save

steem = Steem(nodes=["httpsnode.steem.place"])
chain = Blockchain(steem, mode='head')

already_posted = []
try:
    with open("PostsPosted.txt", "r") as f:
        data = f.read().splitlines()
        f.close()

    for line in data:
        print("loaded link: " + line + " to list")
        already_posted.append(line)
except:
    pass

while True:
    try:
        for op in chain.stream(filter_by=["comment"]):
            if op["parent_author"] == '':
                tags = json.loads(op['json_metadata'])
                tags = tags['tags']
                link = ("https://steemit.com/tag/@" + op["author"] + "/" + op["permlink"])
                try:
                    if not op["author"] + '/' + op["permlink"] in already_posted:
                        save = False
                        if 'spanish' in tags or 'espanol' in tags or 'castellano' in tags:
                            save = sendToMySQL(op["author"], link, op["permlink"], "castellano")
                        if 'castellano' in tags and 'venezuela' in tags and 'concursovenezuela' in tags:
                            save = sendToMySQL(op["author"], link, op["permlink"], "concursovenezuela")
                        if 'minotaurototal' in tags:
                            save = sendToMySQL(op["author"], link, op["permlink"], "minotaurototal")
                        if 'pitchperfect' in tags:
                            save = sendToMySQL(op["author"], link, op["permlink"], "pitchperfect")
                        if 'rutablockchain' in tags:
                            save = sendToMySQL(op["author"], link, op["permlink"], "rutablockchain")
                        if 'slothicorn' in tags:
                            save = sendToMySQL(op["author"], link, op["permlink"], "slothicorn")
                        if 'theunion' in tags:
                            save = sendToMySQL(op["author"], link, op["permlink"], "theunion")
                        if save == True:
                            with open("PostsPosted.txt", "a") as f:  # guardamos el usuario en el archivo
                                f.write(op["author"] + "/" + op["permlink"] + "\n")  # una linea por usuario contestado
                                f.close()
                            already_posted.append(op["author"] + '/' + op["permlink"])
                except:
                    print("Ha ocurrido un error leyendo el post. El programa seguira funcionando")
    except:
        print("Ha ocurrido leyendo parent_author.")
