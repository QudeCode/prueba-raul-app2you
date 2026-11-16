# Prova Tècnica - Reserves 

## Introducció

L’objectiu d’aquesta prova és dissenyar i implementar una aplicació capaç de resoldre un problema de gestió de reserves de recursos empresarials.

L’aplicació completa consta de dues parts: **frontend** i **backend**.  
**Només cal desenvolupar-ne una**, la que millor s'ajusti al teu perfil per tal de mostrar al màxim les teves habilitats.

### Què s’espera en cada cas?

#### Si esculls Frontend
- Implementació de les pantalles principals.
- Implementació de la lògica de negoci i casos d’ús.
- Comunicació amb backend *mock* (dades simulades).

#### Si esculls Backend
- Implementació d’API REST amb els diferents endpoints.
- Implementació de la lògica de negoci i casos d’ús.
- Persistència de dades en base de dades.

### Tecnologies

Escull la tecnologia amb la qual et sentis més còmode d’aquestes:

**Frontend:**
- Android (natiu)
- iOS (natiu)
- Angular  

**Backend:**
- Django
- Python

### Recomanacions
- No perdis temps amb configuracions complexes i detalls molt tècnics (BD, infraestructura, UI...). Ha de ser funcional.
- Valorem especialment un bon anàlisi del problema, un modelat acurat i una implementació neta i ben estructurada.


### Entrega
La teva entrega ha d'incloure:
- **Codi font** (ZIP o repositori GitHub)
- **Instruccions d’execució**
- **Documentació** de l’arquitectura i decisions preses


## Context 

Es demana desenvolupar un sistema de reserves de recursos empresarials, on els treballadors ha de poder consultar els diferents recursos disponibles, veure la seva disponibilitat i efectuar i cancel·lar reserves.
Tots els recursos tenen **nom**, **descripció**, i un **tipus**, cadascun amb els seus atributs específics.

### Tipus de recursos

#### Sales de reunions
- Reserves per hores en un dia concret.
- Capacitat màxima.
- Possibilitat d’**aforament compartit**: diverses reserves simultànies sense superar la capacitat total. 

#### Vehicles
- Reserves per **dies complets**.

#### Equipaments
- Reserves per hores o dies sencers.


## 1. Consultar recursos

El sistema ha de permetre llistar tots els recursos disponibles en una mateixa llista.
Ha de permetre veure el seu nom, descripció, el tipus, la imatge representativa del tipus i els seus atributs específics de cada tipus.

## 2. Consultar disponibilitat

El sistema ha de permetre consultar la disponibilitat d'un recurs per a una data concreta.
Ha de mostrar si està disponible o no en aquell dia (pel cas dels dies) o el rang d'hores disponibles (pel cas de les hores).
Si té aforament compartit, també ha de mostrar quina capacitat queda lliure.
Ha de ser capaç d'explicar per què no està disponible (quines reserves bloquegen)

Per poder fer les proves, hauràs d'emplenar el sistema amb algunes reserves previament generades (aleatories per exemple).

## 3. Reserva de recursos

Es vol poder reservar un recurs donat un dia i/o un rang horari (segons el tipus de recurs).
El sistema ha de garantir que ningú més pugui reservar aquest mateix recurs, validant conflictes temporals (tenir en compte solapaments parcials, totals, etc.).
Ha de tenir en compte si el recurs té aforament compartit, podent indicar la quantitat a reservar i validant que no es sobrepassi la capacitat del recurs


### 4. Aprovació de Reserves

Per tal de controlar millor l'ús dels recursos, un responsable ha d'aprovar primer les reserves fetes pels treballadors.
Per tant, hi ha dos tipus d'usuaris: treballador i responsable.
Quan un treballador fa una reserva, aquesta queda en estat pendent fins que un responsable l'aprova.
Un responsable pot reservar directament sense necessitat d'aprovació, inclús si el recurs està pendent d'aprovació.
La consulta de disponibilitat ha d'indicar també les reserves pendents d'aprovació.


### 5. Cancel·lació de reserves 

Els usuaris han de poder cancelar les reserves dels seus recursos per tal d'alliberar-los.
Ha de validar segons la política de cancel·lació. Cada recurs pot tenir diferents tipus de cancel·lació: flexible, moderada, bloquejada.
   - **Flexible**: cancel·lació fins 1h abans i permet ser transferida a un altre usuari en qualsevol moment.
   - **Moderada**: cancel·lació fins 24h abans, però passat el límit permet ser transferida a un altre usuari.
   - **Bloquejada**: no es pot cancel·lar ni transferir a un altre usuari



Tens llibertat total per modelar el sistema i escollir les classes, mètodes, atributs, capes, patrons i estructures que consideris més adients per resoldre el problema.
Valorem especialment la teva capacitat per analitzar, abstraure i dissenyar una solució clara, coherent i escalable, així com la justificació de les decisions que prenguis.

Molta sort!