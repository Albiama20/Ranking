# 🏆 ELO Ranking System

This Streamlit application manages and tracks player ratings using the ELO system.  
It allows users to view the current rankings, update results after matches, and manage players securely through a password-protected admin interface.

📍 **Live App:** [Open app in Streamlit](https://ranking-boccio.streamlit.app/)

## 🚀 Features

### 👥 Player Management
- Add or remove players directly from the app  
- Initial ELO rating automatically set to **100** for new players  
- All data stored and synchronized with a **Google Sheet**

### 🧮 Match Updates
- Update the ranking after each match by entering players **in order of placement**  
- The app automatically recalculates and saves updated ELO scores  
- Input validation ensures:
  - At least two distinct players per match  
  - No duplicate names  
  - All names must already exist in the database

### 🔒 Admin Protection
- All write operations (add, remove, update) are **password-protected**  
- The password is stored securely in `st.secrets`  
- Users without the password can **only view** the current rankings