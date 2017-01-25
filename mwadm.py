#!/opt/anaconda3/bin/python
#
# Here's a plugin which lets you monitor your senderscore.org reputation. For
# people sending a large amount of email - this might be useful.
#
# Config env var used:
# [senderscore]
#  env.senderscore_check_ip xxx.yyy.zzz.ttt
#

import socket
import sys
import os
import getopt
import requests
from bs4 import BeautifulSoup

#import MySQLdb
import pymysql.cursors

def parse_input(fname):
    try:
        fhandle=open(fname)
    except:
        print ('ERROR: Specified file couldn\'t be opened')
        exit()
    iplist = []
    for ip in fhandle:
        iplist.append(ip.rstrip())
    return iplist

def process_all(iplist,verbose):
    for ip in iplist:
        sscore = get_stat(ip)
        dnsblList = check_blkmx(ip)
        if verbose: print ('{:16}'.format(ip),'|','{:4}'.format(sscore),'|',','.join(dnsblList))
        connection = pymysql.connect(host='192.168.1.175',
                             user='root',
                             password='Admin1234',
                             db='maildb',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
        try:
            with connection.cursor() as cursor:
                # Create a new record
                sql = "INSERT INTO `reputation` (`IP`, `Senderscore`, `DNSBL`) VALUES (%s, %s, %s)"
                cursor.execute(sql, (ip, sscore, ','.join(dnsblList)))

            # connection is not autocommit by default. So you must commit to save
            # your changes.
            connection.commit()

            with connection.cursor() as cursor:
                # Read a single record
                sql = "SELECT `IP`, `Senderscore`,`DNSBL`,`CheckedDate` FROM `reputation` order by CheckedDate Desc LIMIT 1"
                cursor.execute(sql)
                result = cursor.fetchone()
                if verbose: print(result)
        finally:
            connection.close()

    return


def get_senderscore(ip):
    tmp = ip.split(".")
    backwards = "%s.%s.%s.%s" % (tmp[3], tmp[2], tmp[1], tmp[0])
    #replists = ['cmplt.rating.senderscore.com', 'score.senderscore.com', 'uus.rating.senderscore.com', 'vol.rating.senderscore.com', 'filtered.rating.senderscore.com']
    rl = 'score.senderscore.com'
    lookup_results = {}
    scores = {}
    try:
        host = '%s.%s' % (backwards, rl)
        ret = socket.gethostbyname(host)
        if ret:
            lookup_results[rl] = ret
    except Exception:
        # NO SENDERSCORE AVAILABLE
        scores['score'] = 'X'
        return scores
    
    for k in lookup_results.keys():
        v = lookup_results[k].split('.')[3]
        k = k.split(".")[0]
        scores[k] = v
    return scores

def get_stat(ip):
    scores = get_senderscore(ip)
    for key in scores.keys():
        return scores[key]


def check_blkmx(ip):
    #Create a CookieJar object to hold the cookies
    INITURL = 'https://www.blk.mx/'
    client = requests.session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
    }
    #csrf = client.get(URL,headers=headers).cookies['_csrf']
    cookiesObj = client.get(INITURL,headers=headers).cookies

    API_URL = 'https://www.blk.mx/site/check-host?host=' + ip
    REFERER_URL = 'https://www.blk.mx/?host=' + ip

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'Pragma': 'no-cache',
        'Accept-Encoding': 'gzip, deflate, sdch, br',
        'X-Requested-With': 'XMLHttpRequest',
        'Connection': 'keep-alive',
        'Accept': '*/*',
        'Cache-Control': 'no-cache',
        'Accept-Language': 'en-US,en;q=0.8',
        'Referer': REFERER_URL
    }
    
    
    response = client.get(API_URL,headers=headers,cookies=cookiesObj)
    #print (response.status_code,response.headers,response.content)
    result = []
    soup = BeautifulSoup(response.content, 'html.parser')
    if soup.find_all('tr'):
         #print (soup.find_all('tr')[1:])
        for tr in soup.find_all('tr')[1:]:
            result.append(tr.contents[1].contents[0])           
            #print ('DNSBL :',tr.contents[1].contents[0],'| Status :',tr.contents[3].contents[0])
            return result
    else:
       return result

#TBD def print_chart(result):

def main(argv):
   try:
      opts, args = getopt.getopt(argv,"hi:c:v",["help","inputfile="])
   except getopt.GetoptError as err:
      print (err)
      print ('mwadm.py -i <inputfile> [-v]')
      sys.exit(2)
   inputfile = None
   verbose = False
   for opt, arg in opts:
      if opt == "-v":
          verbose = True
      elif opt in ('-h','--help'):
         print ('mwadm.py -i <inputfile> [-v]')
         sys.exit()
      elif opt in ("-i", "--ifile"):
         inputfile = arg
      else:
         assert False, "unhandled option"
   iplist = parse_input(inputfile)
   process_all(iplist,verbose)

if __name__ == "__main__":
   main(sys.argv[1:])
