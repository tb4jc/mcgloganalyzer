# McgLogAnalyzer

Analyzer of log files retrieved from MCG by MCG Issue Archive download.

It can unpack a given MCG Issue Archive or work on an existing direcory.
During the evalation, it detects if the issue archive contains normal set of log files or one with files created by the MCG Extended Logger script.

The tool merges multiple log files as:
- syslog              /tmp/messages*
- MCG Application Log /usr/local/data/log/mcgLogger.log*
- Communication Log   /usr/local/data/log/comLogger.log*
- BTCL Client Log     /usr/local/data/log/btclClient.log*

Additional it creates two files as a merger of all above logs:
- Text File as CSV
- Excel File with additional coloring and possibility for filtering

