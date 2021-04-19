#for f in experiments/*/*.cfg
FILES="
experiments/016-cost_over_time_ksp4_forward_add_t5_NO_CUTOFF/config.cfg"
for f in $FILES
do
	echo $f
	python3 main.py -c $f
done
