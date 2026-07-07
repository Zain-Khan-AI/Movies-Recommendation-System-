import streamlit as st
import pickle
import pandas as pd
import requests
import os
import gdown

FILE_ID = "1i1ryfqpvZ7h4jNK4qZI_C6mJcsYlo9WZ"
OUTPUT = "similarity.pkl"


if not os.path.exists(OUTPUT):
    print("Downloading similarity.pkl...")
    url = f"https://drive.google.com/uc?id={FILE_ID}"
    gdown.download(url, OUTPUT, quiet=False)
# ==========================================
# BYPASS LOCAL NETWORK SECURITY RESTRICTIONS
# ==========================================
os.environ['NO_PROXY'] = 'api.themoviedb.org,image.tmdb.org'

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="Movie Recommendation System",
    page_icon="🍿",
    layout="wide"
)


# ==========================================
# CUSTOM CSS
# ==========================================
st.markdown("""
<style>

/* ==========================
   NETFLIX BACKGROUND
========================== */

.stApp{
    background:
    radial-gradient(circle at top, rgba(229,9,20,0.30) 0%, rgba(20,20,20,0.95) 40%),
    linear-gradient(180deg,#1a0000 0%, #0f0f0f 35%, #000000 100%);
    color:white;
}

/* Title */
h1{
    color:#E50914;
    font-size:55px;
    font-weight:800;
    text-align:center;
}

/* Selectbox */
div[data-baseweb="select"] > div{
    background:#181818 !important;
    color:white !important;
    border:1px solid #333 !important;
    border-radius:8px !important;
}

/* Button */
.stButton>button{
    width:100%;
    background:#E50914;
    color:white;
    border:none;
    border-radius:8px;
    padding:12px;
    font-size:18px;
    font-weight:bold;
    transition:0.3s;
}

.stButton>button:hover{
    background:#F40612;
    box-shadow:0 0 25px rgba(229,9,20,.7);
}

/* Movie Card */
.movie-card{
    background:#181818;
    border-radius:10px;
    overflow:hidden;
    transition:0.35s;
}

.movie-card:hover{
    transform:scale(1.08);
    box-shadow:0 15px 35px rgba(229,9,20,.45);
}

.movie-card img{
    width:100%;
    height:360px;
    object-fit:cover;
    transition:.35s;
}


.movie-card:hover img{
    transform:scale(1.05);
}

.movie-title{
    color:white;
    text-align:center;
    padding:12px;
    font-weight:bold;
}

/* Scrollbar */
::-webkit-scrollbar{
    width:10px;
}

::-webkit-scrollbar-track{
    background:#111;
}

::-webkit-scrollbar-thumb{
    background:#E50914;
    border-radius:20px;
}

</style>
""", unsafe_allow_html=True)



# ==========================================
# FETCH POSTER    
# ==========================================
def fetch_poster(movie_id):
    api_key = "8265bd1679663a7ea12ac168da84d2e8"

    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"

    try:
        response = requests.get(url, timeout=7)

        if response.status_code == 200:
            data = response.json()

            poster_path = data.get("poster_path")

            if poster_path:
                return "https://image.tmdb.org/t/p/w500" + poster_path

        return "https://via.placeholder.com/500x750?text=No+Poster"

    except:
        return "https://via.placeholder.com/500x750?text=No+Poster"

# ==========================================
# CACHE DATA FOR FAST DROPDOWN (Add this new function)
# ==========================================
@st.cache_data
def get_clean_movie_list(movies_df):
    # Convert numpy array/pandas series to pure Python list (Lag fix karega)
    return list(movies_df["title"].values)
# ==========================================
# 🔥 SMART FILE LOADING (Yeh har click par reload hone se bachaega)
# ==========================================
@st.cache_resource
def load_base_files():
    try:
        m_dict = pickle.load(open("movie_dict.pkl", "rb"))
        m_df = pd.DataFrame(m_dict)
        sim_matrix = pickle.load(open("similarity.pkl", "rb"))
        return m_df, sim_matrix
    except Exception as e:
        return None, None

# ==========================================
# RECOMMEND FUNCTION
# ==========================================
# ==========================================
# RECOMMEND FUNCTION (Error Handling Ke Sath)
# ==========================================
def recommend(movie):
    # 1. Check karein ke jo movie user ne search ki hai kya woh dataset mein hai?
    matching_movies = movies[movies['title'] == movie]
    
    # 2. Agar movie nahi milti toh khali return kar dein taaki app crash na ho
    if matching_movies.empty:
        return None, None

    # 3. Agar movie mil jaye toh uska sahi index nikalein
    movie_index = matching_movies.index[0]
    distances = similarity[movie_index]

    movies_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommended_movies = []
    recommended_posters = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(movie_id))

    return recommended_movies, recommended_posters



# ==========================================
# TITLE
# ==========================================
st.title("🎬 Movie Recommendation System")
st.markdown("""
<p style="
text-align:center;
color:#B3B3B3;
font-size:15px;
margin-top:-10px;
margin-bottom:25px;">
🚨Discover similar movies based on your favorite picks. This is a recommendation system only, not a movie streaming platform.
</p>
""", unsafe_allow_html=True)

# ==========================================
# LOAD PICKLE FILES
# ==========================================
# ==========================================
# LOAD PICKLE FILES
# ==========================================
try:
    
    movies, similarity = load_base_files()


    # 🔥 CHANGE HERE: Standard list call karein function ke zariye
    movie_list = get_clean_movie_list(movies)

    # ---------- Center Search Box with Custom Wide Dropdown ----------
    left, center, right = st.columns([1, 4, 1])

    with center:
        # Browser background logic for wide suggestions block
        st.markdown(f"""
            <div style="position: relative; width: 100%; text-align: left; box-sizing: border-box;">
                <label style="font-weight:bold; font-size:16px; color:white; display:block; margin-bottom:8px;">
                    🎬 Type or Select a Movie
                </label>
                
                <!-- Main Search Bar -->
                <input type="text" id="movie_input_html" autocomplete="off"
                       placeholder="Type movie name here (e.g., 'Avatar' or 'h')..." 
                       style="width:100%; padding:14px; background:#181818; color:white; 
                              border:1px solid #444; border-radius:8px; font-size:16px; box-sizing: border-box;">
                
                <!-- Custom Dropdown Container - ISSI KI WIDTH EXACT 100% BAR KE BARABAR HOGI -->
                <div id="custom_dropdown" style="display: none; position: absolute; top: 100%; left: 0; 
                     width: 100%; max-height: 250px; overflow-y: auto; background: #181818; 
                     border: 1px solid #444; border-top: none; border-radius: 0 0 8px 8px; z-index: 9999; 
                     box-sizing: border-box; box-shadow: 0px 8px 16px rgba(0,0,0,0.5);">
                </div>
            </div>

            <script>
                // Movie list string list parsing array
                const movies = {list(movie_list)};
                const input = document.getElementById('movie_input_html');
                const dropdown = document.getElementById('custom_dropdown');

                // Dynamic matching array loop inside frontend JavaScript (0% Server Lag)
                input.addEventListener('input', function() {{
                    const val = this.value.toLowerCase();
                    dropdown.innerHTML = '';
                    
                    if (!val) {{
                        dropdown.style.display = 'none';
                        return;
                    }}

                    // Match filter logic
                    const matches = movies.filter(m => m.toLowerCase().includes(val)).slice(0, 15);

                    if (matches.length > 0) {{
                        matches.forEach(match => {{
                            const item = document.createElement('div');
                            item.textContent = match;
                            item.style.padding = '12px 15px';
                            item.style.cursor = 'pointer';
                            item.style.color = 'white';
                            item.style.borderBottom = '1px solid #222';
                            item.style.fontSize = '15px';
                            
                            // Hover element overlay styling
                            item.addEventListener('mouseenter', function() {{
                                this.style.background = '#E50914';
                            }});
                            item.addEventListener('mouseleave', function() {{
                                this.style.background = 'transparent';
                            }});
                            
                            // When click option, lock value
                            item.addEventListener('click', function() {{
                                input.value = match;
                                dropdown.style.display = 'none';
                                
                                // Streamlit message parameters bridge trigger
                                window.parent.postMessage({{
                                    isStreamlitMessage: true,
                                    type: 'streamlit:setComponentValue',
                                    value: match
                                }}, '*');
                            }});
                            dropdown.appendChild(item);
                        }});
                        dropdown.style.display = 'block';
                    }} else {{
                        dropdown.style.display = 'none';
                    }}
                }});

                // Close dropdown if user clicks outside the workspace container
                document.addEventListener('click', function(e) {{
                    if (e.target !== input) {{
                        dropdown.style.display = 'none';
                    }}
                }});
            </script>
        """, unsafe_allow_html=True)

        # Invisible query param backend value storage element
        selected_movie = st.text_input("hidden_query", key="movie_bridge", label_visibility="collapsed")
        st.markdown("<style>div[data-testid='stTextInput'] { display: none !important; }</style>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        show = st.button(
            "🎬 Show Recommendations",
            use_container_width=True
        )


    if show:
        # Check karein ke variable khali toh nahi hai
        if not selected_movie or str(selected_movie).strip() == "":
            st.warning("⚠️ Please type or select a valid movie name from the suggestion list first!")
        else:
            movie_query = str(selected_movie).strip()
            
            # Safe dataset checking to avoid IndexError crashes
            matching_movies = movies[movies['title'].str.lower() == movie_query.lower()]
            
            if matching_movies.empty:
                st.error("❌ Movie name match nahi hua! Please list me se kisi movie ka poora naam select ya exact type karein.")
            else:
                exact_title = matching_movies.iloc[0]['title']
                names, posters = recommend(exact_title)
                
                if names is None:
                    st.error("❌ Recommendation system load nahi ho saka. Dobara koshish karein.")
                else:
                    # Netflix-style bouncing loading animation
                    st.markdown("""
                    <style>
                    .loading { text-align: center; color: white; font-size: 22px; font-weight: bold; margin-top: 20px; }
                    .loading span { display: inline-block; animation: bounce 1.4s infinite; }
                    .loading span:nth-child(2) { animation-delay: 0.2s; }
                    .loading span:nth-child(3) { animation-delay: 0.4s; }
                    @keyframes bounce { 0%, 80%, 100% { transform: translateY(0); opacity: 0.4; } 40% { transform: translateY(-8px); opacity: 1; } }
                    </style>
                    """, unsafe_allow_html=True)

                    loading = st.empty()
                    loading.markdown('<div class="loading">Finding Similar Movies<span>.</span><span>.</span><span>.</span></div>', unsafe_allow_html=True)
                    
                    loading.empty()

                    cols = st.columns(5)
                    for i in range(5):
                        with cols[i]:
                            st.markdown(
                                f"""
                                <div class="movie-card">
                                    <img src="{posters[i]}">
                                    <div class="movie-title">{names[i]}</div>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

except FileNotFoundError:
    st.error("❌ movie_dict.pkl ya similarity.pkl file nahi mili.")






st.markdown("""
<hr style="border:1px solid #333; margin-top:60px;">

<div style="text-align:center; color:white;">

<h4>
Generated by
<a href="https://www.linkedin.com/in/m-zain-khan-2555913a9/" target="_blank"
style="color:#E50914; text-decoration:none;">
M. Zain Khan
</a>
</h4>

<div style="display:flex;
justify-content:center;
align-items:center;
gap:40px;
margin-top:15px;">

<a href="https://www.linkedin.com/in/m-zain-khan-2555913a9/" target="_blank"
style="text-decoration:none;color:white;font-weight:bold;display:flex;align-items:center;gap:8px;">

<img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" width="28">
<span>LinkedIn</span>

</a>

<a href="https://github.com/Zain-Khan-AI" target="_blank"
style="text-decoration:none;color:white;font-weight:bold;display:flex;align-items:center;gap:8px;">

<img src="https://cdn-icons-png.flaticon.com/512/733/733553.png" width="28">
<span>GitHub</span>

</a>

</div>

</div>
""", unsafe_allow_html=True)

