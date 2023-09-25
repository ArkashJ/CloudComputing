# hw2_mini_internet

https://cdn-uploads.piazza.com/paste/l78dcjpoj615ed/59d96dd159ba1094a7b22833e823fcbca915783586cb05a1bb38fc1b9c4a649f/DS_561-HW_2.pdf

## Steps to run the code
1. Create a virtual environment
```
python3 -m venv env
```
2. Activate the virtual environment
```
source venv/bin/activate.fish
```
3. Install the requirements
```
pip3 install -r requirements.txt
```
4. Make the mini_internet
```
python3 generate_content.py
```
5. Move .html files to a folder called "mini_internet"
```
mkdir mini_internet
mv *.html mini_internet
```
Note: if you use another directory name, you will need to change the directory name in the code.
Go the iter_files_and_get_links function in pagerank.py and change the directory name

6. Run the code
```
python3 pagerank.py --local
```


## Options for running the code
RUN LOCALLY
```
python3 pagerank.py --local
```
RUN ON CLOUD
```
python3 pagerank.py --cloud
```
TEST LOCALLY
Note: you may need to change the epsilon value in (pagerank function) the code to 0.0001
```
python3 pagerank.py --test
```

## Python Commands
Running Python lint to check style
```
pylint pagerank.py 
```

Lint code
```
black pagerank.py
```

Make a virtual environment and run it in fish
```
python3 -m venv env
source venv/bin/activate.fish
```

## Regex
Running regex.compile to prevent making regex objects again anad again 
```
re.compile(str)
```

## Numba
Use numba only on static classes and do not pass in complex data types into the function or call them in the array

## Logic
- Make an adjacency matrix of the graphs where the rows are the nodes and the columns are the edges
- Compute the outgoing and incoming edges of each node
- in each iteration, get the pagerank for each node 
- check if the pagerank is converging

