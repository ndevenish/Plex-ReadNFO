import os, datetime
import dateutil.parser
import textwrap

def Start():
  pass

class ReadNfoAgent(Agent.TV_Shows):

  name = 'Read NFO Agent'
  languages = [Locale.Language.English]
  primary_provider = True
  accepts_from = None
  contributes_to = ["com.plexapp.agents.none",]
    
  def search(self, results, media, lang, manual):
    "Gives a list of possible matches to the detected automatic metadata"
    Log("Starting Search")
    Log(media.show)
    Log(media.id)
    results.Append(MetadataSearchResult(id=media.id,name=media.show,lang=lang,score=100))

  def UpdateShowMetadata(self, metadata, showNfo):
    """Updates show metadata, from an NFO filename"""
    nfoText = Core.storage.load(showNfo)

    #likely an xbmc nfo file
    nfoXML = XML.ElementFromString(nfoText).xpath('//tvshow')[0]

    #title
    try: metadata.title = nfoXML.xpath("./title")[0].text
    except: pass
    #summary
    try: metadata.summary = nfoXML.xpath('./plot')[0].text
    except: pass            

    thumb = os.path.join(os.path.dirname(showNfo), "poster.jpg")
    Log(thumb)
    data = Core.storage.load(thumb)
    metadata.posters["poster"] = Proxy.Media(data)
    
  def update(self, metadata, media, lang, force):
    "Grabs all the information about the show and episodes"
    Log("Starting Update")

    # Work out the base place for the 'series'
    # basedir = os.path.basedir(media.seasons[media.seasons.keys()[0]])
    # Get the first available episode, and get the filename
    anEp = media.seasons.itervalues().next().episodes.itervalues().next()
    aFile = anEp.items[0].parts[0].file
    Log("Using: " + str(aFile))
    baseDir = os.path.dirname(aFile)
    showNfo = os.path.join(baseDir, "tvshow.nfo")
    Log("Reading NFO: " + showNfo)
    
    self.UpdateShowMetadata(metadata, showNfo)

    @parallelize
    def UpdateEpisodes():
      # Full list of media parts...
      for s in media.seasons:
         Log("Season: "+ s)
         # Log(dir(media.seasons[s]))
         for e in media.seasons[s].episodes:
           Log("  Episode: " + e)
           for i in media.seasons[s].episodes[e].items:
             # Log("    Item: " + str(i))
             # for part in i.parts:
             #   Log("       Part: " + part.file)
             #   filename = part.file.decode('utf-8')
             #   nfoFile=os.path.splitext(filename)[0]+".nfo"
              
             filename = i.parts[0].file.decode('utf-8')
             nfoFile=os.path.splitext(filename)[0]+".nfo"
             Log("    nfo: " + nfoFile)
             episode = metadata.seasons[s].episodes[e]
             # episode.nfoFile = nfoFile
             # Create a task for updating this episode
             @task
             def UpdateEpisode(episode=episode, nfo=nfoFile):
                Log("Updating from: " + nfo)
                nfoText = Core.storage.load(nfo)
                # Log("Got nfo: " + nfoText)

                #likely an xbmc nfo file
                Log("X: " + nfo)
                nfoXML = XML.ElementFromString(nfoText).xpath('//episodedetails')[0]

                #title
                try: episode.title = nfoXML.xpath("./title")[0].text
                except: pass
                #summary
                try:
                  summary = nfoXML.xpath('./plot')[0].text
                  # Log(summary)
                  # episode.summary = textwrap.dedent(summary)
                  # Strip off any leading line whitespace
                  episode.summary = '\n'.join([x.strip() for x in summary.split('\n')])
                  # Log("ES: " + repr(episode.summary))
                except: pass            
                #year
                try: episode.originally_available_at = dateutil.parser.parse(nfoXML.xpath("./aired")[0].text).date()
                except: pass
                
                try:
                  thumbnail = nfoXML.xpath('./thumbnail')[0].text
                  fullPath = os.path.join(os.path.dirname(nfo), thumbnail)
                  Log("Thumbnail is: " + fullPath)
                  # Log("Base: " + os.path.dirname(nfo))
                  # Log("All: " + fullPath)
                  # Log(type(fullPath))
                  data = Core.storage.load(fullPath)
                  episode.thumbs[thumbnail] = Proxy.Media(data)
                except: pass            
                
                #content rating
                # try: episode.content_rating = nfoXML.xpath('./mpaa')[0].text
                # except: pass
                #studio
                # try: episode.studio = nfoXML.findall("studio")[0].text
                # except: pass
                #airdate
                # try: episode.duration = nfoXML.findall("aired")[0].text
                # except: pass
                
                # Log(nfoXML.xpath("./aired")[0].text)
                Log("Title: " + episode.title)
                #     Log(episode.originally_available_at)
                #                               # 
                              # 
                              # episode.title = "TEST"
                              # episode.summary = "XXX"
                              # episode.rating = 50.
                              # episode.originally_available_at = datetime.date.today()
               
    # More stuff
    