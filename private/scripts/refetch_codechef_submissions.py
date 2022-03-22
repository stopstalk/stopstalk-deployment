import time

db = current.db
atable = db.auth_user
stable = db.submission
nrtable = db.next_retrieval

cut_off_time_stamp = "2021-01-01 00:00:00"

query = (stable.time_stamp >= cut_off_time_stamp) & \
		(stable.site == "CodeChef") & \
		(stable.user_id != None)
rows = db(query).select(stable.user_id, groupby=stable.user_id)

print "Fetched", len(rows), "users"
for row in rows:
	print "Processing", row.user_id

	query = (stable.user_id == row.user_id) & \
			(stable.site == "CodeChef") & \
			(stable.time_stamp >= cut_off_time_stamp)
	print "Deleted", db(query).delete(), "submissions"

	user_row = atable(row.user_id)
	user_row.update_record(codechef_lr=cut_off_time_stamp)

	nrrow = db(nrtable.user_id == row.user_id).select().first()
	nrrow.update_record(codechef_delay=1)

	db.commit()
	print "_________________________________________"
	time.sleep(1)
