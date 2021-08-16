

import email
import getpass, imaplib
import os
import base64
import imaplib
import json
from optparse import OptionParser
import smtplib
import sys
import urllib.request, urllib.parse, urllib.error


### Refresh token 

client_id = "664990419712-gpdfa298nnk95b8mivog32hafda7g79v.apps.googleusercontent.com"
client_secret = "Yyj0Y6Un3lHO12XexQsl2K7c"
refresh_token = "1//0fFmVyw38nEPwCgYIARAAGA8SNwF-L9Ira2avV-YArwyp7ccs79FFg2lxUhBrOyMHpXL74y0M5BOCP1eD27asw0K2PZKlswcVRMM"
access_token = "ya29.a0ARrdaM-Drd3MGm_mGaoIvWVJ8schzqkb56RsC_5_6rB6OO_6Yb6tpRDp0L3C9hBjuoucSG_eYgnOK1VpPUeNbUng8Fch_hAmUWAlvkrc1CN-KLP7pOl_KvzHRfyrfQ1velzRPesEAChFiNgm0ldrNmcvYpKd"


# The URL root for accessing Google Accounts.
GOOGLE_ACCOUNTS_BASE_URL = 'https://accounts.google.com'


# Hardcoded dummy redirect URI for non-web apps.
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'


def AccountsUrl(command):
  """Generates the Google Accounts URL.

  Args:
    command: The command to execute.

  Returns:
    A URL for the given command.
  """
  return '%s/%s' % (GOOGLE_ACCOUNTS_BASE_URL, command)



params = {}
params['client_id'] = client_id
params['client_secret'] = client_secret
params['refresh_token'] = refresh_token
params['grant_type'] = 'refresh_token'
request_url = AccountsUrl('o/oauth2/token')

response = urllib.request.urlopen(request_url, urllib.parse.urlencode(params).encode("utf-8")).read()
resp = json.loads(response)



class Downloader:
        
    def __init__ (self):
        
        self.user = "resultados@omedic.com.mx"
        self.access_token = resp['access_token']
        self.GenerateOAuth2String( base64_encode=False)
        
        self.detach_dir = '.'
        if 'adjuntos' not in os.listdir(self.detach_dir):
            os.mkdir('adjuntos')
        else:
                        
            for parent, dirnames, filenames in os.walk(os.path.abspath( os.getcwd()) + '/adjuntos'):
                for fn in filenames:
                    if fn.lower().endswith('.pdf'):
                        os.remove(os.path.join(parent, fn))
        self.m = imaplib.IMAP4_SSL('imap.gmail.com')
        self.m.debug = 4
        self.m.authenticate('XOAUTH2', lambda x: self.auth_string)

    
    def GenerateOAuth2String(self, base64_encode=True):
        """Generates an IMAP OAuth2 authentication string.
          
        See https://developers.google.com/google-apps/gmail/oauth2_overview
          
        Args:
          username: the username (email address) of the account to authenticate
          access_token: An OAuth2 access token.
          base64_encode: Whether to base64-encode the output.
              
            Returns:
              The SASL argument for the OAuth2 mechanism.
            """
        self.auth_string = 'user=%s\1auth=Bearer %s\1\1' % (self.user, self.access_token)
        if base64_encode:
            self.auth_string = base64.b64encode(self.auth_string)
        
    def getAttach (self):
        self.m.select(readonly=False)
        eliNumb = ['1', '14', '13', '02', '01', '06', '08', '05', '04', '03', '012', '06']
        domain = ['resultadoseli' , 'gmail']
        for d in domain:
            for en in eliNumb:
                res, data = self.m.search(None,'UNSEEN', 'FROM', '"resultados.eli' + en + '@' + d + '.com"')
                if res == "OK":
                        # Iterating over all emails
                    for msgId in data[0].split():
                        typ, messageParts = self.m.fetch(msgId, '(RFC822)')
                        if typ != 'OK':
                            print ('Error fetching mail.')
                            raise
                
                        emailBody = messageParts[0][1]
                        mail = email.message_from_bytes(emailBody)
                        for part in mail.walk():
                            if part.get_content_maintype() == 'multipart':
                                # print part.as_string()
                                continue
                            if part.get('Content-Disposition') is None:
                                # print part.as_string()
                                continue
                            fileName = part.get_filename()
                
                            if bool(fileName):
                                filePath = os.path.join(self.detach_dir, 'adjuntos', fileName)
                                if not os.path.isfile(filePath) :
                                    print (fileName)
                                    fp = open(filePath, 'wb')
                                    fp.write(part.get_payload(decode=True))
                                    fp.close()
        self.m.close()
        self.m.logout()
    
                


