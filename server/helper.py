# -*- coding: utf-8 -*-
## help function들을 모은 집합입니다
import subprocess
import pandas as pd
import sys
from db_connect import conn, engine
from sentiment.src.sentiment_analysis import SentimentAnalysis

from src import keyword
def exist_test(table):
    cur = conn.cursor()
    query = f"SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' and table_name={table}"
    cur.execute(query)
    result = cur.fetchone()
    if(result == None):
        return 0
    elif(result[0] == 1):
        return 1
    else:
        return 0

def extract_save_reply(youtube_url):
    youtube_key = youtube_url.split("?v=")[-1]
    youtube_key = youtube_key.split("&")[0]
    youtube_key = youtube_key.lower()
    __cmd = f"./run_crawler.sh {youtube_url} {youtube_key}"
    print(__cmd)
    try:
        subprocess.call(__cmd, shell=True)
        #        subprocess.call(f"mv {youtube_key}.json json/", shell=True)
        return 1
    except Exception as e:
        print(e)
        return 0


def make_table(youtube_url):
    youtube_key = youtube_url.split("?v=")[-1]
    youtube_key = youtube_key.split("&")[0]
    youtube_key = youtube_key.lower()
    reply_df = pd.read_json(f"json/{youtube_key}.json")
    reply_df.to_sql(youtube_key, engine, if_exists='replace')
    # insert data

def get_table_data(youtube_url, func_name):
    youtube_key = youtube_url.split("?v=")[-1]
    youtube_key = youtube_key.split("&")[0]
    table = youtube_key.lower()
    sentiment_class = SentimentAnalysis("sentiment/model/word2vec/word2vec.model","sentiment/model/slang/slang_dict.txt")
    if(func_name == "sentiment"):
        cur = conn.cursor()
        query = f'SELECT root,index FROM "{table}"'
        cur.execute(query)
        results = cur.fetchall()
        result = [row[0] for row in results]
        index = [row[1] for row in results]
        temp = sentiment_class.score(index, result)
        print(temp)
        query = f'alter table "{table}" add column sentiment varchar'
        cur.execute(query)
        conn.commit()
        for index,row in temp.iterrows():
            sql = f'update "{table}" set sentiment=\'{row["sentiment"]}\' where index={row["index"]}'
            cur.execute(sql)
            conn.commit()
        sql=f"update history set done=2 where url='{youtube_url}'"
        cur.execute(sql)
        conn.commit()
    elif(func_name == "slang"):
        cur = conn.cursor()
        query = f'SELECT root,index FROM "{table}"'
        cur.execute(query)
        results = cur.fetchall()
        result = [row[0] for row in results]
        index = [row[1] for row in results]
        temp = sentiment_class.slang(index, result)
        print(temp)
        query = f'alter table "{table}" add column slang varchar'
        cur.execute(query)
        conn.commit()
        for index,row in temp.iterrows():
            sql = f'update "{table}" set slang=\'{row["slang"]}\' where index={row["index"]}'
            cur.execute(sql)
            conn.commit()
        sql=f"update history set done=2 where url='{youtube_url}'"
        cur.execute(sql)
        conn.commit()
    elif(func_name == "keyword"):
        cur = conn.cursor()
        query = f"SELECT root FROM {table}"
        cur.execute(query)
        result = cur.fetchall()
        result = [row[0] for row in result]
        temp = get_cnt_words(result)
        print(temp)


if __name__ == "__main__":
    if (len(sys.argv) < 3):
        print("input function argument")
        exit
    if (len(sys.argv) ==3):
        func_name = sys.argv[1]
        youtube_url = sys.argv[2]
        globals()[func_name](youtube_url)
    elif(len(sys.argv)>3):
        func_name = sys.argv[1]
        table_name = sys.argv[2]
        func_name2 = sys.argv[3]
        globals()[func_name](table_name,func_name2)
    # func_name(youtube_url)






