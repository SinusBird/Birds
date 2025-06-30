import os
from ftplib import FTP_TLS

ftp_user = os.getenv("BIRD_FTP_USER")
ftp_pw = os.getenv("BIRD_FTP_PW")
ftp_host = os.getenv("BIRD_FTP_SERVER")
ftp_dir = "/public_html/bird-analytics/" ## funktioniert nicht

ftp = FTP_TLS(ftp_host)
ftp.login(ftp_user,ftp_pw)
ftp.prot_p()  # Aktiviert verschlüsselte Datenübertragung

print("Aktuelles Verzeichnis:", ftp.pwd())
print("Inhalt:", ftp.nlst())

# ftp.cwd(ftp_dir)
# files = ftp.nlst()
# print(files)

ftp.quit()