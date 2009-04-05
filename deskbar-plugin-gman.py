#
# deskbar-plugin-gman.py: A plugin for the deskbar applet that searches 
# for MAN pages and displays them in Yelp (the GNOME documentation 
# viewer) 
#
# Author: Dimitris Lampridis <dlampridis_at_gmail.com>

# (C) Copyright 2009 Dimitris Lampridis
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import deskbar.interfaces.Action
import deskbar.interfaces.Match
import deskbar.core.Utils
import deskbar.interfaces.Module
import commands
import os.path

HANDLERS = ["GManPageModule"]

class GManPageAction(deskbar.interfaces.Action):
	
	def __init__(self, page):
		deskbar.interfaces.Action.__init__(self, page)

		pageinfo     = page.split(' ')
		pagename     = pageinfo[0].strip()
		pagesection  = pageinfo[1].strip()

		self._page = 'man:' + pagename + pagesection

	def activate(self, text=None):
		deskbar.core.Utils.spawn_async( [ '/usr/bin/yelp', self._page ] )
		
	def get_verb(self):
		return "View \"%(name)s\" MAN page"
		
	def get_icon(self):
		return "gtk-help"
		
		
class GManPageMatch (deskbar.interfaces.Match):
	
	def __init__(self, match, **kwargs):
		deskbar.interfaces.Match.__init__(self,
			name="match",
			icon="gtk-help", category="documents", **kwargs)
		self.match = match
		self.add_action( GManPageAction(self.match) )
		
	def get_hash(self):
		return self.match
		
class GManPageModule (deskbar.interfaces.Module):

	INFOS = {'icon': deskbar.core.Utils.load_icon("gtk-help"),
		'name': 'Man page search',
		'description': 'Search through available MAN pages',
		'version': '0.1.2.0',
		}
	
	def __init__(self):
		deskbar.interfaces.Module.__init__(self)
		
	def query(self, text):
		if len(text) > 1:
			if ( text[0] == '!' ) and (len(text) > 3):
				outputofwhatis = commands.getstatusoutput( 'whatis -r ' + text[1:] )
			else:
				outputofwhatis = commands.getstatusoutput( 'whatis -w ' + text + '*' )

			if outputofwhatis[1].endswith ( 'nothing appropriate.' ) is not True :
				for match in outputofwhatis[1].splitlines():
					self._emit_query_ready( text, [ GManPageMatch( match.split(' - ')[0].strip()) ] )

	@staticmethod
	def has_requirements():
		if os.path.isfile("/usr/bin/whatis"):
			if os.path.isfile("/usr/bin/yelp"):
				return True
			else:
				GManPageModule.INSTRUCTIONS = 'Cannot find "yelp" in /usr/bin. Please install the Yelp package first'
		else:
			GManPageModule.INSTRUCTIONS = 'Cannot find "whatis" in /usr/bin. Please install the MAN database (man-db package) first'
		return False
