import streamlit as st
import pandas as pd
import numpy as np
import pickle
import os
from PIL import Image

# Load and clean basket data
basket = pd.read_csv("groceries.csv", header=None)
basket = basket.astype(str)

basket.replace({
    'cling film/bags': 'cling bags',
    'flower soil/fertilizer': 'flower soil',
    'fruit/vegetable juice': 'fruit juice',
    'nuts/prunes': 'nuts',
    'packaged fruit/vegetables': 'packed fruits and vegetables',
    'photo/film': 'photo film',
    'red/blush wine': 'red wine',
    'rolls/buns': 'buns',
    'whipped/sour cream': 'whipped cream'
}, inplace=True)

groceries_list = np.unique(basket.values)
groceries_unique_list = groceries_list[groceries_list != 'nan']

# Paths
background_image_path = "C:\\Users\\91770\\Desktop\\basket analysis\\bgimage.png"
item_images_folder = "C:\\Users\\91770\\Desktop\\basket analysis\\images"
pickle_file_path = 'association_rules.pkl'

# Load association rules
try:
    with open(pickle_file_path, 'rb') as f:
        rules_set = pickle.load(f)
except FileNotFoundError:
    st.error("Association rules pickle file not found")
    rules_set = None

def main():
    # Scrolling title
    st.markdown("""
        <style>
            @keyframes scroll {
                0% { transform: translateX(100%); }
                100% { transform: translateX(-100%); }
            }
            .scrolling-title {
                white-space: nowrap;
                overflow: hidden;
                animation: scroll 10s linear infinite;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<h1 class="scrolling-title">Welcome to Market Basket Analysis</h1>', unsafe_allow_html=True)

    # Load and display background
    image = Image.open(background_image_path)
    show_background = True

    # Sidebar item selection
    st.sidebar.header('Select Items')
    selected_items = st.sidebar.multiselect('Choose items:', groceries_unique_list)

    if st.sidebar.button('Get Recommendations'):
        if len(selected_items) == 0:
            st.warning("Please select at least one item.")
        elif rules_set is not None:
            selected_rules = rules_set[
                rules_set['antecedents'].apply(lambda x: all(item in x for item in selected_items))
            ]
            if not selected_rules.empty:
                recommended_items = get_recommendations(selected_rules)
                if recommended_items:
                    st.header('Recommended Items:')
                    display_images(recommended_items)
                    show_background = False
                else:
                    st.write('No recommendations found for selected items.')
                    show_background = False
            else:
                st.write('No recommendations found for selected items.')
                show_background = False
        else:
            st.error("No association rules to display")
            show_background = False

    if show_background:
        st.image(image, caption='Background', width=800)

# Extract recommended items and image paths
def get_recommendations(selected_rules):
    recommended_items = {}
    for _, row in selected_rules.iterrows():
        consequents = row['consequents']
        for item in consequents:
            item_image_path = os.path.join(item_images_folder, f"{item}.jpeg")
            if os.path.exists(item_image_path):
                recommended_items[item] = item_image_path
    return recommended_items

# Display recommended items with images in rows and columns
def display_images(recommended_items):
    num_columns = 3
    num_items = len(recommended_items)
    rows = num_items // num_columns + (num_items % num_columns > 0)
    image_width = 200
    image_height = 150

    item_index = 0
    for _ in range(rows):
        cols = st.columns(num_columns)
        for col in range(num_columns):
            if item_index >= num_items:
                break
            item, image_path = list(recommended_items.items())[item_index]
            if image_path and os.path.exists(image_path):
                image = Image.open(image_path)
                image = image.resize((image_width, image_height))
                with cols[col]:
                    st.image(image, caption=item, use_container_width=True)  # ✅ Updated here
            else:
                with cols[col]:
                    st.write(item)
            item_index += 1

if __name__ == "__main__":
    main()
