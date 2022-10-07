import json
import requests
import time
import os
import json

PINATA_BASE_URL="https://api.pinata.cloud/"
PINATA_ENDPOINT="pinning/unpin/"
PINATA_HEADERS={"pinata_api_key":"","pinata_secret_api_key":"","Content_Type":"application/json"}

def unpin(cid):
    response=requests.delete(PINATA_BASE_URL+PINATA_ENDPOINT+cid,headers=PINATA_HEADERS)
    print(f"unpin cid : {cid} status:{response.content}")
    time.sleep(0.5)
    pass


if __name__ == "__main__":
    for f in os.scandir("./MetaData/SHIB/"):
        jsonObj=json.load(open(f))
        cid=jsonObj["image"].replace("https://ipfs.io/ipfs/","").split("?")[0]
        unpin(cid)
        os.remove(f)
        time.sleep(0.5)