#!/bin/bash

src=dags/*
dst=/opt/airflow/dags/

rsync $src $dst
echo "Dags from $src dir was successfully synchronized with $dst"
