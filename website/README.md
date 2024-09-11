---
title: Gettinglost Streamlit
emoji: 🏃
colorFrom: gray
colorTo: gray
sdk: streamlit
sdk_version: 1.35.0
app_file: app.py
---

To run the app you need to provide a secrets file that contains information to connect to the database, it can 
be stored in your `~/.streamlit/` directory or anywhere else if you modify the `streamlit.toml` file in this 
directory.

It needs to contain the following keys:

~~~
dbname = user =
password =
host =
port =
sslmode = 'prefer'
~~~
