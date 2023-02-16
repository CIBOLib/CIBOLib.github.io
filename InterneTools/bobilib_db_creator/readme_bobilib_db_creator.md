# Usage: 

First you need to have a config.json. 
Therefore use the json_config_creator.py to get one as follows:

1) Open a terminal in the directory of the json_config_creator.py and type in:

	'python3 json_config_creator.py'


2) Then you need to enter some paths:

	a) Collection path (where the mps/aux-Files are), e.g.: /path_1/collection 

	b) Html path (where the json for browsing and the instance htmls should be stored), e.g: path_2/htmls

	c) Layout path (to make sure the instance htmls have the same layout as the other htmls), e.g.: path_3/_layouts/default.html

	d) Css path (to make sure the instance htmls have the same style as the other htmls), e.g.: path_4/css/main.css


3) Then you will be asked if you want to compress (sub-)directories of the collection. 
   This will give you the possibility to create tar.gz automatically (e.g. MIPLIB2010.tar.gz). 

   If you type in: 'Yes', 'yes' or 'y' you have to provide the path where you want to store the tar.gz, e.g.: path_5/archives


Congratulations! The config.json should appear in the same directory as the json_config_creator.py and the bobilib_db_creator.py.
Now you just need to type 'python3 bobilib_db_creator.py' into your (still open or a new) terminal to create the content for the BIBOLib page.