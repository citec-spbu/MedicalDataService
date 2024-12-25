# MedicalDataService

System for storing, indexing and visualizing medical data in DICOM format

## Diagrams

1. [Use case diagram](https://app.diagrams.net/#Hcitec-spbu%2FMedicalDataService%2Fmain%2FDiagrams%2FUseCaseDiagram.drawio#%7B%22pageId%22%3A%22K9DpIMCQUKm6tweqTpe7%22%7D)
2. [Activity diagram](https://app.diagrams.net/#Hcitec-spbu%2FMedicalDataService%2Fmain%2FDiagrams%2FActivityDiagram.drawio#%7B%22pageId%22%3A%22d6oIZNa-YsMYUfMxQyWx%22%7D)
3. [ER diagram](https://app.diagrams.net/#Hcitec-spbu%2FMedicalDataService%2Fmain%2FDiagrams%2FERDiagram.drawio#%7B%22pageId%22%3A%22ZZTZYGC4paBtnbswUOO2%22%7D)
4. [Sequence diagram](https://app.diagrams.net/#Hcitec-spbu%2FMedicalDataService%2Fmain%2FDiagrams%2FSequenceDiagram.drawio#%7B%22pageId%22%3A%22-7-vLeRaQvUi-DyRjATi%22%7D)

## Setup via Docker (Recomended)

1. `docker-compose build`
2. `docker-compose up`

#### To stop containers

1. `docker-compose down`

## Backend setup (May not work)

1. Install python3.12 interpreter.
2. Install dependencies with `pip install -r requirements.txt`.
3. Create `certs` directory and go it.
4. Create RSA256 private certificate `openssl genrsa -out jwt-private.pem 2048`.
5. Create RSA256 public certificate based on private `openssl rsa -in jwt-private.pem -outform PEM -pubout -out jwt-public.pem`.
6. Go back to root.
7. Launch postgres and create a database.
8. Launch minio and create a bucket.
9. Launch rabbitmq.
10. Create `.env`, copy content from `to_copy/dot_env.txt` and edit if needed.
11. Run `alembic init -t async migration`.
12. Copy content from `to_copy/env_py.txt` to `migration\env.py`.
13. Run `alembic revision --autogenerate -m "Initial revision"`.
14. Run `alembic upgrade head`.
15. Uncomment 3 lines in `migration\env.py`.
16. Run `alembic revision --autogenerate -m "Initial revision"`.
17. Run `alembic upgrade head`.
18. For upgrade alternatively you can run `alembic upgrade VERSION_ID`, where VERSION_ID is id from generated file from folder app/migration/versions which contains a line like `Revision ID: VERSION_ID`.

## Usage

Run `fastapi dev app/main.py` from root folder of project

To check tokens on the backend, log in with the appropriate token. Tokens can be obtained using the `/user/login/` endpoint

`/user/me` waiting for an access token to enter

`/user/me/jwt/refresh_access_token` waiting for a refresh token to enter
