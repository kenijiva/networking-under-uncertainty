#for f in experiments/*/*.cfg
FILES="
experiments/015-cost_over_time_capacity_pst6_forward_add_t5/config.cfg
experiments/015-cost_over_time_capacity_pst6_backward_add_t5/config.cfg"
#experiments/015-cost_over_time_capacity_ksp4_forward_upgrade_t5/config.cfg
#experiments/015-cost_over_time_capacity_ksp4_backward_upgrade_t5/config.cfg
#experiments/015-cost_over_time_capacity_pst6_forward_upgrade_t5/config.cfg
#experiments/015-cost_over_time_capacity_pst6_backward_upgrade_t5/config.cfg
#experiments/015-cost_over_time_capacity_ksp4_forward_add_t5/config.cfg
#experiments/015-cost_over_time_capacity_ksp4_backward_add_t5/config.cfg

#grbgetkey 371e5d52-9faa-11eb-9f30-0242ac130002

for f in $FILES
do
	echo $f
	python3 main.py -c $f
done
