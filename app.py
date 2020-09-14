#DaVonte' Whitfield 9/12/2020
#Tech Degree project 5 My Journal
#Python 3.7
#requirements.txt 

import datetime
import json

from flask import (Flask, render_template, 
		flash, redirect, url_for, 
		abort, request, make_response)
from peewee import *



#Flask---------------------------------------------------

DEBUG = True
PORT = 8000
#HOST = '0.0.0.0' This doesn't work in Visual Studios, by default for me, it's 127.0.0.1

app = Flask(__name__)
app.secret_key = 'auoesh.bouoastuh.4'

#Flask---------------------------------------------------


#Datebase------------------------------------------------

db = SqliteDatabase('journal.db')

class Journal(Model):

	Id = PrimaryKeyField(unique =True) 
	Title = CharField(max_length = 255)
	Date = DateField()
	TimeSpent = IntegerField(default = 0)
	WhatILearned = TextField()
	Resources = TextField()

	class Meta:
		database = db

def initialize():

	#Create the database
	db.connect()
	db.create_tables([Journal], safe = True)

#Datebase------------------------------------------------


#Functions---------------------------------------------------

def get_saved_data():
    try:
        data = json.loads(request.cookies.get('entry'))

    except TypeError:
       data = {}

    return data

def get_max_item_count():
	count = 0

	max_loop_count = Journal.select()

	for items in max_loop_count: #Counting each item stored
		count += 1

	return count

#Functions----------------------------------------------------


#Routes------------------------------------------------

@app.route('/save', methods=['POST']) #Runs after submiting a new entry
def save():
	response = make_response()
	data = get_saved_data()
	data.update(dict(request.form.items()))
	response.set_cookie('entry', json.dumps(data))

	boolcheck = True #For while loop
	num = 1
	
	try:
		Journal.create(#Using 'data' info to create in entry in database
			Id = num,
			Title = data['Title'],
			Date = data ['Date'],
			TimeSpent = data['TimeSpent'],
			WhatILearned = data['WhatILearned'],
			Resources = data['Resources'])

	except IntegrityError: #If exist, go to the next row
		while boolcheck:
			
			try:
				num += 1
				Id = num
				Journal.create(Id = Id,
					   Title = data['Title'],
					   Date = data['Date'],
					   TimeSpent = data['TimeSpent'],
					   WhatILearned = data['WhatILearned'],
					   Resources = data['Resources'])

				boolcheck = False #once entered into a row, leave the while loop

			except IntegrityError: #if that row has something also, try the next row. 
				continue # continue until an empty shows

	entry = Journal.get(Id = num)#Get the entry that was just added to the database

	response = make_response(redirect(url_for('detail', Id = entry.Id, )))

	return response


@app.route('/save_edit/<int:Id_position>', methods = ['POST'])
def save_edit(Id_position): #different from normal save. This is saving edits

	response = make_response()
	data = get_saved_data()
	data.update(dict(request.form.items()))

	#Getting the position of the edit entry and adding in the new data
	entry = Journal.select().where(Journal.Id == Id_position).get()

	entry.Title = data['Title']
	entry.Date = data['Date']
	entry.TimeSpent = data['TimeSpent']
	entry.WhatILearned = data['WhatILearned']
	entry.Resources = data['Resources']
	entry.save()

	response = make_response(redirect(url_for('detail', Id = Id_position, )))
	return response


@app.route('/') # Homepage
@app.route('/entries')
def index():

	stream_entries = Journal.select().limit(4) #This will only show 4 links max

	return render_template('index.html', stream_entries = stream_entries)


@app.route('/entries/new', methods = ('GET', 'POST')) #this renders the new entry html page
def new_entry(): 
	return render_template('new.html')


@app.route('/entries/<int:Id>')
def detail(Id):

	entries = Journal.select().where(Journal.Id == Id).get() #This gets the Id of the received 'Id'
	check = Journal.select().where(Journal.Id == Id) #This is a checker

	if check.count() == 0:
		abort(404)

	return render_template('detail.html', entry = entries)


@app.route('/entries/<int:Id>/edit')
def edit_entry(Id):

	entries = Journal.select().where(Journal.Id == Id).get() #This gets the Id of the received 'Id'
	check = Journal.select().where(Journal.Id == Id) #This is a checker

	if check.count() == 0:
		abort(404)

	return render_template('edit.html', editing=entries)


@app.route('/entries/<int:Id_position>/delete')
def delete_entry(Id_position):
	
	boolcheck = True # For while loop
	
	Journal.get(Id_position).delete_instance() #This will delete the entry at the Id position
	
	counter = 1 #This is for the 'for loop'. This is not 0 because there's no ID position that's 0

	number_of_items = get_max_item_count() #Gets the max amount of entries in the database

	while(boolcheck):
		for item in Journal.select(): # looks through the entries
			if item.Id == counter: #if the counter is the same number as the item's ID, continue
				counter += 1
				continue

			#If they're not the same and the counter less than the max amount of items
			elif item.Id != counter and counter <= number_of_items: 
				entry = Journal.get(item.Id) #Get the item's position and its' data

				Journal.create(Id = counter, #Create a new entry in the spot of the deleted entry
								Title = entry.Title,
								Date = entry.Date,
								TimeSpent = entry.TimeSpent,
								WhatILearned = entry.WhatILearned,
								Resources = entry.Resources)

				#At this point, you have two entries with the same data.
				#This deletes the one that out of place
				Journal.get( item.Id ).delete_instance()
				counter = 1 #resetting counter to 1

				break #Break the 'for loop' to restart its loop to find other out of place entries properly

			else: #This run when all numbers have been check and will exit the 'for' and 'while' loop
				boolcheck = False
				break
				
	response = make_response(redirect(url_for('index')))#Back to the homepage
	return response

#Routes------------------------------------------------


#Main------------------------------------------------------------------------------
if __name__ == '__main__':
	initialize() #Databse

	try: # Whenever the program runs for the first time, this entry will always be entered

		Journal.create(
				Id = 1,
				Title = "Games are great",
				Date = datetime.datetime.strptime('9/6/2020', '%m/%d/%Y'),
				TimeSpent = 5,
				WhatILearned = 'How to play the game',
				Resources = 'Xbox and PC')

	except IntegrityError: # If something there in the database, skip this entry
		pass

	#For me, Visual Studios didn't allow 'host= 0.0.0.0'. by default it was 127.0.0.1
	app.run(debug = DEBUG, port = PORT) #might have to change this for yourself when running.
