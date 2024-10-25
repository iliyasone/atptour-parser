import json
from rich.console import Console
from rich.table import Table
import requests
from config import TELEGRAM_TOKEN, CHAT_ID

def send_to_telegram(text):
    
    # Telegram API URL
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    # Data payload
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"  # Use "Markdown" or "HTML" to format text
    }
    # Send the POST request to Telegram
    response = requests.post(url, data=payload)
    return response.json()


def get_table(data):

    # Variables to keep track of statistics
    total_tournaments = len(data["tournaments"])
    total_matches = 0
    parsed_fields = {"courtVision": 0, "matchBeats": 0, "rallyAnalysis": 0, "stats": 0, "strokeSummary": 0}
    total_fields = len(parsed_fields)

    # Iterate over the tournaments and matches to gather stats
    for tournament in data["tournaments"]:
        matches = tournament["matches"]
        total_matches += len(matches)
        for match in matches:
            for field in parsed_fields.keys():
                if match["isParsed"].get(field, False):
                    parsed_fields[field] += 1

    # Calculate percentages
    def percentage(part, whole):
        return 100 * float(part)/float(whole)

    # Create a table for output
    table = Table(title="Tournaments and Matches Analytics", show_header=True, header_style="bold magenta")

    # Add columns
    table.add_column("Category", style="dim", width=30)
    table.add_column("Count", justify="right")
    table.add_column("Percentage", justify="right")

    # Populate table with data
    table.add_row("Total Tournaments", str(total_tournaments), "")
    table.add_row("Total Matches", str(total_matches), "")
    for field, count in parsed_fields.items():
        table.add_row(f"{field} Parsed", str(count), f"{percentage(count, total_matches):.2f}%")

    return table


def log_status(data):    
    console = Console(color_system=None, no_color=True)
    # Print the table in color
    with console.capture() as capture:
        console.print(get_table(data), )
    send_to_telegram(f'```{capture.get()}```')

def main():
    # Load the data from your JSON file
    with open("temp/traverse.json", "r") as f:
        data = json.load(f)
    log_status(data)


if __name__ == '__main__':
    main()