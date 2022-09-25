from time import time
import datetime
from werkzeug.security import check_password_hash
from flask import request
import os
from app import app

class ServiceProvider:
	def __init__(self,dbcontext):
		self.dbcontext = dbcontext
	# Custom validation 
	# method that wraps the validate_on_submit() method of the form 
	# and removes the check of cs_token due to (me not able to figure out how to get it to work)
	def submit_form_validation(self,form):
		form.validate_on_submit() # will list the errors in the form
		errs = form.errors 
		if len(errs) == 0 or ("csrf_token" in errs and len(errs) == 1):
			return True
		else:
			return False

	def register_account(self,formclass):
		flash = None
		success = False
		submitted = False
		if formclass.register.is_submitted() and formclass.register.submit.data and self.submit_form_validation(formclass.register):
			submitted = True
			user = self.dbcontext.retrieve_user(formclass.register.username.data)
			if user != None:
				flash = 'Username is already taken!'
			else:
				self.dbcontext.insert_user(formclass.register)
				flash = f'account {formclass.register.username.data} was successfully created'
				success = True
		return flash,success,submitted

	def login_account(self,formclass):
		flash = None
		success = False
		submitted = False

		if formclass.login.is_submitted() and formclass.login.submit.data and self.submit_form_validation(formclass.login):
			submitted = True
			user = self.dbcontext.retrieve_user(formclass.register.username.data)
			# Could not find user
			if user == None:
				flash = 'Wrong username or password!'
			else:
				# Calculate the time left until the user can login again
				if user["login_timeout"] == None:
					time_left = 0
				else:
					lockout_stamp = user["login_timeout"]
					time_left = lockout_stamp - round(time.time())
					minutes = round(time_left//60)
					seconds = round(time_left%60)

				# Restore the login_attemps and login_timeout when the time is over
				if time_left <= 0 and user["login_timeout"] != None:
					self.dbcontext.reset_login_attempts(self,user)
					user = self.dbcontext.retrieve_user(user["username"])
				elif time_left > 0:
					flash = f'{minutes} min {seconds} sec until you can login again!'
				
				# User successfully logged in
				if user["login_timeout"] is None and check_password_hash(user['password'], formclass.login.password.data):
					# Reset the login_attemps and login_timeout
					self.dbcontext.reset_login_attempts(self,user)
					flash = "Successfully logged in"
					success = True

				# Logic for setting login_attempts and login_timeout
				elif not check_password_hash(user["Password"], formclass.login.password.data):
					
					if user["Login_attempts"] < 2:
						self.dbcontext.increment_login_attempts(user)
						flash = 'Wrong username or password!'

					elif user["Login_attempts"] == 2:
						lockout_time = 5 # minutes
						lockout_stamp = time.time() + lockout_time*60 # minutes
						self.dbcontext.set_login_timeout(user,lockout_stamp)
						flash = f'You have been locked out of your account for {lockout_time} minutes due to too many failed login attempts'
				#_________________________________
				else:
					flash = 'Wrong username or password!'
	
		return flash,success,submitted
			

	def stream_form(self,form,username):
		flash = None
		success = False
		submitted = False
		maxPosts = 200 # number of posts before you cannot post anymore until the next day
		user = self.dbcontext.retrieve_user(username)

		# if the user is not logged in or doesn't exist, don't redirect them
		coockieUsername = request.cookies.get("username")
		if coockieUsername != username or user == None:
			return flash,success,submitted

		if form.is_submitted() and form.submit.data and self.submit_form_validation(form):
			submitted = True

			# Calculate the time left until the user can post on stream again
			if user["stream_timeout"] == None:
				time_left = 0
			else:
				lockout_stamp =  user["stream_timeout"]
				time_left = round(lockout_stamp - time.time())
				hours = time_left // 3600
				min = (time_left % 3600) // 60
				sec = time_left % 60

			# Restore the stream_attemps and stream_timeout when the time is over
			if time_left <= 0 and user["stream_timeout"] != None:
				self.dbcontext.reset_stream_attempts(self,user)
				user = self.dbcontext.retrieve_user(username)
			
			# flash that the user has hit the daily post limit
			elif time_left > 0:
				flash = f'You have hit your daily limit of {maxPosts} posts. {hours} h {min} min {sec} sec until you can post on stream again!'
				return flash,success,submitted
				

			# Logic for setting stream_posts and stream_timeout
			if user["stream_posts"] < (maxPosts-1):
				self.dbcontext.increment_stream_posts(user)
				flash = f'You have {maxPosts - (user["stream_posts"]+1)} posts left today'
		
			elif user["stream_posts"] == (maxPosts-1):
				now = datetime.datetime.now()
				tomorrow = now + datetime.timedelta(days=1)
				lockout_date = datetime.datetime.combine(tomorrow, datetime.time.min) - now
				lockout_stamp = time.time() + lockout_date.total_seconds()
				time_left = round(lockout_stamp - time.time())
			
				hours = time_left // 3600
				min = (time_left % 3600) // 60
				sec = time_left % 60
				flash = f'You have hit your daily limit of {maxPosts} posts. {hours} h {min} min {sec} sec until you can post on stream again!'
				self.dbcontext.set_stream_timeout(user,lockout_stamp)
			#_________________________________

			success = self.dbcontext.insert_post(user,form)
			if success and form.image.data:
				path = os.path.join(app.config['UPLOAD_PATH'], form.image.data.filename)
				form.image.data.save(path)
			elif not success:
				flash = 'You must enter some content or upload an image'

		posts = self.dbcontext.retrieve_stream_posts()
		return flash,success,submitted,posts


				
					
			