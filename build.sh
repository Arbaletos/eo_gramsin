#!/bin/bash

python3 morph.py fundamenta-krestomatio ondo monato
python3 stat_anal.py monato
python3 stat_anal.py ondo
python3 stat_anal.py fundamenta-krestomatio
python3 mark.py