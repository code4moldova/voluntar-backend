# Voluntar.md

## Contributing

This project is built by amazing volunteers and you can be one of them! Here's a list of ways in [which you can contribute to this project](CONTRIBUTING.md).

If you want to make any change to this repository, please **make a fork first**.

If you see something that doesn't quite work the way you expect it to, open an Issue. Make sure to describe what you _expect to happen_ and _what is actually happening_ in detail.

If you would like to suggest new functionality, open an Issue and mark it as a __[Feature request]__. Please be specific about why you think this functionality will be of use. If you can, please include some visual description of what you would like the UI to look like, if you are suggesting new UI elements. 


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

[Class diagram](ClassDiagram.png)

## Built With

Flask

### Programming languages

Python 3

### Run & Development
#### Docker
Docker is used to run the development version, so you'll need to install [Docker](https://docs.docker.com/install/) and [docker-compose](https://docs.docker.com/compose/install/).

In case you are using WSL with Docker for Desktop (version 2.2.0.4) on Windows: you need to have your repository on the Windows file system rather than on the WSL one because otherwise the volume won't be mounted (solution inspired from this work around: https://github.com/docker/for-win/issues/2151#issuecomment-402163189)

* change the docker-compose.yml variables


```bash
$ docker-compose up
```

Init database with some users
```
cd backend && flask init-db
```

You can login with default admin user. email: ureche@example.com, pass: 123456

#### Pycharm
To run the application using Pycharm you need to install MongoDB Community Edition following steps from [documentation](https://docs.mongodb.com/manual/installation/).
Steps below work for all OS where Pycharm is available.
1. Install pycharm community edition
2. Open the project in pycharm
3. Open terminal from pycharm Alt+F12 or View -> Tool Windows -> Terminal
4. Install pipenv from terminal if it's not installed yet:
    ```
    $ pip install pipenv
    ```
5. Install dependencies from Pipfile
    ```
    $ pipenv install
    ```
6. Add new configuration for python:
Run -> Edit Configurations... -> + -> Python
7. Change option "Script Path" to "Module Name"
8. Enter "flask" in input for "Module Name"
9. Enter **run** in input "Parameters"
10. Open and add new Environment variables:
    - FLASK_APP=app.py
    - FLASK_DEBUG=1
    - SECRET_KEY=whatever 
    - DB_HOST=localhost:27017 (If you are using another port, change to your one)
10. Press Ok
11. To init databases execute command in terminal from Pycharm

## Feedback

* Request a new feature on GitHub.
* Vote for popular feature requests.
* File a bug in GitHub Issues.
* Email us with other feedback contact@code4.md

## License

This project is licensed under the MPL 2.0 License - see the [LICENSE](LICENSE) file for details

## About Code4MD

Started in 2020, Code for Moldova is a civic tech NGO. We have a community of over 100 volunteers (developers, ux/ui, communications, data scientists, graphic designers, devops, it security and more) who work pro-bono for developing digital solutions to solve social problems. #techforsocialgood. If you want to learn more details about our projects [visit our site](https://www.code4.md/) or if you want to talk to one of our staff members, please e-mail us at contact@code4.md.

Last, but not least, we rely on donations to ensure the infrastructure, logistics and management of our community that is widely spread across 11 timezones, coding for social change to make Moldova and the world a better place. If you want to support us, [you can do it here](https://code4.md/).
