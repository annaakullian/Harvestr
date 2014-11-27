#/bin/sh

psql -c "drop database harvester"
psql -c "create database harvester"
python model.py

psql -d harvester -f harvester.sql
