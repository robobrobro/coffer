#!/bin/bash

nosetests --with-coverage --cover-package=coffer --cover-branches --cover-erase --cover-html --cover-html-dir=htmlcov -v
