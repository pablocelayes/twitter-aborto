#!/bin/bash
# LLamar así:
# stdbuf -oL ./update_terminos.sh &>> ../logs/update_terminos.log
source /home/pablo/.virtualenvs/tesiscomp/bin/activate
cd /home/pablo/Proyectos/bsd_metrics/abortolegal/src/
python update_terminos.py
