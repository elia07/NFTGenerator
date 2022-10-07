from distutils.log import info
from logging import warning
from matplotlib.pyplot import close, margins
from numpy import true_divide
import pandas as pd
import plotly.graph_objects as go
import datetime
from datetime import timedelta, timezone, date
from PIL import Image
from sample_metadata import metadata_template 
from pathlib import Path
import requests
import json
import os
import time
import glob
from updateMetaData import update
import copy
from unpinPinata import unpin

DAY_OFFSET=-4 
UPLOAD_IPFS=True

def generate(str,dt,endDate,rareDays,plot_color,roundNum,birthDate=None,forceRare=False):
    while dt <= endDate:
        warning(f" coin:{str} year:{dt.year} month:{dt.month} day:{dt.day}")
        df = pd.read_csv(f'./DataSource/{str}-USD.csv', index_col=0, parse_dates=True)
        #df.index = df.index.strftime("%d-%m-%Y")
        dt_range = pd.date_range(start=(dt+timedelta(days=DAY_OFFSET)).strftime("%Y-%m-%d"), end=dt.strftime("%Y-%m-%d"))
        df = df[df.index.isin(dt_range)]
        df.head()
        

        candlestick = go.Candlestick(
                                    x=df.index,
                                    open=df['Open'],
                                    high=df['High'],
                                    low=df['Low'],
                                    close=df['Close']
                                    )

        fig = go.Figure(data=[candlestick])
    
        
        close=round(df['Close'][4],roundNum)
        open=round(df['Open'][4],roundNum)
        high=round(df['High'][4],roundNum)
        low=round(df['Low'][4],roundNum)
        
        fig.update_xaxes(
                title_text = f"OHLC : {open} , {high} , {low} , {close}",
                title_font = {"size": 12},
                title_standoff = 0,
                dtick="tick0",
                automargin=True
                )
        
        fig.update_layout(
            width=402, height=400,
            title=dt.strftime("%Y-%m-%d"),
            title_x=0.94,
            title_y=0.91,
            xaxis_rangeslider_visible=False,
            margin=dict(l=45, r=77, t=100, b=20),
            paper_bgcolor='rgba(224,227,235,1)',
            plot_bgcolor=plot_color
        )

                

        #fig.show()
        image_name=f"images/{str}/{str}USDT-{dt.year}-{dt.month}-{dt.day}.png"
        fig.write_image(image_name)
        
        #Read the two images
        img_cur = Image.open(image_name)
        img_cur=img_cur.convert("RGBA")
        
        img_placeholder=None
        #if bullish
        #if christmas
        #if rareday
        #if birthday
        isRare=False
        if (open<close and (close*100/open)-100>=10) or (birthDate!=None and (birthDate.month==dt.month and birthDate.day==dt.day)) or (dt.month==1 and dt.day==1) or (dt in rareDays) or forceRare:
            img_placeholder=Image.open(f'logo/{str}_placeholder_rare.png')
            isRare=True
        else:
            img_placeholder=Image.open(f'logo/{str}_placeholder.png')
        img_placeholder=img_placeholder.convert("RGBA")
        
        rareType=""
        if open<close and (close*100/open)-100>=10 :
            rareType="Bull Rush"
        if birthDate!=None and (birthDate.month==dt.month and birthDate.day==dt.day):
            rareType="Birthday"
        if dt.month==1 and dt.day==1:
            rareType="Christmas"
        if dt in rareDays or forceRare:
            rareType="Halving"
        
        
        
        #img_cur.paste(logo,(0,0),logo)
        #img_cur=Image.alpha_composite(logo, img_cur)
        
        #new_image.paste(logo,(img_cur_size[0],0))
        #new_image.save("images/merged_image.jpg","JPEG")
        #new_image.show()
        
        
        final = trans_paste(img_placeholder,img_cur,1,(1,0))
        final.save(image_name)
        create_metadata(str,dt.strftime("%Y-%m-%d"),str,image_name,"",open,high,low,close,rareType,True)
        #time.sleep(0.5)
        warning(f" coin:{str} year:{dt.year} month:{dt.month} day:{dt.day}")
        dt=dt+timedelta(days=1)
        
        
def trans_paste(fg_img,bg_img,alpha=1.0,box=(0,0)):
    fg_img_trans = Image.new("RGBA",fg_img.size)
    fg_img_trans = Image.blend(fg_img_trans,fg_img,alpha)
    bg_img.paste(fg_img_trans,box,fg_img_trans)
    return bg_img

ASSET_TO_NAME_MAPPING={"BTC":"Bitcoin","ETH":"Ethereum","BNB":"Binance","DOGE":"Doge","SHIB":"ShibaInu","LINK":"ChainLink"}
ASSET_TO_BGCOLOR={"BTC":"#f08e3b","ETH":"#434871","BNB":"#282828","DOGE":"#c4942d","SHIBA":"#f5423f","LINK":"#3068d3"}
DESCRIPTION="Decentralized community to memorize crypto currency moments.feel free to surf our community DAPP at https://memorizethisday.io .Customize this NFT at https://memorizethisday.io/CalendarHall/###COLLECTIONNAME###/###DATE###"
EXTERNAL_URL_BASE="https://memorizethisday.io"
def create_metadata(asset,name,description,image,background_color,openPrice,highPrice,lowPrice,closePrice,rareType,getImageFromLastBuild):
    dt = datetime.datetime.strptime(name, '%Y-%m-%d')
    metadata_timestamp=str(int(dt.replace(tzinfo=timezone.utc).timestamp()))
    metadata_file_name=str(hex(int(dt.replace(tzinfo=timezone.utc).timestamp()))).replace("x","").zfill(64)+".json"
    metadata_filename=f"./MetaData/{asset}/{metadata_file_name}"
    metadata = copy.deepcopy(metadata_template)
    imageAddress=""
    if getImageFromLastBuild:
        if Path(metadata_filename).exists():
            jsonData=json.load(open(metadata_filename)) 
            imageAddress=jsonData["image"]
    
    if Path(metadata_filename).exists():
        jsonObj=json.load(open(metadata_filename))
        cid=jsonObj["image"].replace("https://ipfs.io/ipfs/","").split("?")[0]
        if not getImageFromLastBuild:
            unpin(cid)
        os.remove(metadata_filename)    
    
    #image=image.lower().replace("_","-")
    metadata["name"]=f"{ASSET_TO_NAME_MAPPING[asset]} price at {name}"
    metadata["description"]=DESCRIPTION.replace("###COLLECTIONNAME###",ASSET_TO_NAME_MAPPING[asset]).replace("###DATE###",name)
    metadata["image"]=upload_to_pinata(image) if imageAddress=="" else imageAddress
    metadata["external_link"]=EXTERNAL_URL_BASE
    metadata["background_color"]=""
    
    metadata["attributes"][1]['value']=name 
    metadata["attributes"][2]['value']=rareType if rareType!="" else "No" 
    
    metadata["attributes"][3]['value']="Doge" if openPrice==closePrice else "" 
    metadata["attributes"][3]['value']="Bull" if openPrice < closePrice else "Bear" 
    
    if openPrice < closePrice :
        metadata["attributes"][4]['value']= round((closePrice*100/openPrice)-100,2)
    elif openPrice > closePrice :
        metadata["attributes"][4]['value']= round((openPrice*100/closePrice)-100,2)
    else :
        metadata["attributes"][4]['value']=0
    
    metadata["attributes"][5]['value']=openPrice
    metadata["attributes"][6]['value']=highPrice
    metadata["attributes"][7]['value']=lowPrice
    metadata["attributes"][8]['value']=closePrice
    metadata["attributes"][9]['value']=metadata_timestamp
    
    if rareType=="":
        del metadata["attributes"][2]
    
    
    with open(metadata_filename,"w") as file:
        json.dump(metadata,file)
    
    #upload_to_ipfs(metadata_filename)



def upload_to_ipfs(filepath):
    if UPLOAD_IPFS == True:
        with Path(filepath).open("rb") as fp:
            image_binary = fp.read() 
            ipfs_url="http://127.0.0.1:5001"
            endpoint="/api/v0/add"
            response = requests.post(ipfs_url + endpoint,files={"file":image_binary})
            ipfs_hash = response.json()["Hash"]
            filename = filepath.split("/")[-1:][0]
            image_uri = f"https://ipfs.io/ipfs/{ipfs_hash}?filename={filename}"
            return image_uri
    else:
        return ""
    
    
    

PINATA_BASE_URL="https://api.pinata.cloud/"
PINATA_ENDPOINT="pinning/pinFileToIPFS"
PINATA_HEADERS={"pinata_api_key":"","pinata_secret_api_key":""}
def upload_to_pinata(filepath):
    if UPLOAD_IPFS == True:
        filename = filepath.split("/")[-1:][0]
        with Path(filepath).open("rb") as fp:
            image_binary = fp.read()
            response=requests.post(PINATA_BASE_URL+PINATA_ENDPOINT,files={"file":(filename,image_binary)},headers=PINATA_HEADERS)
            print(response.json())
            ipfs_hash = response.json()["IpfsHash"]
            filename = filepath.split("/")[-1:][0]
            image_uri = f"https://ipfs.io/ipfs/{ipfs_hash}?filename={filename}"
            time.sleep(0.5)
            return image_uri
    else:
        return ""

def get_last_image_date(path):
    list_of_files = glob.glob(path+"*") # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime).split("-")
    str_date=latest_file[1]+"-"+latest_file[2]+"-"+latest_file[3]
    str_date=str_date.replace(".png","")
    return (datetime.datetime.strptime(str_date,"%Y-%m-%d")+timedelta(days=1))


def update_asset():
    update("BTC")
    update("ETH")
    update("BNB")
    update("DOGE")
    update("SHIB")
    update("LINK")

def generate_some():
    dt = datetime.datetime(2015, 1,5, 0, 0,0)
    endDate= datetime.datetime(2015,1,10,0,0,0)
    rareDays=[]
    rareDays.append(datetime.datetime(2016, 7,9, 0, 0,0))
    rareDays.append(datetime.datetime(2020, 5,11, 0, 0,0))
    #bitcoin birthdate
    
    btcBirthDate= datetime.datetime(2009,1,3,0,0,0)
    generate("BTC",dt,endDate,rareDays,'rgba(247,147,26,0.4)',2,btcBirthDate)

def generate_all():
    dt = datetime.datetime(2015, 1,5, 0, 0,0)
    endDate= datetime.datetime(2022,4,22,0,0,0)
    #endDate= datetime.datetime(2015,1,7,0,0,0)
    
    #dt = datetime.datetime(2016, 12,26, 0, 0,0)
    rareDays=[]
    rareDays.append(datetime.datetime(2016, 7,9, 0, 0,0))
    rareDays.append(datetime.datetime(2020, 5,11, 0, 0,0))
    #bitcoin birthdate
    
    btcBirthDate= datetime.datetime(2009,1,3,0,0,0)
    generate("BTC",dt,endDate,rareDays,'rgba(247,147,26,0.4)',2,btcBirthDate)
    
    rareDays=[]
    dt = datetime.datetime(2017, 11,13, 0, 0,0)
    dogeBirthDate= datetime.datetime(2013,12,6,0,0,0)
    generate("DOGE",dt,endDate,rareDays,'rgba(249,195,37,0.4)',4,dogeBirthDate)
    
    rareDays=[]
    dt = datetime.datetime(2017, 11,13, 0, 0,0)
    ethBirthDate= datetime.datetime(2015,7,30,0,0,0)
    generate("ETH",dt,endDate,rareDays,'rgba(54,57,119,0.4)',2,ethBirthDate)
    
    rareDays=[]
    dt = datetime.datetime(2017, 11,13, 0, 0,0)
    linkBirthDate= datetime.datetime(2015,7,30,0,0,0)
    generate("LINK",dt,endDate,rareDays,'rgba(56,100,203,0.4)',2)
    
    rareDays=[]
    dt = datetime.datetime(2017, 11,13, 0, 0,0)
    generate("BNB",dt,endDate,rareDays,'rgba(50,50,50,0.4)',2)
    
    rareDays=[]
    dt = datetime.datetime(2020, 8,5, 0, 0,0)
    generate("SHIB",dt,endDate,rareDays,'rgba(235,62,52,0.4)',9)
    
    
def generate_diff():
    from_date=get_last_image_date('./images/BTC/').replace(tzinfo=timezone.utc)
    to_date = datetime.datetime.strptime(date.today().strftime("%Y-%m-%d"),"%Y-%m-%d").replace(tzinfo=timezone.utc)
    generate("BTC",from_date,to_date,[],'rgba(247,147,26,0.4)',2)
    
    from_date=get_last_image_date('./images/DOGE/').replace(tzinfo=timezone.utc)
    generate("DOGE",from_date,to_date,[],'rgba(249,195,37,0.4)',4)
    
    from_date=get_last_image_date('./images/ETH/').replace(tzinfo=timezone.utc)
    generate("ETH",from_date,to_date,[],'rgba(54,57,119,0.4)',2)
    
    from_date=get_last_image_date('./images/LINK/').replace(tzinfo=timezone.utc)
    generate("LINK",from_date,to_date,[],'rgba(56,100,203,0.4)',2)
    
    from_date=get_last_image_date('./images/BNB/').replace(tzinfo=timezone.utc)
    generate("BNB",from_date,to_date,[],'rgba(50,50,50,0.4)',2)
    
    from_date=get_last_image_date('./images/SHIB/').replace(tzinfo=timezone.utc)
    generate("SHIB",from_date,to_date,[],'rgba(235,62,52,0.4)',9)


def generate_n_last(n):
    from_date=datetime.datetime.strptime((date.today()+timedelta(days=-1*n)).strftime("%Y-%m-%d"),"%Y-%m-%d").replace(tzinfo=timezone.utc)
    to_date = datetime.datetime.strptime((date.today()+timedelta(days=-1)).strftime("%Y-%m-%d"),"%Y-%m-%d").replace(tzinfo=timezone.utc)
    generate("BTC",from_date,to_date,[],'rgba(247,147,26,0.4)',2)
    generate("DOGE",from_date,to_date,[],'rgba(249,195,37,0.4)',4)
    generate("ETH",from_date,to_date,[],'rgba(54,57,119,0.4)',2)
    generate("LINK",from_date,to_date,[],'rgba(56,100,203,0.4)',2)
    generate("BNB",from_date,to_date,[],'rgba(50,50,50,0.4)',2)
    generate("SHIB",from_date,to_date,[],'rgba(235,62,52,0.4)',9)

if __name__ == "__main__":
    #update_asset()
    #generate_n_last(10)
    generate_all()
    #generate_some()