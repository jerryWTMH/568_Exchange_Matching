#!/bin/bash
taskset --cpu-list 0-3 python3 server.py