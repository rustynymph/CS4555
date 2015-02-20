runAllTestsParentInDirectory () {
	PYTHONINPUT=" "
	for x in $1/* ; do
		if [ -d $x ] ; then
			PYTHONFILE=$x/*.py
			PYTHONINPUT=$x/*.in
			runTests $PYTHONFILE $PYTHONINPUT
		fi
	done
}

runTests () {
	PYTHONFILENAME=$1
	ABSOLUTEFILENAME=$(basename $1 | rev | cut -d '.' -f 2 | rev)
	DIRECTORY=$(dirname "$1")
	ASSEMBLYFILENAME=$(echo $ABSOLUTEFILENAME".s")
	
	POUTPUT=$(python "compile.py" "$PYTHONFILENAME")
	gcc $DIRECTORY/$ASSEMBLYFILENAME runtime/*.c -lm -m32
	mv "a.out" $DIRECTORY"/a.out"
	interpreted=$(python $1 < $2)
	compile=$($DIRECTORY/a.out < $2)

	diff <(echo $interpreted) <(echo $compile)


}

TESTDIR="./tests"
if [ -d $TESTDIR ]; then
	if [ $1 == "all" ] ; then
		for directory in $TESTDIR/* ; do
			runAllTestsParentInDirectory $directory
		done
	fi
fi