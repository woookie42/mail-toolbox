#!/opt/anaconda3/bin/python

import socket
import requests

ses = requests.session()

url = 'https://accounts.google.com/InputValidator?resource=SignUp'
headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        'Content-type': 'application/json',
        'Origin': 'https://accounts.google.com',
        'Referer': 'https://accounts.google.com/SignUp'
        }
data = '{"input01":{"Input":"GmailAddress","GmailAddress":"erez@otb-algo.com","FirstName":"","LastName":""},"Locale":"en"}'

res = ses.post(url=url, data=data, headers=headers)
print (res.content)
