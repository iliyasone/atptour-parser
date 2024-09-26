import os
import traceback

from atptour import *
from matchbeats import *
from rally_analysis import *
from stroke_summary import *
from stats import *

from tournament_traversal import Tournaments, Parsed

required: Parsed = {
    'courtVision': False,
    'matchBeats': True,
    'rallyAnalysis': True,
    'stats': True,
    'strokeSummary': True
}

with open('traverse.json','r') as f:
    traverse: Tournaments = json.load(f)

try:
    for tournament in traverse['tournaments']:
        atLeastOneMatchSaved = False

        for match in tournament['matches']:
            isParsed = match['isParsed']

            run = []

            for needToParse in required:
                
                if not required[needToParse]:
                    continue # not required

                if isParsed[needToParse]:
                    continue # already parsed
                match needToParse:
                    case 'courtVision':
                        raise NotImplementedError
                    case 'matchBeats' as funcname:
                        run.append((parse_matchbeats, funcname))
                    case 'rallyAnalysis' as funcname:
                        run.append((parse_rally_analysis, funcname))
                    case 'stats' as funcname:
                        run.append((parse_stats, funcname))
                    case 'strokeSummary' as funcname:
                        run.append((parse_stroke_summary, funcname))
            if run:
                link = match['link']
                *_, year, tournament_id, match_id = link.split('/')
                safe_get(match['link'])

                path = '/'.join([year, tournament_id, match_id])
                os.makedirs(path, exist_ok=True)

            for func, funcname in run:
                with open(path + '/' + funcname +'.json', 
                        mode='w') as f:
                    try:
                        data = func()
                    except (WebDriverException, Exception) as er:
                        logger.error(f'{er.__class__} error for {funcname} {match_id} {tournament_id}: {er}. Trying again...')
                        time.sleep(5)
                        try:
                            data = func()
                            logger.info('no error, OK')
                        except (WebDriverException, Exception) as er:
                            logger.error('Error repeated:', exc_info=True)
                            continue
                    logger.info(f'{funcname} for {tournament_id}/{match_id} saved')
                    json.dump(data, f, indent=4)
                isParsed[funcname] = True

            
            if run:
                with open(path + '/match.json', mode='w') as f:
                    json.dump(match, f, indent=4)

            atLeastOneMatchSaved = True
        if atLeastOneMatchSaved:
            with open('/'.join([year, tournament_id]) + '/tournament.json',mode='w') as f:
                json.dump(tournament, f, indent=4)
except (Exception, KeyboardInterrupt):
    with open('traverse.json', 'w') as f:
        json.dump(traverse, f, indent=4)
    raise