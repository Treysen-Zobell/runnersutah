# Runners Utah Inventory Website

This application is a web-based platform for managing company inventory, build using Django and served via Gunicorn and Nginx.

## Table of Contents
1. [Setup Instructions](#setup-instructions)
2. [Tech Stack](#tech-stack)
3. [Development Reference](#development-reference)

## Setup Instructions

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

## Development Reference

```sh
  poetry run python src/manage.py makemigrations
```
```sh
  poetry run python src/manage.py migrate
```
```sh
  poetry run python src/manage.py runserver
```