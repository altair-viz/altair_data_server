all: install

install:
	pip install .

test:
	black .
	python -m flake8 altair_data_server
	python -m mypy altair_data_server
	rm -r build
	python setup.py build &&\
	  cd build/lib &&\
	  python -m pytest --pyargs --doctest-modules altair_data_server

test-coverage:
	python setup.py build &&\
	  cd build/lib &&\
	  python -m pytest --pyargs --doctest-modules --cov=altair_transform --cov-report term altair_data_server

test-coverage-html:
	python setup.py build &&\
	  cd build/lib &&\
	  python -m pytest --pyargs --doctest-modules --cov=altair_transform --cov-report html altair_data_server