
import os
from datetime import timezone, datetime

assets=["BTC","BNB","ETH","DOGE","SHIB","LINK"]
#assets=[]


def renameAllDirectory(asset):
    for f in os.scandir(asset):
        try:
            #dt = datetime.strptime(f.name.replace(".json","").replace("0000000000000000000000000000000000000000000000000000001","1"), '%Y-%m-%d')
            new_file_name=str(hex(int(f.name.replace(".json","").replace("0000000000000000000000000000000000000000000000000000001","1")))).replace("x","").zfill(64)+".json"
            #os.rename(f"./MetaData/{asset}/{f.name}",f"./MetaData/{asset}/{new_file_name}")
            os.rename(f"{asset}/{f.name}",f"{asset}/{new_file_name}")
            print(f"file :{f} rename to : {new_file_name}")
        except:
            continue

if __name__ == "__main__":
    for a in assets:
        renameAllDirectory(f"./MetaData/{a}/")

