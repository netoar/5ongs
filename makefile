.PHONY: all

env/bin/activate: requirements.txt
	/usr/local/bin/python3.8 -m venv env
	./env/bin/pip install -r requirements.txt

run: env/bin/activate
	./env/bin/flask run

dev: env/bin/activate
	FLASK_ENV=development ./env/bin/flask run

freeze: env/bin/pip
	./env/bin/pip freeze > requirements.txt

test: env/bin/activate
	./env/bin/python -m unittest test_app.py

clean:
	rm -rf __pycache__
	rm -rf ./env