import urllib.request
from datetime import timedelta, timezone, datetime, date, time
import csv
import os

def update(asset):
    file_name=f"{asset}-USD.csv"
    #from_date_timestamp = str(int(.replace(tzinfo=timezone.utc).timestamp()))
    #.strftime("%Y-%m-%d")
    from_date_timestamp=str(int(get_last_saved_date("./DataSource/"+file_name).replace(tzinfo=timezone.utc).timestamp()))
    to_date_timestamp = str(int(datetime.strptime((date.today()+timedelta(days=-1)).strftime("%Y-%m-%d"),"%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp()))
    
    if not from_date_timestamp==to_date_timestamp:
        urllib.request.urlretrieve(f"https://query1.finance.yahoo.com/v7/finance/download/{asset}-USD?period1={from_date_timestamp}&period2={to_date_timestamp}&interval=1d&events=history&includeAdjustedClose=true", f"{file_name}")
        data_file = open(file_name)
        csvreader = csv.reader(data_file)
        header = next(csvreader)
        for row in csvreader:
            new_row_data=row[0]+","+ row[1]+","+ row[2]+","+ row[3]+","+ row[4]+","+ row[5]+","+ row[6]
            with open("./DataSource/"+file_name, 'a') as f:
                f.write("\n")
                f.write(new_row_data)
                print(new_row_data)
                
        os.remove(file_name)



def get_last_saved_date(file_name):
    with open(file_name, "r", encoding="utf-8", errors="ignore") as scraped:
        final_line = scraped.readlines()[-1]
        return datetime.strptime(final_line.split(",")[0], '%Y-%m-%d')+timedelta(days=1)
        

if __name__ == "__main__":
    update("BTC")
    update("ETH")
    update("BNB")
    update("DOGE")
    update("SHIB")
    update("LINK")
    pass