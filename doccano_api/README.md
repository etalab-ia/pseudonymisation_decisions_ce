
## Doccano

Pour lancer Doccano deux options:

-   (Par défaut) Docker Compose
-   Docker

### Docker Compose

```bash
$ git clone https://github.com/doccano/doccano.git
$ cd doccano
$ docker-compose -f docker-compose.prod.yml up
```

Aller à  <http://0.0.0.0/>.

_Les crédentials de super utilisateurs sont configurées dans le fichier `docker-compose.prod.yml`:_
```yml
ADMIN_USERNAME: "admin"
ADMIN_PASSWORD: "password"
```

### Docker

La première fois, création du Docker Doccano:

```bash
docker pull doccano/doccano
docker container create --name doccano \
  -e "ADMIN_USERNAME=admin" \
  -e "ADMIN_EMAIL=admin@example.com" \
  -e "ADMIN_PASSWORD=password" \
  -p 8000:8000 doccano/doccano
```

Puis, pour lancer le container:

```bash
docker container start doccano
```

Pour arrêter le container `docker container stop doccano -t 5`.
Les données persisteront entre les sessions.

Aller à  <http://127.0.0.1:8000/>.

## API
Pour utiliser l'API, initialiser un client :


```python
from doccano_api import doccano_routines
client = doccano_routines.instantiate_client(url='http://0.0.0.0/', user='admin', password='password') 
```

Puis utiliser le client pour les différentes routines, par exemple, pour envoyer un fichier dans un projet:

```python
from doccano_api import doccano_routines

project_id = 1
file_path = "path to file"
tags = ["PERSONNE", "LOCATION"]

client = doccano_routines.instantiate_client(url='http://0.0.0.0/', user='admin', password='password') 

doccano_routines.upload_file(client, project_id, file_path)
doccano_routines.clean_labels(client, project_id, tags)

 
```


