import pandas as pd
from datetime import datetime
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

try:
    creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    )   
    client = gspread.authorize(creds)
except Exception as e:
    st.error(f"Authentication error: {e}")
    st.stop()

try:
    sheet = client.open("ELO").sheet1
except Exception as e:
    st.error(f"Error opening sheet: {e}")
    st.stop()


def protected_action(action_func, *args, password, ADMIN_PASSWORD, success_msg="Action completed!"):
    """
    Esegue action_func solo se la password è corretta.
    - action_func: funzione da eseguire
    - *args: argomenti da passare alla funzione
    - success_msg: messaggio visualizzato se l'azione va a buon fine
    """
    if password == ADMIN_PASSWORD:
        action_func(*args)
        st.success(f"✅ {success_msg}")
        return True
    else:
        st.error("❌ Incorrect password — action denied.")
        return False


def load_players():
    """
    Reads a Google Sheet with:
    - First column: player names
    - Last column: ELO rating
    Skips the first row (header).

    Returns: dictionary {name: rating}
    """
    # Read all values ​​from the sheet
    data = sheet.get_all_values()

    # Convert to DataFrame and skip the first row (header)
    df = pd.DataFrame(data[1:])

    # First column = names, last column = ELO
    names = df.iloc[:, 0]
    elo = df.iloc[:, -1]

    # Create the dictionary
    players_ranking = dict(zip(names, elo))

    # Remove NaN values and convert scores to float
    players_ranking = {
        str(k).strip(): float(v)
        for k, v in players_ranking.items()
        if pd.notna(v) and str(v).strip() != ""
    }

    return players_ranking


def input_check(order_list, players_dict):
    """
    Input is valid if:
    1. order_list contains at least 2 distinct elements
    2. all elements are keys from the players_dict dictionary
    3. there are no duplicates in the list
    """
    if len(order_list) != len(set(order_list)):
        return False
    if len(order_list) < 2:
        return False
    if not all(player in players_dict for player in order_list):
        return False
    return True



def update_ranking(order, k=32):
    """
    Update the Google Sheet by adding a new column with the updated ELO scores.
    In the first row of the new column, write the date and time of the update.
    Do not delete existing data.
    """
    n = len(order)
    players_ranking = load_players()
    new_ratings = players_ranking.copy()

    # Calculating expected scores
    expected = {}
    for i in range(n):
        e = 0
        for j in range(n):
            if i == j:
                continue
            e += 1 / (1 + 10 ** ((players_ranking[order[j]] - players_ranking[order[i]]) / 400))
        expected[order[i]] = e / (n - 1)

    # Actual score based on position (1 = first, n = last)
    actual = {p: (n - i - 1) / (n - 1) for i, p in enumerate(order)}

    # Updating scores
    for p in order:
        new_ratings[p] += int(k * (actual[p] - expected[p]))

    # Read all existing data
    data = sheet.get_all_values()

    # Convert to DataFrame for easier manipulation
    df_original = pd.DataFrame(data)
    df = df_original.iloc[1:].reset_index(drop=True)

    # Names of players in the first column
    names = df.iloc[:, 0].astype(str).str.strip()

    # Build the new column of updated scores
    new_column = []
    for name in names:
        if name in new_ratings:
            new_column.append(new_ratings[name])
        else:
            # If no new score exists, keep the last existing value
            new_column.append(df.iloc[names[names == name].index[0], -1])

    # Datetime of the update
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Update the first cell (timestamp)
    col_index = len(df_original.columns) + 1
    sheet.update_cell(1, col_index, timestamp)

    # Update the scores row by row (starting from the second row)
    for i, value in enumerate(new_column, start=2):
        sheet.update_cell(i, col_index, value)


def add_player(name):
    """
    Adds a new player to the Google Sheet.
    - The name is written in the first column at the bottom of the table.
    - 100 is written in all subsequent columns (one for each past match).
    """

    # Read all values ​​from the sheet
    data = sheet.get_all_values()

    # Count the total columns
    num_cols = len(data[0])
    new_row = [name] + [int(100)] * (num_cols - 1)

    # Append the row at the bottom
    sheet.append_row(new_row)


def remove_player(name):
    """
    Removes the indicated player from the Google Sheet.
    - Search for the name in the first column.
    - Deletes the entire corresponding row, leaving no blank lines.
    """

    # Get all rows from the sheet
    data = sheet.get_all_values()

    # Find the player's row in the first column
    player_row = None
    for i, row in enumerate(data[1:], start=2):
        if row and row[0].strip() == name.strip():
            player_row = i
            break

    if player_row is None:
        print(f"❌ Player '{name}' not found.")
        return

    # Delete the corresponding row
    sheet.delete_rows(player_row)