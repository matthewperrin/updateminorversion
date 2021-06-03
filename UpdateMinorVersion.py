'''
Update Minor Version And Save

@author Matt P
@date 29-03-2019 01:28:08
@version 1.0.68
'''
from datetime import datetime
import sublime
import sublime_plugin
import re

# javascript
class UpdateMinorVersionCommand(sublime_plugin.TextCommand):
	def run(self, args):
		content = self.view.substr(sublime.Region(0, self.view.size()))

		# matches the first versioning occurance
		# format is as follows:
		#       const AS_VERSION = "1.2.3";
		# supports const | let | var
		# variabe name must end with _VERSION
		# version format must be dot decimal notation and can be a string or not
		matchObj = re.search('^((?:\s*const|let|var)\s+(?:[A-Z]+_VERSION)\s*=\s*["\'`]?(?:\d+(?:\.\d+)*\.)?)(\d+)(["\'`]?\s*;)$', content, re.U | re.M)

		if matchObj == None:
			return

		target_region = sublime.Region(matchObj.start() + len(matchObj.group(1)), matchObj.end())
		self.view.sel().clear()
		self.view.sel().add(target_region)

		self.view.run_command( "insert_snippet", { "contents": "%s%s" % (int(matchObj.group(2)) + 1, matchObj.group(3)) } )

# date in JSDocs
class UpdateDateCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		content = self.view.substr(sublime.Region(0, self.view.size()))
		matchObj = re.search('^([\s\*/]*)([@\\\\;]+\x20*date\s+)([\x20-\x7E]+)$', content, re.U | re.M)

		if matchObj == None:
			return

		target_region = sublime.Region(matchObj.start() + len(matchObj.group(1)), matchObj.end())
		self.view.sel().clear()
		self.view.sel().add(target_region)
		self.view.run_command( "insert", { "characters": "%s%s" % (matchObj.group(2), datetime.now().strftime("%d-%m-%Y %H:%M:%S")) } )

# version in JSDocs
class UpdateVersionCommand(sublime_plugin.TextCommand):
	def run(self, args):
		content = self.view.substr(sublime.Region(0, self.view.size()))

		matchObj = re.search('^([\s\*/]*(?:[@\\\\;]+\x20*)version\s+(?:\d+(?:\.\d+)*\.)?)(\d+)(\w*)$', content, re.U | re.M)

		if matchObj == None:
			return

		target_region = sublime.Region(matchObj.start() + len(matchObj.group(1)), matchObj.end())
		self.view.sel().clear()
		self.view.sel().add(target_region)

		self.view.run_command( "insert_snippet", { "contents": "%s%s" % (int(matchObj.group(2)) + 1, matchObj.group(3)) } )

class UpdateMinorVersionAndSaveCommand(sublime_plugin.WindowCommand):
	def run(self):
		# save a reference to the current view and its first selector (note that there could be multiple)
		view = self.window.active_view();
		regionList = []
		for sel in view.sel():
			regionList.append(sel)
		restorePosition = view.viewport_position()

		# run the desired TextCommand (s)
		self.window.run_command("update_minor_version")
		self.window.run_command("update_date")
		self.window.run_command("update_version")
		self.window.run_command("save")

		# restore the old view's first selector and viewport position :)
		view.sel().clear()
		for region in regionList:
			view.sel().add(region)
		view.set_viewport_position(restorePosition);