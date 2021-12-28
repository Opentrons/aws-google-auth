.PHONY:test
test:
	python3 -m unittest -v -f
	@echo "check to be sure we didn't mess up our local aws configs..."
	@aws configure list --profile identity &> /dev/null || {\
  		echo "aws configs are damaged";\
		exit 1;\
	}
	@echo "...ok"