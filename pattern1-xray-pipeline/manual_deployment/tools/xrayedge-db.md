# Database commands used in the demo

## Connexion to the DB (oc rsh first into the DB pod)

```bash
mysql -u root
```

```sql
USE xraylabdb;
```

# Reinitialize the environment

You can copy/paste all lines at once in the mysql prompt. Don't forget the blank line at the end if you want to run the last command automatically!

```sql
DROP TABLE images_uploaded;
DROP TABLE images_processed;
DROP TABLE images_anonymized;

CREATE TABLE images_uploaded(time TIMESTAMP, name VARCHAR(255));
CREATE TABLE images_processed(time TIMESTAMP, name VARCHAR(255), model VARCHAR(10), label VARCHAR(20));
CREATE TABLE images_anonymized(time TIMESTAMP, name VARCHAR(255));

INSERT INTO images_uploaded(time,name) SELECT CURRENT_TIMESTAMP(), '';
INSERT INTO images_processed(time,name,model,label) SELECT CURRENT_TIMESTAMP(), '', '','';
INSERT INTO images_anonymized(time,name) SELECT CURRENT_TIMESTAMP(), '';

```

## Display rows from each table

```sql
SELECT * FROM images_uploaded;
SELECT * FROM images_processed;
SELECT * FROM images_anonymized;

```
