# MedicalDataService
System for storing, indexing and visualizing medical data in DICOM format

## Diagrams
1. [Use case diagram](https://app.diagrams.net/#Hcitec-spbu%2FMedicalDataService%2Fmain%2FDiagrams%2FUseCaseDiagram.drawio#%7B%22pageId%22%3A%22K9DpIMCQUKm6tweqTpe7%22%7D)
2. [Activity diagram](https://app.diagrams.net/#Hcitec-spbu%2FMedicalDataService%2Fmain%2FDiagrams%2FActivityDiagram.drawio#%7B%22pageId%22%3A%22d6oIZNa-YsMYUfMxQyWx%22%7D)
3. [ER diagram](https://app.diagrams.net/#Hcitec-spbu%2FMedicalDataService%2Fmain%2FDiagrams%2FERDiagram.drawio#%7B%22pageId%22%3A%22ZZTZYGC4paBtnbswUOO2%22%7D)
4. [Sequence diagram](https://app.diagrams.net/#Hcitec-spbu%2FMedicalDataService%2Fmain%2FDiagrams%2FSequenceDiagram.drawio#%7B%22pageId%22%3A%22-7-vLeRaQvUi-DyRjATi%22%7D)

## Backend setup
1. Install python3.12 interpreter 
2. Install dependencies with `pip install -r requirements.txt`
3. Create a database `YOUR_DB_NAME` for the project, specify the password for this database for your user.
4. Create `.env` file in root folder of project with following content:
    ```
    DB_HOST = 'localhost'
    DB_PORT = '5438'
    DB_NAME = 'YOUR_DB_NAME'
    DB_USER = 'YOUR_USER'
    DB_PASSWORD = 'YOUR_PASSWORD'
    ```
    Note that DB_PORT indicates the server version of PostgreSQl, for more info on linux you can run `pg_lsclusters`
5.  Go to app folder, run `alembic init -t async migration`
6. Move `alembic.ini` file from app folder to root folder of project (`mv alembic.ini ..`)
7. In file `alemvic.ini` change row `script_location = migration` to `script_location = app/migration`
8. Open file app/migration/env.py, delete all contents from the beginning of the file up to and including line `target_metadata = None` (row 23) and insert the following content instead
    ``` python
    import asyncio
    from logging.config import fileConfig
    
    from sqlalchemy import pool
    from sqlalchemy.engine import Connection
    from sqlalchemy.ext.asyncio import async_engine_from_config
    
    from alembic import context
    
    import sys
    from os.path import dirname, abspath
    
    sys.path.insert(0, dirname(dirname(abspath(__file__))))
    
    from app.database import DATABASE_URL, Base
    from app.users.models import User
    
    
    # this is the Alembic Config object, which provides
    # access to the values within the .ini file in use.
    config = context.config
    config.set_main_option("sqlalchemy.url", DATABASE_URL)
    
    # Interpret the config file for Python logging.
    # This line sets up loggers basically.
    if config.config_file_name is not None:
        fileConfig(config.config_file_name)
    
    target_metadata = Base.metadata
    
    # add your model's MetaData object here
    # for 'autogenerate' support
    # from myapp import mymodel
    # target_metadata = mymodel.Base.metadata
    ```
    Pay attention to `from app.users.models import User`, for each table in the database you need to add the corresponding import to this (env.py) file, however, at the moment there is a description only for the users table in app/users
9. Go to root folder of project, run `alembic revision --autogenerate -m "Initial revision"`, 
10. Run `alembic upgrade head`, a users table has now been created in your database. To roll back changes run `alembic downgrade -1`.
For upgrade alternatively you can run `alembic upgrade VERSION_ID`, where VERSION_ID is id from generated file from folder app/migration/versions which contains a line like `Revision ID: VERSION_ID`
10. Create `certs` directory and enter it `mkdir certs && cd certs`
12. Create RSA256 private certificate `openssl genrsa -out jwt-private.pem 2048`
13. Create RSA256 public certificate based on private `openssl rsa -in jwt-private.pem -outform PEM -pubout -out jwt-public.pem`

## Usage
Run `fastapi dev app/main.py` from root folder of project

To check tokens on the backend, log in with the appropriate token. Tokens can be obtained using the `/user/login/` endpoint

`/user/me` waiting for an access token to enter

`/user/me/jwt/refresh_access_token` waiting for a refresh token to enter
