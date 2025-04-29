import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import time
import random
import plotly.express as px
import plotly.graph_objects as go
from streamlit_lottie import st_lottie
import requests

# Set Page Config
st.set_page_config(
    page_title="Personal Library Management System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
.main-header {
    font-size:3rem;
    color: #1E3A8A;
    font-weight: 700;
    margin-bottom: 1rem;
    text-align: center;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
}
.sub-header {
    font-size: 1.8rem;
    color: #3B82F6;
    font-weight:600;
    margin-top:1rem;
    margin-bottom:1rem;
}
.success-message {
    padding: 1rem;
    background-color: #ECFDF5;
    border-left: 5px solid #10B981;
    border-radius:0.375rem;
}
.warning-message {
    padding: 1rem;
    background-color: #FEF3C7;
    border-left: 5px solid #F59E0B;
    border-radius:0.375rem;
}
.book-card {
    background-color: #F3F4F6;
    border-radius:0.5rem;
    padding: 1rem;
    margin-bottom: 1rem;
    border-left: 5px solid #3B82F6;
}
.read-badge {
    background-color: #10B981;
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius:1rem;
    font-size: 0.875rem;
    font-weight:600;
}
.unread-badge {
    background-color: #F87171;
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius:1rem;
    font-size: 0.875rem;
    font-weight:600;
}
</style>
""", unsafe_allow_html=True)

# Functions
def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

def load_library():
    if os.path.exists("library.json"):
        with open("library.json", "r") as file:
            st.session_state.library = json.load(file)

def save_library():
    with open("library.json", "w") as file:
        json.dump(st.session_state.library, file)

def add_book(title, author, publication_year, genre, read_status):
    book = {
        "title": title,
        "author": author,
        "publication_year": publication_year,
        "genre": genre,
        "read_status": read_status,
        "added_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.library.append(book)
    save_library()
    st.session_state.book_added = True
    time.sleep(0.5)

def remove_book(index):
    if 0 <= index < len(st.session_state.library):
        del st.session_state.library[index]
        save_library()
        st.session_state.book_removed = True

def search_book(search_term, search_by):
    results = []
    for book in st.session_state.library:
        if search_by == "Title" and search_term.lower() in book["title"].lower():
            results.append(book)
        elif search_by == "Author" and search_term.lower() in book["author"].lower():
            results.append(book)
        elif search_by == "Genre" and search_term.lower() in book["genre"].lower():
            results.append(book)
    st.session_state.search_results = results

def get_library_stats():
    total_books = len(st.session_state.library)
    read_books = sum(1 for book in st.session_state.library if book["read_status"])
    percent_read = (read_books / total_books * 100) if total_books > 0 else 0

    genres = {}
    authors = {}
    decades = {}

    for book in st.session_state.library:
        genres[book["genre"]] = genres.get(book["genre"], 0) + 1
        authors[book["author"]] = authors.get(book["author"], 0) + 1
        decade = (book["publication_year"] // 10) * 10
        decades[decade] = decades.get(decade, 0) + 1

    return {
        "total_books": total_books,
        "read_books": read_books,
        "percent_read": percent_read,
        "genres": dict(sorted(genres.items(), key=lambda x: x[1], reverse=True)),
        "authors": dict(sorted(authors.items(), key=lambda x: x[1], reverse=True)),
        "decades": dict(sorted(decades.items()))
    }

def create_visualizations(stats):
    if stats["total_books"] > 0:
        fig_read_status = go.Figure(data=[go.Pie(
            labels=["Read", "Unread"],
            values=[stats["read_books"], stats["total_books"] - stats["read_books"]],
            hole=0.4
        )])
        fig_read_status.update_layout(title_text="Read vs Unread Books")
        st.plotly_chart(fig_read_status, use_container_width=True)

    if stats["genres"]:
        genres_df = pd.DataFrame({
            "Genre": list(stats["genres"].keys()),
            "Count": list(stats["genres"].values())
        })
        fig_genres = px.bar(
            genres_df,
            x="Genre",
            y="Count",
            color="Count",
            color_continuous_scale=px.colors.sequential.Blues
        )
        fig_genres.update_layout(title_text="Books by Genre")
        st.plotly_chart(fig_genres, use_container_width=True)

    if stats["decades"]:
        decades_df = pd.DataFrame({
            "Decade": [f"{decade}s" for decade in stats["decades"].keys()],
            "Count": list(stats["decades"].values())
        })
        fig_decades = px.line(
            decades_df,
            x="Decade",
            y="Count",
            markers=True
        )
        fig_decades.update_layout(title_text="Books by Decade")
        st.plotly_chart(fig_decades, use_container_width=True)

# Initialize Session State
if "library" not in st.session_state:
    st.session_state.library = []
if "search_results" not in st.session_state:
    st.session_state.search_results = []
if "book_added" not in st.session_state:
    st.session_state.book_added = False
if "book_removed" not in st.session_state:
    st.session_state.book_removed = False
if "current_view" not in st.session_state:
    st.session_state.current_view = "library"

# Load Library
load_library()

# Sidebar
st.sidebar.title("Navigation")
lottie_book = load_lottieurl("https://assets9.lottiefiles.com/temp/1f20_aKAfIn.json")
if lottie_book:
    st_lottie(lottie_book, height=200)

nav_options = st.sidebar.radio("Choose an option:", ["View Library", "Add Book", "Search Books", "Library Statistics"])
st.session_state.current_view = nav_options

# Main
st.markdown("<h1 class='main-header'>📚 Personal Library Manager</h1>", unsafe_allow_html=True)

if st.session_state.current_view == "Add Book":
    st.markdown("<h2 class='sub-header'>Add a New Book</h2>", unsafe_allow_html=True)
    with st.form(key="add_book_form"):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Book Title")
            author = st.text_input("Author")
            publication_year = st.number_input("Publication Year", min_value=1000, max_value=datetime.now().year, step=1)
        with col2:
            genre = st.text_input("Genre")
            read_status = st.radio("Read Status", ["Read", "Unread"], horizontal=True)
            submit_button = st.form_submit_button("Add Book")

    if submit_button and title and author:
        add_book(title, author, publication_year, genre, read_status == "Read")
        st.success("Book added successfully!")
        st.balloons()

elif st.session_state.current_view == "View Library":
    st.markdown("<h2 class='sub-header'>Your Library</h2>", unsafe_allow_html=True)
    if not st.session_state.library:
        st.warning("Your library is empty. Add some books!")
    else:
        for i, book in enumerate(st.session_state.library):
            st.markdown(f"""
            <div class="book-card">
            <h3>{book['title']}</h3>
            <p><strong>Author:</strong> {book['author']}</p>
            <p><strong>Publication Year:</strong> {book['publication_year']}</p>
            <p><strong>Genre:</strong> {book['genre']}</p>
            <p><span class="{ 'read-badge' if book['read_status'] else 'unread-badge' }">{ 'Read' if book['read_status'] else 'Unread' }</span></p>
            </div>
            """, unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Remove {i}", key=f"remove_{i}"):
                    remove_book(i)
                    st.rerun()
            with col2:
                if st.button(f"Toggle Read Status {i}", key=f"toggle_{i}"):
                    st.session_state.library[i]["read_status"] = not st.session_state.library[i]["read_status"]
                    save_library()
                    st.rerun()

elif st.session_state.current_view == "Search Books":
    st.markdown("<h2 class='sub-header'>Search Books</h2>", unsafe_allow_html=True)
    search_by = st.selectbox("Search By", ["Title", "Author", "Genre"])
    search_term = st.text_input("Enter search term")
    if st.button("Search"):
        search_book(search_term, search_by)
    if st.session_state.search_results:
        for book in st.session_state.search_results:
            st.write(f"**{book['title']}** by {book['author']} ({book['publication_year']})")
    elif search_term:
        st.warning("No books found matching your search.")

elif st.session_state.current_view == "Library Statistics":
    st.markdown("<h2 class='sub-header'>Library Statistics</h2>", unsafe_allow_html=True)
    stats = get_library_stats()
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Books", stats["total_books"])
    col2.metric("Books Read", stats["read_books"])
    col3.metric("Percent Read", f"{stats['percent_read']:.1f}%")
    create_visualizations(stats)

# Footer
st.markdown("---")
st.markdown("© 2025 Arfa Siddiqui - Personal Library Manager", unsafe_allow_html=True)
