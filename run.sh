#!/bin/bash

poetry run python src/load_data_trainings.py --path datasets/mbpp.jsonl
while true; do sleep 3600; done