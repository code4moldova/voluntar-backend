# covid19md-voluntari-server


### Application Structure

```
├── backend
│   ├── app.py
│   ├── endpoints
│   │   └── __init__.py
│   └── static
│       └── swagger.yaml
├── docker-compose.yml
├── Dockerfile
├── Pipfile
├── Pipfile.lock
└── README.md
```

Installation
------------

### Using docker-compose

It is very easy to start exploring the example using Docker:

```bash
$ docker-compose up
```

Init database with some users
```
cd backend && flask init-db
```

You can login with default admin user. email: ureche@example.com, pass: 123456
