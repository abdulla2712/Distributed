# Cinema Management Program

Program is written in Python and integrated with Docker, Django and MySQL.

---

## Installation

Docker version used during development:
- [Docker Desktop 4.15.0](https://docs.docker.com/desktop/release-notes/#4150) with Docker Compose version v2.13.0
- Windows extra in case docker doesn't start:
  - Enable WSL by running powershell as administrator and enter
    ```
    dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
    ```
  - [Install WSL2 Linux kernel update package for x64 machines](https://wslstorestorage.blob.core.windows.net/wslblob/wsl_update_x64.msi)
  - Restart windows and start the docker

---

## Run
```sh
$ docker compose up
$ docker ps # check are the 2 containers running (db, app)
```

App should be available at:
- http://localhost:8000
- http://localhost:8000/admin

## Useful commands

```sh
$ docker compose build # build images
$ docker compose down && docker volume prune -f && docker system prune --volumes # stop containers and delete the data
$ docker system prune --all # remove all stopped containers and images
```

From within the container.
```sh
$ docker exec -it app bash
python manage.py
python manage.py makemigrations
python manage.py migrate
python manage.py loaddata initial.yaml
python manage.py dumpdata --format=yaml > ./dump_file.yaml
```

## Users

There are number of users, the only superuser added is:

```
username: admin
password: NnwNeE88
```


## Design

- Theaters can have multiple screens.
- Screen can have only 1 movie assigned.
- Screen type has been added to handle the ticket prices.
- Screen is occupied if movie is assigned within "starts_at" and "ends_at" date.
- Same movie can be added to different screens at the same time.
- There is one category per movie.
- When the movie is added to the screen, the tickets are generated behind the scenes without customer data, meaning they are not yet sold.
- When the movie is removed from the screen, the tickets are removed behind the scenes regardless of if they have been sold or assigned to the customer.
- Movie becomes inactive when current time passes "ends_at" date on save.
- Django User model has been extended with extra fields.
- Django Group model has been extended with an extra "is_active" field and 2 groups have been added to the initial data fixture. The first group is "Manager" which can handle any cinema related records, it should not be mistaken with superuser and all admin records like sessions. The second group added is "Cashier" which can only handle cinema ticket records.

## Future possibilities
- The "screen.is_occupied" and "movie.is_active" are handled on save which in real life would not be enough. As the time passes, every minute we would need to have a running background task which would update those values accordingly.
- It could be possible to assign the same movie multiple times to one screen during different times. e.g. Run the same movie from 18-20 and 20-22 hours.
- Movie could be added to multiple categories.
- Removing the movie from the screen should not delete the sold tickets or there should be an UI warning.
- Changing the number of seats for the screen should add or remove unsold tickets.
- Groups "is_active" doesn't have functionality at this point.
- Frontend speed optimization, minimization, etc..
- Tests.
