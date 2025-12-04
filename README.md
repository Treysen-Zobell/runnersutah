# Runners Inventory System

This application is a web-based platform for managing company inventory, build using Django and served via Gunicorn and Nginx.

## Table of Contents
1. [Workflow](#workflow)
2. [Setup Instructions](#setup-instructions)
3. [Tech Stack](#tech-stack)
4. [Development Reference](#development-reference)

---
## Workflow

### 1. Creating Product Templates
Product templates are the first step to creating any type of product. Each template essentially boils down to a list of
either optional or required pieces of information for a product of a certain type. Take for example, line pipe.
Different pipes have different specific information, but they are all classified by things like their outside diameter,
weight per foot, couplings, etc. If we wanted to add these pipes to our inventory system we would make a template, 
probably labeled "Line Pipe", and give all those fields. Specifically, we would give it the correct type of field for
what is being stored so automated functions like sorting still work. Currently, the supported fields are:

- Text - Stores text describing a product, such as a person's name.
- Integer - Stores a number without a decimal, for things that only come in whole numbers.
- Decimal - Stores a number with a decimal, for things that require additional precision.
- Choices - Stores a list of options, of which one can be selected for a product.
- Measure - Stores a measurement, either metric or imperial.
- Static - Doesn't take any input, mostly used for adding labels within tables.

### 2. Creating Products
After we have the appropriate template for a product category, we can fill it with specific products. Using the example
of line pipe again, we can make a product with an outside diameter of 6 5/8", a weight per foot of 19.19, and a
coupling of type ERW. We also need to assign the product to some customers so that they can hold a stock of it.

---
## Setup Instructions

---
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

---
## Development Reference

```sh
  poetry run python src/manage.py makemigrations
```
```sh
  poetry run python src/manage.py migrate --run-syncdb
```
```sh
  poetry run python src/manage.py runserver
```

### Todo:
 - Make product "deactivate-able" for a customer so it can be hidden from view.