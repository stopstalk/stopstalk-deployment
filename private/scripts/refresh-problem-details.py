"""
    Copyright (c) 2015-2020 Raj Patel(raj454raj@gmail.com), StopStalk

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
import utilities
import pydal.objects
import sites
import gevent
from gevent import monkey
gevent.monkey.patch_all(thread=False)

now_time = datetime.datetime.now()
today = now_time.strftime("%Y-%m-%d")
before_30 = (now_time - \
             datetime.timedelta(30)).strftime("%Y-%m-%d")

pstable = db.problem_setters
pstable_problem_ids = db(pstable.problem_id).select(distinct=True)
pstable_problem_ids = [x.problem_id for x in pstable_problem_ids]

change_counts = {}

# ==============================================================================
class SpecialOps:
    def __init__(self, record):
        self.record_type = "row" if isinstance(record, pydal.objects.Row) else "table"

    # --------------------------------------------------------------------------
    def date_op(self, value):
        return str(value) if self.record_type == "row" else value

    # --------------------------------------------------------------------------
    def contains_op(self, column, contains_value):
        if self.record_type == "row":
            return column.__contains__(contains_value)
        else:
            return column.contains(contains_value)

    # --------------------------------------------------------------------------
    def not_op(self, value):
        if self.record_type == "row":
            return not value
        else:
            return ~value

    # --------------------------------------------------------------------------
    def belongs_op(self, column, search_space):
        if self.record_type == "row":
            return column in search_space
        else:
            return column.belongs(search_space)

# ==============================================================================
class TagHandler():
    # --------------------------------------------------------------------------
    @staticmethod
    def column_value():
        return "tags"

    # --------------------------------------------------------------------------
    @staticmethod
    def conditional(dal_object):
        """
            @params dal_object (DAL relation or Record object): Object on which the conditions should be applied
        """
        special_ops = SpecialOps(dal_object)
        return (special_ops.date_op(dal_object.tags_added_on) >= before_30) & \
               (dal_object.tags == "['-']") & \
               (special_ops.not_op(special_ops.contains_op(dal_object.link,
                                                           "gymProblem/")))

    # --------------------------------------------------------------------------
    @staticmethod
    def update_params(link, prev_value, curr_value):
        # Problems having tags = ["-"]
        # Possibilities of such case -
        #   => There are actually no tags for the problem
        #   => The problem is from a contest and they'll be
        #      updating tags shortly(assuming 15 days)
        #   => Page was not reachable due to some reason

        curr_value = "['-']" if curr_value == [] else str(curr_value)
        if prev_value != curr_value and prev_value == "['-']":
            print "Updated tags", link, prev_value, "->", curr_value
            return dict(tags=curr_value if curr_value != "['-']" else "['-']",
                        tags_added_on=today)
        else:
            print "No-change in tags", link
            return dict()

    # --------------------------------------------------------------------------
    @staticmethod
    def update_database(problem_record, new_value):
        column_value = TagHandler.column_value()
        curr_update_params = TagHandler.update_params(
                                problem_record.link,
                                problem_record[column_value],
                                new_value
                             )

        if len(curr_update_params):
            problem_record.update_record(**curr_update_params)
            change_counts[column_value]["updated"] += 1

        change_counts[column_value]["total"] += 1

# ==============================================================================
class EditorialHandler():
    # --------------------------------------------------------------------------
    @staticmethod
    def column_value():
        return "editorial_link"

    # --------------------------------------------------------------------------
    @staticmethod
    def conditional(dal_object):
        """
            @params dal_object (DAL relation or Record object): Object on which the conditions should be applied
        """
        special_ops = SpecialOps(dal_object)
        return (
                (
                    (dal_object.editorial_added_on == None) |
                    (special_ops.date_op(dal_object.editorial_added_on) >= before_30)
                ) & \
                (
                    (dal_object.editorial_link == None) | \
                    (dal_object.editorial_link == "")
                )
               ) & \
               (
                    special_ops.not_op(
                        special_ops.contains_op(dal_object.link,
                                                "gymProblem/")
                    )
               )

    # --------------------------------------------------------------------------
    @staticmethod
    def update_params(link, prev_value, curr_value):
        if curr_value is not None and prev_value is None:
            print "Updated editorial_link", link, prev_value, "->", curr_value
            return dict(editorial_link=curr_value,
                        editorial_added_on=today)
        else:
            print "No-change in editorial_link", link
            return dict()


    # --------------------------------------------------------------------------
    @staticmethod
    def update_database(problem_record, new_value):
        column_value = EditorialHandler.column_value()
        curr_update_params = EditorialHandler.update_params(
                                problem_record.link,
                                problem_record[column_value],
                                new_value
                             )

        if len(curr_update_params):
            problem_record.update_record(**curr_update_params)
            change_counts[column_value]["updated"] += 1

        change_counts[column_value]["total"] += 1

# ==============================================================================
class ProblemSetterHandler():
    # --------------------------------------------------------------------------
    @staticmethod
    def column_value():
        return "problem_setters"

    # --------------------------------------------------------------------------
    @staticmethod
    def conditional(dal_object):
        special_ops = SpecialOps(dal_object)
        return (special_ops.date_op(dal_object.tags_added_on) >= before_30) & \
               (special_ops.not_op(special_ops.belongs_op(dal_object.id,
                                                          pstable_problem_ids)))

    # --------------------------------------------------------------------------
    @staticmethod
    def update_database(problem_record, new_value):
        column_value = ProblemSetterHandler.column_value()
        change_counts[column_value]["total"] += 1

        problem_link = problem_record.link
        problem_id = problem_record.id

        if new_value is None:
            print "No-change in problem_setters", problem_link
            return

        records = db(pstable.problem_id == problem_id).select()
        existing_records = set([(x.problem_id, x.handle) for x in records])
        prev_value = [x[1] for x in existing_records]

        updated_database = False
        for value in new_value:
            if (problem_id, value) not in existing_records:
                pstable.insert(problem_id=problem_id,
                               handle=value)
                updated_database = True
            else:
                print (problem_id, value), "already exists"

        if updated_database:
            change_counts[column_value]["updated"] += 1
            print "Updated problem_setters", problem_link, prev_value, "->", new_value
        else:
            print "No-change in problem_setters", problem_link
        return

# ==============================================================================
genre_classes = {
    "tags": TagHandler,
    "editorial_link": EditorialHandler,
    "problem_setters": ProblemSetterHandler
}

# ------------------------------------------------------------------------------
def refresh_problem_details():
    ptable = db.problem

    # If tag or editorial retrieval is required
    query = False

    for genre in genre_classes:
        query |= genre_classes[genre].conditional(ptable)

    results = db(query).select(orderby="<random>", limitby=(0, 2000))

    threads = []
    workers = 10
    for i in xrange(0, len(results), workers):
        threads = []
        # O God I am so smart !!
        for problem_record in results[i : i + workers]:
            threads.append(gevent.spawn(get_problem_details,
                                        problem_record))

        gevent.joinall(threads)

    return

# ------------------------------------------------------------------------------
def get_problem_details(problem_record):
    link = problem_record.link

    update_things = []
    for genre in genre_classes:
        this_class = genre_classes[genre]
        if this_class.conditional(problem_record):
            update_things.append(this_class.column_value())

    site = utilities.urltosite(link)
    Site = getattr(sites, site.lower()).Profile

    try:
        details = Site.get_problem_details(problem_link=link,
                                           update_things=update_things)
    except AttributeError:
        # get_problem_details not implemented for this site
        print "get_problem_details not implemented for", link
        return

    for column_value in update_things:
        this_class = genre_classes[column_value]
        this_class.update_database(problem_record, details[column_value])

    return

if __name__ == "__main__":
    for genre in genre_classes:
        change_counts[genre_classes[genre].column_value()] = {
            "updated": 0, "total": 0
        }

    refresh_problem_details()

    print change_counts
