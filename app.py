import streamlit as st
import re
from elo_utils import load_players, update_ranking, add_player, remove_player, protected_action, input_check

st.set_page_config(page_title="ELO system", page_icon="🏆")

st.title("🏆 ELO system for games")
st.write("This application tracks players' ELO ratings over time. ",
         "Each match automatically updates the ranking based on the order in which participants finish.")
st.write("")
st.write("")

# Load players and display current ranking
st.subheader("📊 Current ELO ranking overview")
ranking_placeholder = st.empty()
all_players_ranking = load_players()
ranking_placeholder.subheader("Current ranking")
ranking_placeholder.write(all_players_ranking)

# Password protection
st.subheader("🔑 Admin access — management and updates")
ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]
password = st.text_input("Enter admin password", type="password")


# Update ranking
st.subheader("🏁 Update ranking after a match")
input_order = st.text_input(
    "Enter players in order of placement separated by a comma (e.g. AlbiAma, FraPava, GioDeldu, ...)"
)
order = [x.strip() for x in input_order.split(",") if x.strip()]

if st.button("Update ranking"):
    if not input_check(order, all_players_ranking):
        st.error("❌ Invalid input. " \
        "Please ensure at least 2 distinct players are entered, all names are correct, and there are no duplicates.") 
    elif protected_action(update_ranking, order, password=password, ADMIN_PASSWORD=ADMIN_PASSWORD, 
                        success_msg="Ranking updated successfully!") and input_check(order, all_players_ranking):
        all_players_ranking = load_players()
        ranking_placeholder.subheader("Current ranking")
        ranking_placeholder.write(all_players_ranking)


# Add player
st.subheader("📋 Manage players")
new_player = st.text_input("Enter new player's name")

if st.button("Add player"):
    if not new_player:
        st.warning("⚠️ Please enter a player name.")
    elif not re.fullmatch(r"[A-Za-z]+", new_player):
        st.error("❌ The name must contain only letters (A–Z or a–z), no spaces or special characters.")
    elif new_player in all_players_ranking:
        st.warning(f"{new_player} already exists.")
    else: 
        if protected_action(add_player, new_player, password=password, ADMIN_PASSWORD=ADMIN_PASSWORD, 
                            success_msg=f"Player '{new_player}' added with initial score 100!"):
            all_players_ranking = load_players()
            ranking_placeholder.subheader("Current ranking")
            ranking_placeholder.write(all_players_ranking)

# Remove player
options = ["None"] + list(all_players_ranking.keys())
player_to_remove = st.selectbox("Select a player to remove", options=options, index=0)
if st.button("Remove player"):
    if player_to_remove == "None":
        st.info("ℹ️ No player selected for removal.")
    else:
        if protected_action(remove_player, player_to_remove, password=password, ADMIN_PASSWORD=ADMIN_PASSWORD, 
                            success_msg=f"Player '{player_to_remove}' removed from ranking!"):
            all_players_ranking = load_players()
            ranking_placeholder.subheader("Current ranking")
            ranking_placeholder.write(all_players_ranking)