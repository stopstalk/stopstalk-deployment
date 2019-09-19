"""
    Copyright (c) 2015-2019 Raj Patel(raj454raj@gmail.com), StopStalk

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

tags_mapping = {("Easy",): ("Easy", "easy", "simple", "Introduction", "Fundamentals"),
                ("Medium",): ("Medium", "medium", "Easy-Medium", "easy-medium"),
                ("Hard",): ("Hard", "hard", "medium-hard", "Medium-Hard", "hardest problem"),
                ("Data Structures",): ("data structures", "data-structure", "Data Structure", "datastructures", "Data Structures", "Data-Structures"),
                ("Probability",): ("probabilities", "probability", "Probability", "Probability & Statistics - Foundations"),
                ("Implementation",): ("implementation", "Implementation", "Basic Programming", "basic-prog"),
                ("Divide and Conquer",): ("divide and conquer", "divide-and-conq"),
                ("Game Theory",): ("Game Theory", "game-theory", "game"),
                ("Dynamic Programming",): ("dp", "Dynamic Programming", "dynamic-prog", "dynamic-programming", "dynamic programming", "Dynamic programming"),
                ("Constructive Algorithms",): ("constructive algorithms", "Algorithms", "algorithm", "Constructive Algorithms"),
                ("Greedy",): ("greedy", "Greedy"),
                ("Sorting",): ("sortings", "sorting", "Sorting"),
                ("Math",): ("math", "maths", "Math", "simple-math", "simple-math-1", "simple-maths", "Simple-math", "ProjectEuler+", "Mathematics", "basic-math", "Algebra", "basic-maths", "mathematics", "matrices", "arithmetic"),
                ("Number Theory",): ("number theory", "number-theory", "Number Theory"),
                ("Geometry",): ("Geometry", "geometry"),
                ("Combinatorics",): ("Combinatorics", "combinatorics", "combinations"),
                ("Disjoint Set Union",): ("dsu", "Disjoint Set", "disjoint-set", "union-find", "disjoint-set-2"),
                ("Minimum Spanning Tree", "Graph"): ("mst", "Minimum Spanning Tree", "spanningtree"),
                ("Graph",): ("graph", "graphs", "Graph", "Graphs", "graph-theory", "Graph Theory", "graph matchings", "graph theory", "maxflow", "mincut-maxflow", "floyd-warshall"),
                ("Depth First Search", "Graph"): ("dfs and similar", "dfs", "DFS"),
                ("Breadth First Search", "Graph"): ("bfs", "BFS"),
                ("Ad-hoc",): ("adhoc", "ad-hoc", "Ad-Hoc", "ad-hoc-1", "cakewalk", "cake-walk", "Very-Easy", "Ad Hoc", "problem for beginners"),
                ("String",): ("string", "String", "strings", "Strings", "String Algorithms", "string algorithms", "string suffix structures"),
                ("Tree",): ("trees", "Trees", "tree", "Tree"),
                ("Binary Search Tree",): ("Binary Search Tree",),
                ("Segment Tree",): ("Segment Tree", "segment-tree", "Segment Trees", "segment-trees"),
                ("Trie",): ("tries", "Trie", "trie", "trie-1", "Tries"),
                ("Bit Manipulation",): ("bitwise-operatn", "bitwise", "Bit Manipulation", "Bit manipulation", "bit"),
                ("Bitmasks",): ("Bitmasks", "bitmasks", "bitmasking", "Bitmask"),
                ("Dynamic Programming", "Bit Manipulation"): ("dp+bitmask",),
                ("Hashing",): ("hashing", "Hashing"),
                ("Binary Search",): ("binarysearch", "binary-search", "binary search", "Binary Search"),
                ("Brute Force",): ("brute force", "Brute Force", "brute-force", "bruteforce"),
                ("Two Pointers",): ("two pointers", "Two-pointer", "two-pointers"),
                ("Binary Indexed Tree",): ("fenwick", "BIT"),
                ("Stacks",): ("stack", "Stack", "stacks", "Stacks"),
                ("Queues",): ("Queue", "Queues", "queues"),
                ("Binary Tree",): ("binary-tree",),
                ("Heap",): ("Heap", "heap"),
                ("Priority Queue",): ("priority-queue", "Priority Queue", "Priority-Queue"),
                ("Recursion",): ("recursion", "Recursion", "Memoization", "Recurrence", "recurrence", "recurrences"),
                ("Shortest Path", "Graph"): ("Shortest Path", "shortest paths", "shortest-path", "dijkstra", "Dijkstra", "dijkstra-s-algorithm"),
                ("Graph Coloring",): ("two-coloring", "bicolor"),
                ("Convex Hull",): ("convex-hull",),
                ("Backtracking",): ("backtracking", "Backtracking"),
                ("Sieve",): ("Sieve", "sieve"),
                ("Linked List",): ("Linked Lists",),
                ("Matrix Exponentiation",): ("matrix-expo", "Matrix Exponentiation", "exponentiation"),
                ("Ternary Search",): ("ternary search", "Ternary Search"),
                ("Square Root Decomposition",): ("sqrt-decomp", "Sqrt-Decomposition"),
                ("Functional Programming",): ("Functional Programming",),
                ("Array",): ("array", "suffix-array", "Suffix Arrays", "Arrays", "arraysum", "Subarrays", "subarray", "Arrays & Hashes"),
                ("Artificial Intelligence",): ("Artificial Intelligence",)}

problems = db(ptable).select(ptable.id, ptable.tags)
untagged = {}

for problem in problems:
    if problem.tags == "['-']":
        continue

    current_set = set([])
    this_tags = set(eval(problem.tags))

    for key in tags_mapping:
        for possibility in tags_mapping[key]:
            if problem.tags.__contains__("'" + possibility + "'"):
                this_tags.remove(possibility)
                for final_tag in key:
                    current_set.add(final_tag)

    flag = False

    for final_tag in current_set:
        if (1L, problem.id, all_tags[final_tag]) not in current_suggested_tags:
            flag = True
            sttable.insert(user_id=1L,
                           tag_id=all_tags[final_tag],
                           problem_id=problem.id)
    if flag:
        print problem.id, problem.tags, "-->", current_set

    for final_tag in this_tags:
        if untagged.has_key(final_tag):
            untagged[final_tag] += 1
        else:
            untagged[final_tag] = 1

print "\n\n\n=========================== Untagged ===========================\n"

for a, b in sorted(untagged.items(), key=lambda (k, v): (v, k), reverse=True):
    print a, b
