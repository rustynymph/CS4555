#!/bin/bash
submit:
	mkdir -p "submit"
	cp -r AssemblyAST submit
	cp *.py submit
	cp runtime/* submit
	zip submit.zip submit/*
	rm -r submit

clean:
	find . -type f -name "*.s" -delete
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.out" -delete
	find . -type f -name "*.zip" -delete
	find . -type f -name "*.gch" -delete