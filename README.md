# Getting Lost


## Website

The web site is contained in 3 files in the `website` directory. The structure of the page is set in 
`index.html`, which is styled by `style.css`. Interactivity and data submission is handled by `script.js` 
which depends on the [Leaflet](http://leaflet.org) library to display the map and markers. As the user moves 
from one section to the next in the application the current results are `POST`ed to the back end server, with 
later updates sent using `PUT`. Once a set of positions are stored the app holds the `position_id` that refers 
to that record. This id is set in the user record when that is created and a `user_id` is returned. If either 
of those variables is set to a non-zero value then the data will be updated rather than created, Finally, an 
event record is created with a reference to both the user and position being stored. The user is offered a 
final opportunity to edit the three records before submitting the data. 

### Testing

A local copy of the web site can be run locally `python3 -m http.server 4000` inside the `website` directory. 
If you want to test interactions with the back end then you will also need to be running a back end server as 
described below. If the server is running anyway except `localhost:8000` you will need to set the URL in the 
`env.js` file. 

## Backend

The application logic for the back end server is implemented in the `backend` directory. The server is 
implemented using the [`FastAPI` library](https://fastapi.tiangolo.com/), with interactions with the database 
being handled by [`SQLAlchemy` ](https://www.sqlalchemy.org/) to give an abstraction layer above the database.

The code should be run in a python virtual environment with the dependencies from `requirements.txt` installed 
(`pip install -r requirements.txt`). FastAPI uses the [`uvicorn` server software](https://www.uvicorn.org/) to 
provide the service, it is started (in the `backend` directory) `uvicorn main:app --reload`. Make sure that 
you have set up the **correct** database URL as discussed below. 

### Database

The data is stored in a PostGIS database. The location of the database is set via an environment variable 
(`database_url`) which should contain a PostGIS connection URL like 
(`postgresql://user:password@localhost/lost`). The data is stored in three tables in the `lost` schema, 
`positions`, `users` and `events`. These tables are created automatically via [`alembic` 
](https://alembic.sqlalchemy.org/en/latest/index.html) using the command `alembic upgrade head`. As a result 
any changes to the structure of the database **must** be made in the python code `data/models.py`. This will 
then allow the database creation code to be updated via `alembic revision --autogenerate -m "reason for 
change"`, you will then need to check and possibly modify the `alembic` version file before running the 
`upgrade` command. 

### Testing

To access a test database set a `test_database_url` in the same format as above, the unit tests will create 
and clean the database so you should avoid running the unit tests against the production database! Unit tests 
are executed from the `backend` directory with `python -m pytest`, any new functionality or bug fixes should 
have a passing unit test. 
