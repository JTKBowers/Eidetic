#create postgres user
createuser eidetic

#then the db
createdb eidetic

# finally, create the tables
psql -d eidetic -U eidetic -f init_tables.sql
