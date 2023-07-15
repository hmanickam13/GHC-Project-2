# Web-Pricer
Integrating QuantLib with Google Sheets using xlwings API for Option Pricing and Greeks Calculation

## Google Cloud VM (Debian 10)
1. Create instance on GCloud. 
- Debian 10
- Instructions here: https://cloud.google.com/compute/docs/instances/create-start-instance

2. Use GCloud CLI to SSH into your VM instance
```sh
gcloud compute ssh <instance-name> --zone=<zone>
```

3. Install python, pip and git:
```sh
sudo apt-get update
sudo apt-get install python3-pip python3-venv git
```

### Using a Python Virtual Environment

4. Clone the project repo
```sh
git clone https://github.com/hmanickam13/GHC-Project-2.git
```

5. Create virtual environment & activate it
```sh
python3 -m venv venv
source venv/bin/activate
```

6. Install dependencies
```sh
pip install -r requirements.txt
``` 

Now you are good to go!
We can start the FastAPI application

7. Navigate to app directory & launch app
```sh
uvicorn main:app --host 0.0.0.0 --port 80
```
```

### Using Docker
4. Install docker
Install necessary packages to allow apt to use a repository over HTTPS:
```sh
sudo apt install apt-transport-https ca-certificates curl software-properties-common
```

Add the Docker GPG key:
```sh
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
```

Add the Docker repository to the system:
```sh
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

Update the package lists again:
```sh
sudo apt update
```

Install docker
```sh
sudo apt install docker-ce docker-ce-cli containerd.io
```

Start and enable the Docker service:
```sh
sudo systemctl start docker
sudo systemctl enable docker
```

Verify that Docker is installed and running by running a simple container:
```sh
sudo docker run hello-world
```

5. Clone the project repo
```sh
git clone https://github.com/hmanickam13/GHC-Project-2.git
```

Now you are good to go!
We can start the flask application



## Google Sheets
Hyperlink: https://docs.google.com/spreadsheets/d/1m9DkYm1JcmWz36gk4nxD2cYi_G0-DFs4PEEdMI1TDs4/edit?usp=sharing
<br>
Next, we need to paste the output of the following command into AppsScript on Google Sheets xlwings.js.
```sh
cp /usr/local/python/3.10.4/lib/python3.10/site-packages/xlwings/js/xlwings.js .
```
Alternatively, the output of the above command is in the googlesheets directory.
<br>
You can now add function calls inside your main.gs on AppsScript on Google Sheets