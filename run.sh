#for f in experiments/*/*.cfg
FILES="
experiments/013-cost_over_time_capacity_ksp4_forward_upgrade_t5/config.cfg
experiments/013-cost_over_time_capacity_ksp4_backward_upgrade_t5/config.cfg
experiments/013-cost_over_time_capacity_pst6_forward_upgrade_t5/config.cfg
experiments/013-cost_over_time_capacity_pst6_backward_upgrade_t5/config.cfg
experiments/013-cost_over_time_capacity_ksp4_forward_add_t5/config.cfg
experiments/013-cost_over_time_capacity_ksp4_backward_add_t5/config.cfg
experiments/013-cost_over_time_capacity_pst6_forward_add_t5/config.cfg
experiments/013-cost_over_time_capacity_pst6_backward_add_t5/config.cfg"
for f in $FILES
do
	echo $f
	#python3 main.py -c $f
done
