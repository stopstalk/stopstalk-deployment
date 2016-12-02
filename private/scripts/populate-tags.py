"""
    Copyright (c) 2015-2016 Raj Patel(raj454raj@gmail.com), StopStalk

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    THE SOFTWARE.
"""

ptable = db.problem
ttable = db.tag
sttable = db.suggested_tags

all_tags = {}
current_suggested_tags = set([])

tags = db(ttable).select()
for tag in tags:
    all_tags[tag.value] = tag.id

current_state = db(sttable).select()
for row in current_state:
    current_suggested_tags.add((row.user_id, row.problem_id, row.tag_id))

tags_mapping = {("Implementation",): ("implementation",),
                ("Dynamic Programming",): ("dp", "Dynamic Programming", "dynamic-prog", "dynamic-programming"),
                ("Constructive Algorithms",): ("constructive algorithms", "Algorithms"),
                ("Greedy",): ("greedy", "Greedy"),
                ("Sorting",): ("sortings", "sorting", "Sorting"),
                ("Math",): ("math", "maths", "Math", "simple-math"),
                ("Number Theory",): ("number theory", "number-theory", "Number Theory"),
                ("Geometry",): ("Geometry", "geometry"),
                ("Combinatorics",): ("Combinatorics", "combinatorics"),
                ("Disjoint Set Union",): ("dsu", "Disjoint Set", "disjoint-set", "union-find"),
                ("Minimum Spanning Tree", "Graph"): ("mst", "Minimum Spanning Tree", "spanningtree"),
                ("Graph",): ("graph", "graphs", "Graph", "Graphs", "graph-theory", "Graph Theory"),
                ("Depth First Search", "Graph"): ("dfs and similar", "dfs", "DFS"),
                ("Breadth First Search", "Graph"): ("bfs", "BFS"),
                ("Ad-hoc",): ("adhoc", "ad-hoc", "Ad-Hoc", "ad-hoc-1", "cakewalk", "cake-walk"),
                ("String",): ("string", "String", "strings", "Strings"),
                ("Tree",): ("trees", "Trees", "tree", "Tree"),
                ("Binary Search Tree",): ("Binary Search Tree",),
                ("Segment Tree",): ("Segment Tree", "segment-tree", "Segment Trees"),
                ("Trie",): ("tries", "Trie", "trie", "trie-1", "Tries"),
                ("Bit Manipulation",): ("bitwise-operatn", "bitwise", "Bit Manipulation", "Bit manipulation", "bit"),
                ("Bitmasks",): ("Bitmasks", "bitmasks", "bitmasking", "Bitmask"),
                ("Dynamic Programming", "Bit Manipulation"): ("dp+bitmask",),
                ("Hashing",): ("hashing", "Hashing"),
                ("Binary Search",): ("binarysearch", "binary-search", "binary search", "Binary Search"),
                ("Brute Force",): ("brute force", "Brute Force", "brute-force"),
                ("Two Pointers",): ("two pointers", "Two-pointer"),
                ("Binary Indexed Tree",): ("fenwick", "BIT"),
                ("Stacks",): ("stack", "Stack", "stacks", "Stacks"),
                ("Queues",): ("Queue", "Queues", "queues"),
                ("Binary Tree",): ("binary-tree",),
                ("Heap",): ("Heap", "heap"),
                ("Priority Queue",): ("priority-queue", "Priority Queue", "Priority-Queue"),
                ("Recursion",): ("recursion", "Recursion", "Memoization", "Recurrence", "recurrence", "recurrences"),
                ("Shortest Path", "Graph"): ("Shortest Path", "shortest paths", "shortest-path"),
                ("Graph Coloring",): ("two-coloring", "bicolor"),
                ("Convex Hull",): ("convex-hull",),
                ("Backtracking",): ("backtracking", "Backtracking"),
                ("Sieve",): ("Sieve", "sieve"),
                ("Linked List",): ("Linked Lists",),
                ("Matrix Exponentiation",): ("matrix-expo", "Matrix Exponentiation"),
                ("Ternary Search",): ("ternary search", "Ternary Search"),
                ("Square Root Decomposition",): ("sqrt-decomp", "Sqrt-Decomposition")}
problems = db(ptable).select()

for problem in problems:
    if problem.tags == "['-']":
        continue
    print problem.id
    current_set = set([])
    for key in tags_mapping:
        for possibility in tags_mapping[key]:
            if problem.tags.__contains__("'" + possibility + "'"):
                for final_tag in key:
                    current_set.add(final_tag)
                break
    for final_tag in current_set:
        if (1L, problem.id, all_tags[final_tag]) in current_suggested_tags:
            print (1L, problem.id, all_tags[final_tag]), "skipped"
        else:
            sttable.insert(user_id=1L,
                           tag_id=all_tags[final_tag],
                           problem_id=problem.id)
