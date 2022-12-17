import obspython as obs
import urllib.request
import urllib.error
import json
import requests

url         = ""
interval    = 30
source_name = ""
outputIndex = 63  # Last index
currentFile = ""
tracker_active = False
stream_key	= ""

session = requests.Session()

# ------------------------------------------------------------

def update_audio():
	global url
	global interval
	global source_name
	global currentFile
	global tracker_active
	global stream_key

	source = obs.obs_get_source_by_name(source_name)
	

	if tracker_active:
		if source is not None:
			try:
				req = url + '/obs/audio/' + stream_key + '/'
				response = session.get(req)
				print(response.status_code)
				if response.status_code == 200:
					response_json = response.json()
					print(response_json)
					if 'file-name' in response_json:
						if currentFile != response_json['file-name']:
							if response_json['file-name'] == 'none':
								print('set new file ' + response_json['file-name'])
								currentFile = response_json['file-name']
								settings = obs.obs_data_create()
								obs.obs_data_set_string(settings, "local_file", "")
								obs.obs_source_update(source, settings)
								obs.obs_source_set_monitoring_type(source, obs.OBS_MONITORING_TYPE_MONITOR_AND_OUTPUT)
								obs.obs_set_output_source(outputIndex, source)
								currentFile = response_json['file-name']
								obs.obs_data_release(settings)
								obs.obs_source_media_stop(source)
							else:
								settings = obs.obs_data_create()
								obs.obs_data_set_string(settings, "local_file", script_path() + response_json['file-name'])
								obs.obs_source_update(source, settings)
								obs.obs_data_release(settings)
								obs.obs_source_set_monitoring_type(source, obs.OBS_MONITORING_TYPE_MONITOR_AND_OUTPUT)
								obs.obs_set_output_source(outputIndex, source)
								currentFile = response_json['file-name']


			except Exception as all_error:
				obs.script_log(str(obs.LOG_WARNING), "Common error" + str(all_error))
				# obs.remove_current_callback()
	else:
		settings = obs.obs_data_create()
		obs.obs_data_set_string(settings, "local_file", "")
		obs.obs_source_update(source, settings)
		obs.obs_data_release(settings)
		obs.obs_source_set_monitoring_type(source, obs.OBS_MONITORING_TYPE_MONITOR_AND_OUTPUT)
		obs.obs_set_output_source(outputIndex, source)
		obs.obs_source_media_stop(source)

	obs.obs_source_release(source)
	

def refresh_pressed(props, prop):
	update_audio()

# ------------------------------------------------------------

def script_description():
	return "Updates a text source to the text retrieved from a URL at every specified interval.\n\nBy Jim"

def script_update(settings):
	global url
	global interval
	global source_name
	global currentFile
	global tracker_active
	global stream_key

	url         = obs.obs_data_get_string(settings, "url")
	interval    = obs.obs_data_get_int(settings, "interval")
	source_name = obs.obs_data_get_string(settings, "source")
	tracker_active = obs.obs_data_get_bool(settings, "tracker_active")
	currentFile = ""
	stream_key	= obs.obs_data_get_string(settings, "stream_key")


	obs.timer_remove(update_audio)

	if url != "" and source_name != "":
		obs.timer_add(update_audio, interval * 1000)

def script_defaults(settings):
	obs.obs_data_set_default_int(settings, "interval", 30)
	obs.obs_data_set_default_bool(settings, "tracker_active", False)
	obs.obs_data_set_default_string(settings, "url", "http://localhost:8001")
	obs.obs_data_set_default_string(settings, "stream_key", "555")

def script_properties():
	props = obs.obs_properties_create()

	obs.obs_properties_add_bool(props, "tracker_active", "Activate tracker")
	obs.obs_properties_add_text(props, "url", "URL", obs.OBS_TEXT_DEFAULT)
	obs.obs_properties_add_text(props, "stream_key", "Stream key", obs.OBS_TEXT_DEFAULT)
	obs.obs_properties_add_int(props, "interval", "Update Interval (seconds)", 1, 3600, 1)

	p = obs.obs_properties_add_list(props, "source", "Media Source", obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)
	sources = obs.obs_enum_sources()
	if sources is not None:
		for source in sources:
			source_id = obs.obs_source_get_unversioned_id(source)
			if source_id == "ffmpeg_source":
				name = obs.obs_source_get_name(source)
				obs.obs_property_list_add_string(p, name, name)

		obs.source_list_release(sources)

	obs.obs_properties_add_button(props, "button", "Refresh", refresh_pressed)
	return props

def script_unload():
	obs.timer_remove(update_audio)
	source = obs.obs_get_source_by_name(source_name)
	if source is not None:
		settings = obs.obs_data_create()
		obs.obs_data_set_string(settings, "local_file", "")
		obs.obs_source_update(source, settings)
		obs.obs_data_release(settings)
		obs.obs_source_set_monitoring_type(source, obs.OBS_MONITORING_TYPE_MONITOR_AND_OUTPUT)
		obs.obs_set_output_source(outputIndex, source)
		obs.obs_source_media_stop(source)

	obs.obs_source_release(source)

# 	obs.obs_set_output_source(outputIndex, None)