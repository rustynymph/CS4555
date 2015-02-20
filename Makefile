submit:
	zip  hw.zip compile.py AssemblyAST.py Flatten.py LivenessAnalysis.py Optimizer.py Parser_hw2.py Translator.py ply/ -j runtime/*

clean:
	find . -type f -name "*.s" -delete
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.out" -delete
	find . -type f -name "*.zip" -delete
	find . -type f -name "*.gch" -delete