# nJoy
**With nJoy its all about enjoying the movies and or series you watch.**
## Disclaimer
**Running this application is not easy at the moment - Its open source so GFIY**
## Running the application (from Source /w Docker & Docker-Compse)
**This is how I would run it without an CI/CD integration and before I have worked on the setup wizard.**

**Clone the repository to your host**
```bash
git clone https://github.com/njoy/njoy-backend.git
# change directory
cd njoy-backend
```
**Create Volumes**
```bash
mkdir -p /opt/njoy-backend/data/videos
mkdir /opt/njoy-backend/data/thumbnails
mkdir /opt/njoy-backend/config
mkdir /opt/njoy-backend/keys
mkdir /opt/njoy-backend/logs
```
**Create Key-Pair**
```bash
mv backend-shared/security/.keys/temp.py
python3 temp.py
mv temp.py /backend-shared/security.keys/temp.py
```
**Move keys to volume**
```bash
mv *.pem /opt/njoy-backend/keys
```
**Copy config to volume**
```bash
mv config/example.config.json /opt/njoy-backend/config/config.json
# open config to edit
nano config.json
```
**Edit config to your needs**
```json
{
    ...
    "database":{
        "hostname":"your.hostname.com",
        ...
        "admin":{
            ...
            "password":"match with cicd/.env"
        }
        ...
    },
    ...
    "verwaltung":{
        "admin":{
            "username":"admin",
            "password":"verysecret",
            ...
        }
    },
    ...
}
```
**Build Docker-Image**
```bash
docker build -f dockerfile . -t njoy-backend
```
**Spin up container**
```bash
docker compose -p njoy-backend -f docker-compose.yaml up -d
```
### Behind the scenes
**There is some magic or logic working in the background**
- On launch the database gets created with all tables
- An admin-account gets created
**Username and password are defined in the config.json**
*If you change the config.json you need to restart the container*
```bash
docker restart njoy-backend
```
**API-Health-Check**
```bash
#copy and open address
http://localhost:6692/api/v1/healthz
#should return '200 OK'
```
## Next Steps
### 1 Connect the Frontend-Application
- **Follow this [Guide]([https://google.de](https://github.com/njoyporn/njoy-frontend)) to host the frontend**
### 2 Preparation for Production
- **DNS:**
    - Domain: yourdomain.com
    - Subdomain: api.yourdomain.com
    - *Optional:* acquire a certificate for TSL
- **Server**
    - **CPU-Cores:**    2
    - **RAM:**          4 GB
    - **HDD:**          20 GB
    - **SSD:**          120 GB (depending on your file size)
##### Webserver
- #### *Apache2*
- #### *Gunicorn*
### **INFO:** You need to enable the headers module
```bash
a2enmod headers
```
```bash
#You need to set the access-header within apache even the flask app is wrapped within CORS-utility. 
#The gunicorn-wsgi is messing everything up. 
<IfModule mod_ssl.c>
<VirtualHost *:443>
    ServerName api.yourdomain.com
    ServerAlias api.yourdomain.com

    SSLProxyEngine On

    Header add Access-Control-Allow-Origin "*"
    Header add Access-Control-Allow-Methods "POST, GET, OPTIONS"
    Header add Access-Control-Allow-Headers "Content-Type, X-Requested-With, Origin, Authorization"

    ProxyPass / http://localhost:6692/
    ProxyPassReverse / http://localhos:6692/

    SSLEngine on
    ErrorLog ${APACHE_LOG_DIR}/error.log
    CustomLog ${APACHE_LOG_DIR}/access.log combined
    Include /etc/letsencrypt/options-ssl-apache.conf

    SSLCertificateFile /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/api.yourdomain.com/privkey.pem
</VirtualHost>
</IfModule>
```
After you configured everything correct you can check the settings
```bash
apachectl -t
```
If everythig is ok restart Apache2
```bash
service apache2 restart
```
Else you can start investigating your errors with:
```bash
systemctl restart apache2
```

## Known Issues
### Docker
I cant use multiple **.env-Files**. Maybe I don't get the [Documentation](https://docs.docker.com/compose/how-tos/environment-variables/set-environment-variables/#additional-information-1)
#### Work-Around
I use a .env-File and take care to not touch it. I am fine with using my Piplelines for it.
When you deploy the containers and don't use a pipeline to provide the ENV-Vars the .env-File has to be used instead 