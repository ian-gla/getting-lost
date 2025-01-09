# Getting Lost Back End


## Prerequesits

You will need to have installed `python3`, `python3-venv`, `postgresql` and `postgis`.

## Setup

It is assumed that you are running in a virtual environment (`python3 -m venv .venv`) as recent Linuxs won't
let you install stuff directly in the main `python` install (which is probably a good thing).

Start the virtual environment `. .venv/bin/activate`.

It should be sufficient to run `pip install -r requirements.txt` to set the virtual environment. 

## Database set up 

In theory you should be able to just run `alembic upgrade head` to create the database schema, tables etc. You
will need to create a database called `getting-lost` and set an environment variable `database_url` that
equals something like `postgresql://iturton:ianian@localhost/getting-lost` (though with your username and
password) before it will work.

## Contributing 

The central git repository is https://github.com/GDSGlasgow/getting-lost 

If all is working then making changes to `data/models.py` to change the data structures and then running
`alembic revision --autogenerate -m "new models"` should create a new
[alembic](https://thinhdanggroup.github.io/alembic-python/) migration script, then running `alembic upgrade
head` should update the database to reflect the new model. 
