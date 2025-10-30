# Runners Inventory Management System

This application is a web-based platform for managing company inventory, build using Django and served via Gunicorn and
Nginx.

## Setup Instructions

### Prerequisites:

- A device accessible from a public IP. This could be a VPS that offers a public IP or a local device with port
forwarding on ports 80 and 443 setup on the router.
- A public domain that you control the DNS records for.

### 1. Update Domain DNS Record

The specific process for updating records varies by your domain provider, but all follow the same basic procedure.

1. Get the server's public IP.
2. Set the DNS record for your desired URL to the public IP. For example, if you want https://inventory.example.com to
link to this project set the entry name *inventory* to the IP under the domain example.com.

### 2. Start and Configure Nginx Proxy Manager

1. Start the service using `docker compose up nginx`
2. Login using the default login, admin@example.com : changeme
3. You will be prompted to create your own user, do so
4. Create a new proxy host with the following settings
    - Details > Domain Names: example.com
    - Details > Scheme: https
    - Details > Forward Hostname / IP: backend
    - Details > Forward Port: 8000
    - Advanced > Custom Nginx Configuration: 
   ```
   location /static/ {
       alias /mnt/staticfiles/;
   }
   location /media/ {
      alias /mnt/media/;
   }
   ```
    - SSL > SSL Certificate > Request a new SSL Certificate
    - Save

### 3. Start Everything and Create a User

1. Start all the services using `docker compose up`
2. Connect a terminal to the backend container using `docker exec -it runners-backend sh`
3. Create a superuser using the command `poetry run python manage.py createsuperuser`
4. You will be prompted to enter a username and a password, do so.

### 4. Test Your User

1. Go to the sites admin section using the url https://example.com/admin/
2. Log in using the credentials you provided for the user

### Complete
The site should be running, and you should now have a user. Ideally this process will be streamlined in the future
to skip attaching to the container. A landing page could probably be made to allow the user to create the first
user on the site itself. Whether this is feasible security wise is a question to be answered later.

## Tech Stack

| Layer              | Technology              |
|--------------------|-------------------------|
| Backend            | Django 5.2.7            |
| Frontend           | Django Templates + JS   |
| Database           | PostgreSQL              |
| Server             | Gunicorn                |
| Reverse Proxy      | Nginx                   |
| Dependency Manager | Poetry                  |
| Containerization   | Docker / Docker Compose |
