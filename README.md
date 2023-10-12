# URL Shortening APP

This is a URL shortening web app. This service allows users to shorten long
URLs into shorter, unique URLs. When users access the shortened URL, they will be redirected to the original long URL.

## Installation


```bash
# get code
git clone https://github.com/nesar97/GMR.git
cd GMR
# Create python virtual environment
python -m venv ../GMRenv
# activate venv
source ../GMRenv/bin/activate
# Install required packages in venv
pip install -r requirements.txt
```

## Usage

Start the server 
```bash
python main.py
```

Visit http://127.0.0.1:8080/

### Front End

Home page 
```http://127.0.0.1:8080/```

Error  ```http://127.0.0.1:8080/error.html```

### REST API

For accessing REST APIs visit following url

**/shorten** -      Endpoint to shorten a URL .    
**/<short_url>** -  Endpoint to redirect to the original URL.  
**/list** -         Endpoint to list all URLs.