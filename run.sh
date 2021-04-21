#for f in experiments/*/*.cfg
FILES="
experiments/004-link-adding-effect/config.cfg"
for f in $FILES
do
	echo $f
	python3 main.py -c $f
done
