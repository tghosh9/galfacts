#Shell Script created by Joseph Kania
#23 June 2014
#end channels are exculded to give better results


#!/bin/sh 

python2.7 find_sources.py --field S0206+330 --date 54707 --beam 0 --exclude_channels 0000 0001 0002 0003 0004 0005 0006 0007 0008 0009 0010 0011 0012 0013 0014 0015 0016  0017 0018 0019 0020 0021 0022 0023 0024 0025 0026 0027 0028 0029 003 0031 0032 0033  1369 1370 1371 1372 1373 1374 1375 1376 1377 1378 1379 1380 1381 2001 2002 2003 2004 2005 2006 2007 2008 2009 2010 2011 2012 2013 2014 2015 2016 2017 2018 2019 2020 2021 2022 2023 2024 2025 2026 2027 2028 2029 2030 2031 2032 2033 2034 2035 2036 2037 2037 2039 2040 2041 2042 2043 2044 2045 2046 2047 --verbose --file_verbose --data_filepath /share/tghosh/galavants/varib/data_calgary 

echo shellDone!
