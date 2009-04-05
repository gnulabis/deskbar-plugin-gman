import deskbar.interfaces.Action
import deskbar.interfaces.Match
import deskbar.core.Utils
import deskbar.interfaces.Module
import commands

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
		
	def is_valid(self, text=None):
		return 1
#		return (os.path.exists(self._pagepath) and os.path.isfile(self._pagepath))
		
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
		'version': '0.0.2.1',
		}
	
	def __init__(self):
		deskbar.interfaces.Module.__init__(self)
		
	def query(self, text):
		if len(text) > 1:
			outputofwhatis = commands.getstatusoutput( 'whatis -r ' + text )
			if outputofwhatis[1].endswith ( 'nothing appropriate.' ) is not True :
				for match in outputofwhatis[1].splitlines():
					self._emit_query_ready( text, [ GManPageMatch( match.split(' - ')[0].strip()) ] )

