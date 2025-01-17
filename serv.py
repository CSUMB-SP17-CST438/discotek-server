import flask
import flask_socketio
from flask_socketio import join_room, leave_room
from flask import request
import discoSounds as ds
import os
import json
import datetime
import requests
import facebook
import time
from song_update_service import *

import events, log
from schema import *

public_room = 912837
app = flask.Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL','postgresql://jcrzr:anchor99@localhost/postgres')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= 0

db.init_app(app)
socket = flask_socketio.SocketIO(app)
# default route
thread_holder = SongThreadHolder(socket)

@app.route('/')
def start():
	return flask.render_template('index.html')


# @socket.on(events.CONNECT)
# def on_connect():
# 	log.sock(events.CONNECT)

# adds a client to the public room


@socket.on('join room')
def on_join_room(data):
	sessionid = request.sid
	print("********************************************************joined room*************************************************************")
	join_room(public_room)

# should be called when connected to get a list of songs for the room
# will take a 'genre' as an arguement, so this needs to be passed in


@socket.on('get songs')
def on_get_songs(data):
	genre = data['genre']
	songs = ds.getSongList(genre)
	print("********************************************SONGLIST triggered******************************************************************")
	socket.emit('song list', songs, room=public_room)



#expects floor_id, and song_id as arguments.
#updates songlist with song_picked added as the next song in the playlist to be played.
@socket.on('song picked')
def on_song_picked(data):
	current_song = data['song']
	thread_holder.find_thread(data['floor_id']).update_list(current_song['id'])
	current_song['stream_url'] = stream_url_loc
	socket.emit('song to play', current_song, room=floor_id)


"""this listener is expecting key:pair list (i.e json) with either fb_t for facebook token, or google_t for google token
	if user exists, function will validate and pass back user information and auth status. else, it will add user reference to schema"""

@socket.on(events.LOGIN)
def on_login(data):
	log.sock(events.LOGIN)
	if 'fb_t' not in data:
		# print('google_t: ')
		# print(data)
		response = requests.get(
			'https://www.googleapis.com/oauth2/v3/tokeninfo?id_token=' + data['google_t'])
		json = response.json()
		# print(json)
		fname = json['given_name'] 
		lname = json['family_name']
		link = json['picture']
		email = json['email']
		mem_found = memberExists_by_email(email)
		# print(mem_found)
		if mem_found:
			mem = getMemberObject_by_email(email)
			log.emit(events.LOGIN_STATUS)
			socket.emit(events.LOGIN_STATUS, userEmit(mem), room=request.sid)
		else:
			new_mem = registerMember(fname,lname,email,link)
			log.emit(events.LOGIN_STATUS)
			socket.emit(events.LOGIN_STATUS, userEmit(new_mem), room=request.sid)

#
	if 'google_t' not in data:
		graph = facebook.GraphAPI(access_token=data['fb_t'],version='2.7')
		js = graph.get_object(id='me', fields='first_name,last_name,email,picture')
		print("js:",js)
		fname = js['first_name']
		lname = js['last_name']
		email = js['email']
		print("***************************EMAIL************************")
		link = js['picture']['data']['url']
		mem_found = memberExists_by_email(email)
		print(mem_found)
		if mem_found:
			mem = getMemberObject_by_email(email)
			log.emit(events.LOGIN_STATUS)
			socket.emit(events.LOGIN_STATUS, userEmit(mem), room=request.sid)
		else:
			new_mem = registerMember(fname,lname,email,link)
			log.emit(events.LOGIN_STATUS)
			socket.emit(events.LOGIN_STATUS, userEmit(new_mem), room=request.sid)


@socket.on(events.MESSAGE_SEND)
def on_new_message(data):
	log.sock(
		events.MESSAGE_SEND+"\n"+
		log.get_json(data)
	)
	floor_id = data['floor']
	member_id = data['from']
	text = data['message']

	add_message(floor_id, member_id, text)
	log.emit(events.MESSAGE_LIST_UPDATE)
	# print("floor messages", getFloorMessages(floor_id))
	socket.emit(events.MESSAGE_LIST_UPDATE, {
				'floor_messages': getFloorMessages(floor_id)}, room=floor_id)



#function will return floor list object after initializing the object
#the function should users associated with it. member_id and floorid 
#floor_name and a floor_genre
# @app.route('/floors')
@socket.on(events.GET_FLOOR_LIST)
def on_get_floor_list(data):
	log.sock(events.GET_FLOOR_LIST)
	log.emit(events.FLOOR_LIST_UPDATE)
	socket.emit(events.FLOOR_LIST_UPDATE, getPublicFloors())




#function assumes that the client sends
@socket.on('create floor')
def on_create(data):
	print("data: ",json.dumps(data,indent=4))
	if data['is_public'] == 1:
		public = True
	else:
		public = False
	print("******************join songlist message")
	flag, new_floor = add_floor(data['floor_name'],data['member_id'],public,data['floor_genre'])
	if flag == True:
		new_floor.add_member(data['member_id'])
		join_room(new_floor.floor_id)
		genre = data['floor_genre']
		songs = ds.getSongList(genre)
		thread_holder.add_thread(new_floor.floor_name,new_floor.floor_id,songs)
		time.sleep(2)
		new_floor.set_songlist(thread_holder.find_thread(new_floor.floor_id).songlist)
		updated_floor = getFloor(new_floor.floor_id)
		socket.emit('floor created', {'floor':updated_floor.to_list()},room=new_floor.floor_id)
		log.emit(events.FLOOR_LIST_UPDATE)
		socket.emit(events.FLOOR_LIST_UPDATE, getPublicFloors())
	else:
		socket.emit('error',{'message':new_floor})


@socket.on(events.JOIN_FLOOR)
#join room, function expects data to be json array/objects
# expects keys 'floor_id', 'member_id, returns jsonarray to parse
def on_join_floor(data):
	floor_id = data['floor_id']
	member_id = data['member_id']
	log.sock(events.JOIN_FLOOR+'\n'+
		log.get_mapf(data, log.BOLD, log.CYAN)
	)
	join_room(floor_id)
	floor_to_join = getFloor(floor_id)
	floor_to_join.add_member(member_id)
	# print(floor_to_join.to_list())
	#need to check if floor exists before creating thread.
	if thread_holder.find_thread(floor_id) is None:
		#create a new songlist update thread
		print("thread is none")
		floor_to_join = getFloor(floor_id)
		floor_list = floor_to_join.to_list()
		new_thread = thread_holder.add_thread(floor_to_join.floor_name,floor_to_join.floor_id,floor_list['songlist'])
		#refresh floor object
		time.sleep(2)
		floor_to_join.set_songlist(new_thread.songlist)
		floor_to_join = getFloor(floor_id)
		floor_list = floor_to_join.to_list()
		socket.emit('floor joined', {'floor':floor_list}, room=request.sid)
		# print("floor",json.dumps(floor_list[0:4],indent=4))
		# print("***memlist update***")
		# print(floor_to_join.to_list()['floor_members'])
		socket.emit('member list update', {'floor members': floor_list['floor_members']},room=floor_to_join.floor_id)

	else:
		print("thread is active")
		floor_to_join.set_songlist(thread_holder.find_thread(floor_to_join.floor_id).songlist)
		#refresh floor object after new songlist has been updated
		floor_to_join = getFloor(floor_id)
		print("****floor songlist***")
		floor_list = floor_to_join.to_list()
		# print(json.dumps(floor_list['songlist'][0:3],indent=4))
		socket.emit('floor joined', {'floor':floor_to_join.to_list()}, room=request.sid)
		# print("***memlist update***")
		# print(floor_list['floor_members'])
		socket.emit('member list update', {'floor members': floor_list['floor_members']},room=floor_to_join.floor_id)
		
@socket.on(events.LEAVE_FLOOR)
def on_leave_floor(data):
	log.sock(events.LEAVE_FLOOR)
	current_floor = getFloor(data['floor_id'])
	current_floor.rm_member(data['member_id'])
	current_floor = getFloor(data['floor_id'])
	leave_room(data['floor_id'])
	# socket.emit('member left', {'floor':current_floor.to_list()}, room=data['floor_id'])
	socket.emit('member list update', {'floor members': current_floor.to_list()['floor_members']},room=data['floor_id'])
	if not current_floor.isActive():
		current_floor.set_songlist(thread_holder.find_thread(current_floor.floor_id).songlist)
		thread_holder.update_thread_status(current_floor.floor_id,current_floor.isActive())

def userEmit(member):
	print(member.to_simple_list())
	return {'authorized': 1,'email': member.member_email,'member_id':member.member_id,'user':member.to_simple_list()}


###################################################################################################################################
###################################################################################################################################
#############################PROFILE UPDATE HANDLERS###############################################################################
@socket.on('get floor profiles')
def get_floor_profiles(data):
	floor = data['floor_id']
	
@socket.on(events.PROFILE_UPDATE)
def on_update_profile(data):
	# dt = data[0]
	print(data)
	me = update_profile(**data)
	print("updated user: ",me)
	for t in thread_holder.threads:
		fl = getFloor(t.floor_id)
		fl_id_found = None
		for m in fl.floor_members:
			if m.member_id == data['member_id']:
				print("found!")
				fl_id_found = fl.floor_id
				break
	if fl_id_found is not None:
		socket.emit('floor joined', {'floor':fl.to_list()}, room=request.sid)
		fl_list = fl.to_list()
		socket.emit('member list update', {'floor members': fl_list['floor_members']},room=fl.floor_id)
		
		
	socket.emit(events.PROFILE_UPDATED,me)
	
@socket.on(events.PING)
def on_ping(data):
	s_id = request.sid
	socket.emit(events.PONG, "keep me alive",room= s_id)

#This event is for the privacy policy page
@app.route('/privacy')
def privacy():
	return flask.render_template('privacy.html')

if __name__ == '__main__':
	socket.run(
		app,
		port=int(os.getenv('PORT', '8080')),
		host=os.getenv('IP', '0.0.0.0'),
		debug=True)

 # waht did you do yesterday?
 # what did you do toda?
 # what is the plan for today?
 # roadblocks?


#on login:
