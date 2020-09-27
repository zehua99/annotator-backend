# Annotator Backend
The Socket backend for the multi-user article annotating tool. Find the frontend project [here](https://github.com/simonzli/article-annotator).

## Input Data
The input data should have the following structure:
```json
[{
  "id": 1,
  "category": "The category this article belongs to",
  "question": "Does the story adequately discuss the costs of the intervention?",
  "answer": 1,
  "explanation": "The story offers an estimate of the cost of an acupuncture session at $125...",
  "article": "The entire article",
  "paragraphs": ["paragraph_1", "paragraph_2"],
  "sentences": ["sentence_1", "sentence_2"]
}]
```
Change [lines 17 through 49](https://github.com/simonzli/annotator-backend/blob/master/server.py#L17-L49) to suit your dataset.

## Run the Server
1. Install Python 3
2. Run `pip install -r requirements.txt` under your project root directory.
3. Run `python server.py` to start the server.

## Nginx Configuration
Here is a sample Nginx server config for the project. Put it inside the `http` clause of your `nginx.conf`. Note that you should [generate SSL certificates](https://letsencrypt.org/getting-started/) for your domains if you want to enable HTTPS.

```nginx
upstream socket_nodes {
  ip_hash;
  server 127.0.0.1:5000;
}

server {
  server_name example.com;

  location ~* \.io {
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-NginX-Proxy false;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header Host $host;
    proxy_pass http://socket_nodes;

    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
  }

  listen [::]:443; # managed by Certbot
  ssl on;
  listen 443 ssl; # managed by Certbot
  ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem; # managed by Certbot
  ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem; # managed by Certbot
  include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
  ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
}
```
