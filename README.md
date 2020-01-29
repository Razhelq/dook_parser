# dook_parser


Python 3.8.1 application created to parse gunicorn logs.

*How to run the application:*

    It's a console application which can be executed in terminal/command prompt.
    eg.:
    python parser.py filenanme.log --from 0-11-2019_09-07-22 --to 0-11-2019_09-07

Application takes up to 3 arguments using argparse library:

    optional arguments:
    --from  beginning of the time   'eg. 30-11-2019_09-07-22'
    --to    end of the time frame   'eg. 30-11-2019_09-07-22'
    required argument:
    --file  string with file name   'eg. gunicorn.log2'

Tests are made in pytest. They require example gunicorn.log2 file in same directory. There are 4 use cases (without argument, with "from" only, with "to" only and with both)
For each case there are setup modules which creates Logg objects and tests functions which tests all methods. 
Tests could be merged but I decided to mark each use case to have a possibility to launch them separately.
There are 4 marks: no_arg, fromm, to, from_to.

*How to run tests:*

    type in console one of below lines
    pytest
    pytest -m no_arg
    pytest -m fromm
    pytest -m to
    pytest from_to

__App Description:__

At first application checks if the from/to arguments were provided and converts values to datetime format.
For date part - user needs to provide at least a day number, next values will be assigned automatically 
(for "from" argument it will be beginning of the unix epoch date, for "to" argument - current date).
For time part - if not provided (eg. 30-11-2019) 
or partially provided (eg. 30-11-2019_09) the rest values will be assigned automatically
(for "from" value it will be the lowest number (eg. midnight 00:00:00), 
for "to" values it will be the highest number (eg. 23:59:59))    

Next application opens a file and read provided log file line by line. 
For each of them at first application check if date in the line is inside provided time frame.
Next it starts to count the requests and look for the responses and responses sizes.
When all lines are done application counts average size of 2xx requests
 and requests per seconds value.
 
At the end application displays the values in clean format.
