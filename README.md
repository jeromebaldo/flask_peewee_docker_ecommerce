# flask_peewee_docker_ecommerce

## Contexte et objectifs de l'application 

### Le contexte
Ce laboratoire a consisté à développer et déployer une application Web responsable du paiement de commandes Internet. Il a été réalisé dans le cadre du cours "Technologies Web Avancées" donné par l'Université du Québec à Chicoutimi. 

### Les objectifs 
- Développer une API REST
- Utiliser des services Web distants
- S'assurer de la résilience et de la performance d'une application Web

## Point de situation
### Composition du repository
- api8inf349 contient la partie python permettant le front-end et le backend 
- config_infos comprend les logs divers ainsi que les dépendandes requises pour l'application 
- Le fichier Dockerfile permet de monter le conteneur du serveur/ client 
- le fichier docker-compose.yml permet de monter l'ensemble de l'application dont les datas , l'application et redis.
### conteneurs installés 
- reddis servant de cache pour les commandes déjà , localisé sur le localhost au port 6379
- db est composé d'une base de données postgresql, localisé sur le localhost au port 5432
- pgadmin permet la possibilité de réaliser des CRUD sur la base de données . Il est accessible sur le localhost au port 
- api8inf349 est compos du client et du serveur. Le client est affiché grâce à Jinja2. les 2 composantes sont élaborés avec python et flask.



## Installation et exécution de l'application

### Logiciels et dépendances requis 
- Installation et utilisation du logiciel Docker Deskstop
- Utilisation du terminal de commande avec la dépendance Docker CLI
### Exécution de l'application 

- Pour lancer l'application , il suffit de taper la commande "docker-compose up" pour monter et rouler le front-end et le backend.
- Les conteneurs devront apparaitre dans le logiciel Docker connecté avec votre session.
- Pour le serveur / client Flask "api8inf349" vous pouvez accèder à l'adresse suivante: http://localhost:5000/
- Pour PGAdmin ,vous pouvez accèder à l'adresse suivante : http://localhost:5050/

## Sources

- Documentation officielle de Jinja2 => https://jinja.palletsprojects.com/en/3.1.x/
- Documentation officielle de Peewee => http://docs.peewee-orm.com/en/latest/
- Documentation officielle de Flask => https://flask.palletsprojects.com/en/2.3.x/ et https://flask-fr.readthedocs.io/
- Pour la résolution de la contenarisation d'Angular => https://github.com/docker/awesome-compose/tree/master/angular
- 
## Changelog
### V1 => 
- version initiale
