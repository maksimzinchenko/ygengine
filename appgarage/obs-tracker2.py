import obspython as obs
import requests
import urllib.request
import urllib.error
import json

tracker_active = False
url         = ""
interval    = 5
stream_key	= ""

session = requests.Session()

def update_text():
	global tracker_active
	global url
	global interval
	global stream_key

	if tracker_active:
		if url and stream_key:
			req = url + '/obs/stream/' + stream_key + '/'
			set_scene_name = 'S0_default'
			try:
				response = session.get(req)
				if response.status_code == 200:
					response_json = response.json()
					if response_json['found']:
						if response_json['active']:
							set_scene_name = response_json['currentScene']
						else:
							set_scene_name = 'S0_realstream_not_active'
							if response_json['finished']:
								set_scene_name = 'S0_realstream_finished'

				# check for update interval change
				# if int(response_json['updateInterval']) != int(interval):
				# 	# obs.script_log(obs.LOG_WARNING, "New interval got: " + str(response_json['updateInterval']))

				# 	interval = response_json['updateInterval']
				# 	obs.timer_remove(update_text)
				# 	obs.timer_add(update_text, interval * 1000)

				# 	settings = obs.obs_data_create()
				# 	obs.obs_data_set_int(settings, "interval", interval)
				# 	obs.obs_data_release(settings)
			
			# except urllib.error.URLError as err:
			# 	set_scene_name = 'S0_no_connection'

			except Exception as err:
				print(err)
				set_scene_name = 'S0_no_connection'

			try:
				all_scenes = obs.obs_frontend_get_scenes()
				for scene in all_scenes:
					scene_name = obs.obs_source_get_name(scene)
					if scene_name == set_scene_name:
						currentScene = obs.obs_frontend_get_current_scene()
						if scene != currentScene:
							print('change scene')
							obs.obs_frontend_set_current_scene(scene)
						obs.obs_source_release(currentScene)
				obs.source_list_release(all_scenes)
			except Exception as err:
				print('Error In scenes:')

			


def refresh_pressed(props, prop):
	update_text()

# ------------------------------------------------------------

def script_description():
	return "Get config retrieved from a URL at every specified interval."

def script_update(settings):
	global tracker_active
	global url
	global interval
	global stream_key

	tracker_active = obs.obs_data_get_bool(settings, "tracker_active")
	url         = obs.obs_data_get_string(settings, "url")
	stream_key	= obs.obs_data_get_string(settings, "stream_key")
	interval    = obs.obs_data_get_int(settings, "interval")
	

	obs.timer_remove(update_text)

	if url != "":
		obs.timer_add(update_text, interval * 1000)

def script_defaults(settings):
	obs.obs_data_set_default_int(settings, "interval", 5)
	obs.obs_data_set_default_bool(settings, "tracker_active", False)
	obs.obs_data_set_default_string(settings, "url", "http://localhost:8001")
	obs.obs_data_set_default_string(settings, "stream_key", "555")

def script_properties():
	props = obs.obs_properties_create()

	obs.obs_properties_add_bool(props, "tracker_active", "Activate tracker")
	obs.obs_properties_add_text(props, "url", "Engine host and port", obs.OBS_TEXT_DEFAULT)
	obs.obs_properties_add_text(props, "stream_key", "Stream key", obs.OBS_TEXT_DEFAULT)
	obs.obs_properties_add_int(props, "interval", "Update Interval (seconds)", 1, 3600, 1)
	obs.obs_properties_add_button(props, "button", "Refresh", refresh_pressed)

	return props

# def script_unload():
# 	obs.timer_remove(update_text)