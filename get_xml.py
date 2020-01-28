import os
from ftplib import FTP

ftp = FTP('electionsonline.ap.org')
ftp.login(os.environ['FTP_UNAME'], os.environ['FTP_PWORD'])
ftp.cwd('/Delegate_Tracking/Reports/')

for file_name in ['delstate.xml', 'delsum.xml', 'delsuper.xml']:
    local_file = open(os.path.join('xml', file_name), 'wb')
    ftp.retrbinary('RETR ' + file_name, local_file.write, 1024)
    local_file.close()

ftp.quit()
