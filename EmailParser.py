import csv, json


f = open("Hillary Clinton - Sheet1.csv", "r")
csvfile = csv.DictReader(f)

def contains_headline_less_than_four(story_list):
	for headline in story_list:
		if len(headline.split(" ")) <= 4:
			return True

	return False

def get_idx_less_than_four(story_list):
	for idx, headline in enumerate(story_list):
		if len(headline.split(" ")) <= 4:
			return idx

	return -1


def contains_duplicate_publishers(email_list):
	'''
	find whether there are same publisher's article next to each other,
	which probably means that one is the headline, and the other is the kicker.
	We want to remove the kicker, so we check whether it exists.
	'''
	for idx, email in enumerate(email_list):
		if idx != (len(email_list) - 1):
			if email["publication"] == email_list[idx+1]["publication"]:
				return idx+1

	return -1





email_data =[]
for email in csvfile:
	# email_data = {}
	one_day_headlines = email["Headline"].split("update")
	# print one_day_headlines
	one_day_headlines = [one_day_headline for one_day_headline in one_day_headlines if one_day_headline != ""]
	if len(one_day_headlines) <= 0:
		continue
	else:
		one_day_headlines = one_day_headlines[0]

	# print json.dumps(one_day_headlines, indent=4)


	one_day_headlines = one_day_headlines.split("|")
	one_day_headlines = [d.strip() for d in one_day_headlines]
	one_day_headlines = [d for d in one_day_headlines if d!= ""]

	# print json.dumps(one_day_headlines, indent=4)

	stories = []
	for story in one_day_headlines[2:]:
		story = story.split("\n\n")
		stories.extend(story)

	one_day_headlines = one_day_headlines[0:2] + stories
	one_day_headlines = [d.strip() for d in one_day_headlines]

	stories = one_day_headlines[2:]
	while(contains_headline_less_than_four(stories)):
		
		idx_length_less_than_four = get_idx_less_than_four(stories)

		if idx_length_less_than_four >= len(stories) -1:
			stories[idx_length_less_than_four -1 ] = stories[idx_length_less_than_four -1 ] + "||" + stories[idx_length_less_than_four]	
			stories.pop(idx_length_less_than_four)
			continue
		# hide two bars, so we can seperate them in the future
		stories[idx_length_less_than_four + 1 ] = stories[idx_length_less_than_four] + "||" + stories[idx_length_less_than_four + 1]
		stories.pop(idx_length_less_than_four)
		# remove the one that is already appended

	one_day_headlines = one_day_headlines[0:2] + stories

	# remove two neighbor that has the same publisher
	print json.dumps(one_day_headlines, indent=4)

	one_email_data = []
	for d in one_day_headlines[2:]:
		if d.find("||") != -1:
			headline_publication = d.split("||")
		elif d.find("-") != -1:
			headline_publication = d.split("-")
		else:
			headline_publication = []

		# print headline_publication
		one_date = one_day_headlines[0][one_day_headlines[0].find(" ") + 1:]

		if not len(headline_publication) > 1:
			# continue means, to give up this row.
			continue
			one_email_data.append({
				"headline": d,
				"date": one_date,
				"publication": ""
				})
		else:
			if len(headline_publication[0]) > len(headline_publication[1]):
				
				# check whether headline starts with cap
				if not headline_publication[0][0].isupper():
					continue

				one_email_data.append({
					"headline": headline_publication[0],
					"date": one_date,
					"publication": headline_publication[1]
					})
			else:

				# check whether headline starts with cap
				if not headline_publication[1][0].isupper():
					continue

				one_email_data.append({
					"headline": headline_publication[1],
					"date": one_date,
					"publication": headline_publication[0]
					})

	while(contains_duplicate_publishers(one_email_data) > -1):
		one_email_data.pop(contains_duplicate_publishers(one_email_data))

	email_data.extend(one_email_data)

print json.dumps(email_data, indent=4)
# check whether


with open("hilary-cleaned-2.csv", "w") as of:
	csvWriter = csv.DictWriter(of, fieldnames=["headline", "date", "publication"])
	csvWriter.writeheader()
	for email in email_data:
		csvWriter.writerow(email)


	# for one_day_headline in one_day_headlines:
	# 	# one_day_headline = one_day_headline.split("|")
	# 	print "================================="
	# 	print "haha"
	# 	print one_day_headline
	# 	print "================================="
	# lines = email.split("|")
	# print lines[0]