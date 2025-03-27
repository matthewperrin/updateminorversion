'''
Update Minor Version And Save

@author Matt P
@date 19-12-2024 17:44:42
@version 2.1.3
'''
from datetime import datetime
import sublime
import sublime_plugin
import re
import logging
logging.basicConfig(level = logging.DEBUG, format = ' %(asctime)s - %(levelname)s - %(message)s')

class UpdateMinorVersionEventListener(sublime_plugin.EventListener):
	def on_pre_save(self, view):
		view.run_command("update_all")

# javascript
class UpdateMinorVersionCommand(sublime_plugin.TextCommand):
	def run(self, edit, **kwargs):
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

		self.view.run_command("insert_snippet", { "contents": "%s%s" % (int(matchObj.group(2)) + 1, matchObj.group(3)) } )

	def name(self):
		return "update_minor_version"

	def is_enabled(self, **kwargs):
		return True

	def is_visible(self, **kwargs):
		return True

	def is_checked(self, **kwargs):
		return False

	def description(self, **kwargs):
		return "Updates occurances of javascript variables (const, let, var, etc) with variable names ending in '_VERSION' using semantic versioning syntax"

# date in JSDocs
# this should let you add a comment with @date 19-12-2024 17:44:42
class UpdateDateCommand(sublime_plugin.TextCommand):
	def run(self, edit, **kwargs):
		lines = self.view.lines(sublime.Region(0, self.view.size()))

		for line in lines:
			text = self.view.substr(line)
			matchObj = re.search('(@date\s+)([\x200-9:-]+)$', text, re.U)

			if matchObj is not None:
				target_region = sublime.Region(line.begin() + matchObj.start() + len(matchObj.group(1)), line.begin() + matchObj.end())
				scopes = self.view.extract_tokens_with_scopes(target_region)

				if all("comment" in scope[1] for scope in scopes):
					self.view.sel().clear()
					self.view.sel().add(target_region)
					self.view.run_command( "insert", { "characters": datetime.now().strftime("%d-%m-%Y %H:%M:%S") } )

	def name(self):
		return "update_date"

	def is_enabled(self, **kwargs):
		return True

	def is_visible(self, **kwargs):
		return True

	def is_checked(self, **kwargs):
		return False

	def description(self, **kwargs):
		return "Updates occurances of jsdoc dates with the current timestamp"

# version in JSDocs
class UpdateVersionCommand(sublime_plugin.TextCommand):
	def run(self, edit, **kwargs):
		lines = self.view.lines(sublime.Region(0, self.view.size()))
		# extract_tokens_with_scopes

		for line in lines:
			text = self.view.substr(line)
			matchObj = re.search('(@version\s+(?:\d+(?:\.\d+)*\.)?)(\d+)(\w*)$', text, re.U)

			if matchObj is not None:
				target_region = sublime.Region(line.begin() + matchObj.start() + len(matchObj.group(1)), line.begin() + matchObj.end())
				scopes = self.view.extract_tokens_with_scopes(target_region)
				
				if all("comment" in scope[1] for scope in scopes):
					self.view.sel().clear()
					self.view.sel().add(target_region)
					self.view.run_command( "insert_snippet", { "contents": "%s%s" % (int(matchObj.group(2)) + 1, matchObj.group(3)) } )

	def name(self):
		return "update_version"

	def is_enabled(self, **kwargs):
		return True

	def is_visible(self, **kwargs):
		return True

	def is_checked(self, **kwargs):
		return False

	def description(self, **kwargs):
		return "Updates occurances of jsdoc versions with an incremented version number"

class UpdateMinorVersionAndSaveCommand(sublime_plugin.TextCommand):
	def run(self, edit, **kwargs):
		# save a reference to the current view and its first selector (note that there could be multiple)
		regionList = []
		for sel in self.view.sel():
			regionList.append(sel)
		restorePosition = self.view.viewport_position()

		self.view.run_command("update_minor_version")
		self.view.run_command("update_date")
		self.view.run_command("update_version")

		# restore the old view's first selector and viewport position :)
		self.view.sel().clear()
		for region in regionList:
			self.view.sel().add(region)
		self.view.set_viewport_position(restorePosition);

	def name(self):
		return "update_all"

	def is_enabled(self, **kwargs):
		return True

	def is_visible(self, **kwargs):
		return True

	def is_checked(self, **kwargs):
		return False

	def description(self, **kwargs):
		return "Runs all UMV commands in sequence"
