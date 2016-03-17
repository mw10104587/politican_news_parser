I hunted around a fair bit looking for a way to convert Google Alerts into spreadsheet form, splitting the information into date, headline and publication name. I couldn’t find anything useful, so we decided to create one to help us analyze the data on the coverage of the U.S. Presidential race (hyperlink). There are probably easier ways to extract the data, but this is what worked for me.

Step 1: Set up an account with mailparser.io to extract the relevant information from each Alert. Set the parsing rules as follows;

Data source: ‘Body’ and ‘html’
Filters:
Replace and remove -> remove lines and entities -> remove link URL’s (removes all the URLS and only leaves behind core information we need)
Find start position -> Text match after ‘Daily’ (eliminates everything written before the word daily occurs
Define end position -> text match after ‘WEB’ (eliminates all articles from non-news sources)
Define end position -> text match after BLOG (eliminates all blog articles)
Replace and remove->Search and replace text -> search for ‘BLOG’ replace with (LEAVE BLANK SPACE). Do the same for ‘WEB’, ‘blogs’, ‘flag as irrelevant’, ‘full coverage’, ‘unsubscribe’  (basically cleans the information so only what we want is left behind)

Step 2: Forward all the emails to the mailparser address. There are some add-ons which allow you to mass forward emails, although Gmail imposes a limit of 100 mass forwards a day. 

Create a webhook and dispatch the emails with the rule created to appear in a Google spreadsheet. Name the first column ‘Headline’ (important to run the code successfully).

By this point, in your spreadsheet, each alert should occupy one cell, starting from ‘update-(date).

Step3: Run the following code on the data, downloaded as a csv file. Before running the code, Replace “Hillary Clinton - Sheet1.csv” with your file name and rename "hilary-cleaned-2.csv" to whatever you want to call your file.


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



And voila! You should have the data in a very pretty form, with the headline of each article followed by the date and outlet which published it.

Some limitations: Any news outlets which has more than 4 words is eliminated. In a few cases, we get the first line of the article and not the headline. To avoid these problems, along with variables in the type of sites the Alert chooses, I would recommend limiting the analyses to specific news outlets.

ProTip: If you’re doing a cross analysis through different Alerts, like analysing Hillary Clinton and Bernie Sanders, make sure that you remove instances where a headline appears twice. Some headlines show up in both Clinton’s alerts and in Bernie’s alerts. This spreadsheet add-on is great for removing double counting.

