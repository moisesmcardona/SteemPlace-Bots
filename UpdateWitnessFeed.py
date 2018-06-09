import urllib.request, json
from steem import Steem
from time import sleep

def updateWitnessFeed(price):
    pk = ["key"]
    witness_account = "account"
    steem = Steem(keys=pk[0], nodes=["https://httpsnode.steem.place"])
    print("Updating price feed with price: $", price)
    try:
        steem.witness_feed_publish(price, quote='1.000', account=witness_account)
        print("Price updated successfully!")
    except Exception as ex:
        print("An error occurred")
        print(str(ex))

while True:
    url = "https://api.coinmarketcap.com/v2/ticker/1312/"
    response = urllib.request.urlopen("https://api.coinmarketcap.com/v2/ticker/1312/")
    data = json.loads(response.read().decode())
    price = round(float(data["data"]["quotes"]["USD"]["price"]), 3)
    updateWitnessFeed(price)
    sleep(60 * 60) #runs every 60 minutes / 1 hour'

