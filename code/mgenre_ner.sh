dir=$1
out=$2

for file in $dir/*
do
	echo $file
	base=$(basename $file .pickle)
	echo $base
	python entity_le.py $file $base $out
done
