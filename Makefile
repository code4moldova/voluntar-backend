help:
	@echo  'Commands:'
	@echo  '  autoformat   - Run black on all the source files, to format them automatically'
	@echo  '  verify       - Run a bunch of checks, to see if there are any obvious deficiencies in the code'
	@echo  ''

autoformat:
	black -l 120 ./backend/

verify:
	black -l 120 --check ./backend/
	flake8 --config=.flake8 ./backend/
# 	bandit -r ./backend/
