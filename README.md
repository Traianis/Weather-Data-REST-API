# Weather-Data-REST-API

De a se rula scriptul de testare cu un Postman descarcat local!

Pentru rularea dockerului se va folosii comanda:

sudo docker compose up --build
(de verificat daca porturile servicilor sunt ocupate)

In docker-compose am 2 networkuri(unul pentru utilitarul bazei de date si 
celalalt pentru serverul de API) si 3 servicii: 

1. PostgreSQL (baza de date):
    - username si parola pentru conectare: admin, admin
    - port: 5432
    - datele sunt persistente prin volumul postgres_data

2. PgAdmin (utilitarul bazei de date):
    - username si parola pentru conectare : admin@test.com, admin
    - port: 8080
    - depinde de pornirea serviciului postgres

3. Serverul API:
    - foloseste un Dockerfile pentru a pornii serverul de Flask
    - depinde de pornirea serviciului postgres
    - port: 6000


Serverul pentru API:

Dockerfileul va crea o imagine care copiaza requirements si scriptul in directorul de rulare si ruleaza api.py

api.py: Desi in docker compose containerul pentru serviciul apiului va astepta sa se porneasca cel al bazei de date.
S ar putea ca serverul bazei de date sa nu si termine initializarea inca, asa ca am introdus 5 reincercari in script
(cu sleeptime intre ele). Dupa conectare verifica daca exista baza de date si o creeaza (+ tabelele) in caz contrar.
Apoi am pornit serverul Flask.

Pentru a face conexiunea dintre baza de date si serverul Flask am folosit sqlalchemy.
Am facut clase care reprezinta tabelele din baza de date, la care am impus regulile 
prezentate in enunt si am facut o metoda care sa returneze un dictionar cu datele din baza de date,
prelucrand numele coloanelor pentru a satisface schema requesturilor. Pentru api am respectat cerintele din enunt.
