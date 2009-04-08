#
# deskbar-plugin-gman.py: A plugin for the deskbar applet that searches 
# for MAN pages and displays them in Yelp (the GNOME documentation 
# viewer) 
#
# Author: Dimitris Lampridis <dlampridis_at_gmail.com>
#
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
#

# You should not change anything below this line under normal circumnstances
# (unless you are here to code, in which case, be my guest!)
import deskbar.interfaces.Action
import deskbar.interfaces.Match
import deskbar.core.Utils
import deskbar.interfaces.Module
import commands
import gtk
import os
from os.path import *
from ConfigParser import RawConfigParser

# Names of external binaries
WHATIS      = 'whatis'
YELP        = 'yelp'

# Location of configuration file for the G-Man plugin
GMAN_CONFIG_DIR = expanduser ('~/.config/deskbar-applet')
GMAN_CONFIG_DIR_PERMISSIONS = 0755
GMAN_CONFIG_FILE = 'deskbar-plugin-gman.conf'
GMAN_CONFIG = join (GMAN_CONFIG_DIR, GMAN_CONFIG_FILE)

# Default configuration values
GMAN_DEFAULT_RESULTLIMIT = "20"
GMAN_DEFAULT_SEARCHCHAR = "!"

NAME        = "G-Man"
DESCRIPTION = "Search through available MAN pages"
VERSION     = "0.6.0"

HANDLERS = ["GManPageModule"]

class GManPageAction(deskbar.interfaces.Action):
	
	def __init__(self, page):
		deskbar.interfaces.Action.__init__(self, page)

		pageinfo     = page.split(' ')
		pagename     = pageinfo[0].strip()
		pagesection  = pageinfo[1].strip()

		self._page = 'man:' + pagename + pagesection

	def activate(self, text=None):
		deskbar.core.Utils.spawn_async( [ YELP, self._page ] )
		
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
		'name': NAME,
		'description': DESCRIPTION, 
		'version': VERSION,
		}
	
	def __init__(self):
		deskbar.interfaces.Module.__init__(self)

		config = self.read_cfg ()
		self.resultlimit =  config.getint('Preferences', 'resultlimit')
		self.searchchar = config.get('Preferences', 'searchchar')


	def query(self, text):
		if len(text) > 1:
			if ( text[0] == self.searchchar ) and (len(text) > 2):
				outputofwhatis = commands.getstatusoutput( WHATIS + ' -r ' + text[1:] )
			else:
				outputofwhatis = commands.getstatusoutput( WHATIS + ' -w ' + text + '*' )

			if outputofwhatis[1].endswith ( 'nothing appropriate.' ) is not True :
				if len(outputofwhatis[1].splitlines()) > self.resultlimit:
					results = outputofwhatis[1].splitlines()[:self.resultlimit]
				else:
					results = outputofwhatis[1].splitlines()

				for match in results:
					self._emit_query_ready( text, [ GManPageMatch( match.split(' - ')[0].strip()) ] )

	def has_config(self):
		return True

	def show_config(self, parent):
		GManConfigDialog = gtk.Dialog ( NAME + " config", parent,
						gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
						( gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
						  gtk.STOCK_OK, gtk.RESPONSE_OK ) )
		
		GManWidgetMaxResults = gtk.HBox ()
		GManWidgetMaxResultsSpin = gtk.SpinButton ()
		GManWidgetMaxResultsSpin.set_range (1, 50)
		GManWidgetMaxResultsSpin.set_increments (1,10)
		GManWidgetMaxResultsSpin.show()
		GManWidgetMaxResults.add ( GManWidgetMaxResultsSpin )
		GManWidgetMaxResultsLabel = gtk.Label('max results')
		GManWidgetMaxResultsLabel.show()
		GManWidgetMaxResults.add ( GManWidgetMaxResultsLabel )
		GManWidgetMaxResults.show()
		GManConfigDialog.vbox.add ( GManWidgetMaxResults )

		GManWidgetSubStringSearch = gtk.HBox ()
		GManWidgetSubStringSearchEntry = gtk.Entry (3)
		GManWidgetSubStringSearchEntry.set_text ('!' )
		GManWidgetSubStringSearchEntry.show()
		GManWidgetSubStringSearch.add ( GManWidgetSubStringSearchEntry )
		GManWidgetSubStringSearchLabel = gtk.Label('Substring search prefix')
		GManWidgetSubStringSearchLabel.show()
		GManWidgetSubStringSearch.add ( GManWidgetSubStringSearchLabel )
		GManWidgetSubStringSearch.show()
		GManConfigDialog.vbox.add ( GManWidgetSubStringSearch )

		GManWidgetWhatisLocationLabel = gtk.Label('absolute path to "whatis" binary:')
		GManWidgetWhatisLocationLabel.show()
		GManConfigDialog.vbox.add ( GManWidgetWhatisLocationLabel )

		GManWidgetWhatisLocation = gtk.Entry(20)
		GManWidgetWhatisLocation.set_has_frame = True
		GManWidgetWhatisLocation.set_text ('/usr/bin/whatis' )
		GManWidgetWhatisLocation.show()
		GManConfigDialog.vbox.add ( GManWidgetWhatisLocation )

		GManWidgetYelpLocationLabel = gtk.Label('absolute path to "yelp" binary:')
		GManWidgetYelpLocationLabel.show()
		GManConfigDialog.vbox.add ( GManWidgetYelpLocationLabel )

		GManWidgetYelpLocation = gtk.Entry(20)
		GManWidgetYelpLocation.set_has_frame = True
		GManWidgetYelpLocation.set_text ('/usr/bin/yelp')
		GManWidgetYelpLocation.show()
		GManConfigDialog.vbox.add ( GManWidgetYelpLocation )

		GManConfigDialogReturn = GManConfigDialog.run()
		GManConfigDialog.destroy()

		
	@staticmethod	
	def read_cfg ():
		config = RawConfigParser()
		CreateConfig = False

		if exists ( GMAN_CONFIG ):
			cfgfile = open ( GMAN_CONFIG, 'r' )
			config.readfp (cfgfile)
			cfgfile.close ()
			if not ( config.has_section('Preferences') and
				 config.has_option('Preferences', 'resultlimit') and
				 config.has_option('Preferences', 'searchchar') ):
				for section in config.sections():
					config.remove_section (section)
				CreateConfig = True

		else:
			if not exists (GMAN_CONFIG_DIR):
				os.mkdir (GMAN_CONFIG_DIR, GMAN_CONFIG_DIR_PERMISSIONS)
			CreateConfig = True

		if CreateConfig:
			config.add_section ('Preferences')
			config.set('Preferences', 'resultlimit', GMAN_DEFAULT_RESULTLIMIT)
			config.set('Preferences', 'searchchar', GMAN_DEFAULT_SEARCHBAR)
			cfgfile = open ( GMAN_CONFIG, 'w' )
			config.write (cfgfile)
			cfgfile.close ()

		return config	


	@staticmethod
	def has_requirements():
		if deskbar.core.Utils.is_program_in_path (WHATIS):
			if deskbar.core.Utils.is_program_in_path (YELP):
				return True
			else:
				GManPageModule.INSTRUCTIONS = 'Cannot find "' + YELP + '". Please install the Yelp package first'
		else:
			GManPageModule.INSTRUCTIONS = 'Cannot find "' + WHATIS + '". Please install the MAN database (man-db package) first'
		return False
