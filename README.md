# check_triangulation
Lab for triangulation checking algorithm implementation.

# Input arguments
Options:
  * `--input` - path to the file, that contains polygon and diagonals descriptions.
  
# Input file example
```
5     # number of points in polygon, after that we have 5 lines with points' coordinates
0 3     
-1 -2
-3 -3
-5 1
-3 3
0 2   # after polygon's points we have diagonals descriptions - every line contains two indices
2 4
```

# Output
`True` or `False`

# TODO
* GUI mode
