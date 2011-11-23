import os, datetime

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

  def update(self, metadata, media, lang, force):
    "Grabs all the information about the show and episodes"
    Log("Starting Update")

    metadata.title = "TEST TITLE"
    metadata.summary = "THIS IS A SUMMARY"
    @parallelize
    def UpdateEpisodes():
      # Full list of media parts...
      for s in media.seasons:
         Log("Season: "+ s)
         for e in media.seasons[s].episodes:
           Log("  Episode: " + e)
           for i in media.seasons[s].episodes[e].items:
             Log("    Item: " + str(i))
             for part in i.parts:
               Log("       Part: " + part.file)
               filename = part.file.decode('utf-8')
               nfoFile=os.path.splitext(filename)[0]+".nfo"
              
               episode = metadata.seasons[s].episodes[e]
               
               # Create a task for updating this episode
               @task
               def UpdateEpisode(episode=episode):
                 episode.title = "TEST"
                 episode.summary = "XXX"
                 episode.rating = 50.
                 episode.originally_available_at = datetime.date.today()

    # More stuff
    