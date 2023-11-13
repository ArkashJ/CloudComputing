Using Apache Beam and Cloud Data Flow to read 10k files and 
find out the top 5 incoming and top 5 outgoing calls.

For local testing:
Set up virtual environment:
```
source env/bin/activate.fish
pip install -r requirements.txt
```

Run:
```
python main.py --input "../hw2/mini_internet_test/" --output="."
```
