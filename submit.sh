#!/bin/bash
#BSUB -q normal
#BSUB -n 1
#BSUB -e /gpfs/home/jqlu/double_color_balls/result.err
#BSUB -o /gpfs/home/jqlu/double_colro_balls/result.out
python /gpfs/home/jqlu/double_color_balls/balls_train.py
