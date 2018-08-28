# aspace-comma-endings

A single script that
* looks for ArchivesSpace resource/digital object titles that end with a comma,
* saves them in a list and generates a CSV report, and
* changes any matching titles found with details saved to a log file.

To run, you will need the following libraries installed:
* [ArchivesSnake](https://github.com/archivesspace-labs/ArchivesSnake)
* [Pandas](https://pandas.pydata.org/)
* [TQDM](https://github.com/tqdm/tqdm)


You will also need to edit the script with your credentials here:
```client = ASnakeClient(baseurl='xxx',
                      username='xxx',
                      password='xxx')```
