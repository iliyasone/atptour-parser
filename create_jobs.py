from tournament_traversal import Tournament,Tournaments

from typing import TypedDict, List, Dict, Any
import os

def create_download_jobs(data: Tournaments, existing_jobs) -> List[Dict[str, Any]]:
    jobs = []
    existing_links = {job['url'] for job in existing_jobs}

    for tournament in data["tournaments"]:
        
        for match in tournament["matches"]:
            # Similarly, parse 'match_id' from match["link"] or another field.
            link_parts = match["link"].strip("/").split("/")
            year = link_parts[7]
            tournament_id = link_parts[8]
            match_id = link_parts[9].upper()

            link_map = {
                "stroke-analysis": (
                    f"https://itp-atp-sls.infosys-platforms.com/"
                    f"static/prod/stroke-analysis/v2/{year}/{tournament_id}/{match_id}/data.json"
                ),
                "rally-analysis": (
                    f"https://itp-atp-sls.infosys-platforms.com/"
                    f"static/prod/rally-analysis/{year}/{tournament_id}/{match_id}/data.json"
                ),
                "match-beats": (
                    f"https://itp-atp-sls.infosys-platforms.com/"
                    f"static/prod/match-beats/{year}/{tournament_id}/{match_id}/data.json"
                ),
                "court-vision": (
                    f"https://itp-atp-sls.infosys-platforms.com/"
                    f"static/prod/court-vision/{year}/{tournament_id}/{match_id}/data.json"
                ),
                "stats-keystats": (
                    f"https://itp-atp-sls.infosys-platforms.com/"
                    f"static/prod/stats-plus/{year}/{tournament_id}/{match_id}/keystats.json"
                ),
                "stats-ytdstats": (
                    f"https://itp-atp-sls.infosys-platforms.com/"
                    f"static/prod/stats-plus/{year}/{tournament_id}/{match_id}/ytdstats.json"
                ),
                "complete": (
                    f"https://www.atptour.com/-/Hawkeye/"
                    f"MatchStats/Complete/{year}/{tournament_id}/{match_id}"
                )
            }

            for parsed_type, url in link_map.items():
                # Construct local filename: out/<year>/<tournament_id>/<match_id>/<parsed_type>.json
                local_path = os.path.join(
                    "out",
                    str(year),
                    tournament_id,
                    match_id,
                    f"{parsed_type}.json",
                )
                if url in existing_links:
                    continue

                job = {
                    "url": url,
                    "local_path": local_path,
                    "parsed_type": parsed_type,
                    "year": year,
                    "tournament_id": tournament_id,
                    "match_id": match_id,
                    "match": match,  # reference to the actual match object
                }
                jobs.append(job)

    return jobs




def main():
    import json

    with open('jobs.json') as f:
        current_jobs = json.load(f)

    with open('temp/traverse_temp.json') as f:
        tournaments = json.load(f)
    
        
    with open('jobs.json', 'w') as f:
        json.dump(current_jobs + create_download_jobs(tournaments, current_jobs),f, indent=4)


if __name__ == '__main__':
    main()

