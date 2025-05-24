import os
import time
import cv2
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from ultralytics import YOLO
import requests
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision.models import efficientnet_b3, EfficientNet_B3_Weights

from googleapiclient.discovery import build
import google.generativeai as genai
from dotenv import load_dotenv
from flask_cors import CORS

# --- Load environment variables ---
load_dotenv()

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
RESULT_FOLDER = 'static/results'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

#Prompt gemini
prompt = ""

script_dir = os.path.dirname(os.path.abspath(__file__))
prompt_file_path = os.path.join(script_dir, 'static', 'prompt.txt')

try:
    with open(prompt_file_path, 'r', encoding='utf-8') as f_prompt:
        prompt = f_prompt.read()
    print(prompt)
except FileNotFoundError:
    print(f"ERROR: The prompt file 'prompt.txt' was not found at {prompt_file_path}")
except Exception as e:
    print(f"ERROR: Could not read the prompt file 'prompt.txt': {e}")

# --- Cấu hình API Keys và CSE ID ---
GOOGLE_CSE_ID = os.getenv('GOOGLE_CSE_ID')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Kiểm tra xem các biến môi trường đã được đặt chưa
if not GOOGLE_CSE_ID or not GOOGLE_API_KEY or not GEMINI_API_KEY:
    print("Lỗi: Vui lòng đặt các biến môi trường GOOGLE_CSE_ID, GOOGLE_API_KEY và GEMINI_API_KEY.")
    print("Kiểm tra file .env hoặc biến môi trường hệ thống.")

# --- Khởi tạo API Clients ---
cse_service = None
if GOOGLE_CSE_ID and GOOGLE_API_KEY:
    try:
        cse_service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
        print("Google Custom Search API service built.")
    except Exception as e:
        print(f"Lỗi khi build Google Custom Search API service: {e}")

gemini_model = None
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_model = genai.GenerativeModel('gemini-2.5-flash-preview-04-17')
        print("Gemini API model configured.")
    except Exception as e:
        print(f"Lỗi khi cấu hình Gemini API model: {e}")

#Xeno-Canto API
XENO_CANTO_API_BASE_URL = 'https://www.xeno-canto.org/api/2/recordings'

def get_bird_songs(bird_name, max_results=3):
    """
    Calls Xeno-Canto API to get audio recordings for a bird species.
    Args:
        bird_name (str): The common name of the bird (e.g., "Blue_Jay").
        max_results (int): Maximum number of audio URLs to return.
    Returns:
        list: A list of audio file URLs.
    """
    if not bird_name or bird_name.startswith("Error") or bird_name.startswith("Invalid") or bird_name == "N/A":
        print(f"Skipping Xeno-Canto API call for invalid bird name: {bird_name}")
        return []

    query_name = bird_name.replace('_', ' ')


    api_url = f"{XENO_CANTO_API_BASE_URL}?query={query_name}" 

    print(f"Xeno-Canto API Query URL: {api_url}")

    audio_urls = []
    try:
        print(f"Calling Xeno-Canto API for: {query_name}")
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()

        data = response.json()

        print(f"Xeno-Canto API Response Data Keys: {data.keys()}")
        print(f"Xeno-Canto API Num Recordings found: {data.get('num_recordings')}")

        if data and 'recordings' in data:
            for recording in data['recordings'][:max_results]:
                if 'file' in recording:
                    raw_file_path = recording['file']
                    print(f"Raw recording file path from API: {raw_file_path}")
                    if raw_file_path.startswith('http://') or raw_file_path.startswith('https://') or raw_file_path.startswith('//'):
                        full_audio_url = raw_file_path
                    else:
                        full_audio_url = f"https://www.xeno-canto.org{raw_file_path}"

                    print(f"Constructed full audio URL: {full_audio_url}") # <-- Print URL đã xây dựng
                    audio_urls.append(full_audio_url)
            print(f"Found {len(audio_urls)} audio recordings for {query_name}.")
        else:
            print(f"No audio recordings found on Xeno-Canto for {query_name}.")

    except requests.exceptions.RequestException as e:
        print(f"Error calling Xeno-Canto API for {query_name}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while processing Xeno-Canto data for {query_name}: {e}")

    return audio_urls

YOLO_MODEL_PATH = 'best.pt'

CLASSIFIER_MODEL_PATH = 'efficientnet_b3_bird_classifier.pth'
CLASSIFIER_IMG_SIZE = 300
CLASSIFIER_NORM_MEAN = [0.485, 0.456, 0.406]
CLASSIFIER_NORM_STD = [0.229, 0.224, 0.225]

# --- Danh sách lớp chim (giữ nguyên) ---
CLASSIFIER_CLASSES = [
"Abert's_Towhee",
    "Acadian_Flycatcher",
    "Acorn_Woodpecker",
    "Allen's_Hummingbird",
    "American_Avocet",
    "American_Black_Duck",
    "American_Coot",
    "American_Crow",
    "American_Dipper",
    "American_Goldfinch",
    "American_Kestrel",
    "American_Oystercatcher",
    "American_Pipit",
    "American_Redstart",
    "American_Robin",
    "American_Three_toed_Woodpecker",
    "American_Tree_Sparrow",
    "American_White_Pelican",
    "American_Wigeon",
    "American_Woodcock",
    "Anhinga",
    "Anna's_Hummingbird",
    "Anna_Hummingbird",
    "Artic_Tern",
    "Ash_throated_Flycatcher",
    "Baird_Sparrow",
    "Bald_Eagle",
    "Baltimore_Oriole",
    "Band_tailed_Pigeon",
    "Bank_Swallow",
    "Barn_Owl",
    "Barn_Swallow",
    "Barred_Owl",
    "Barrow's_Goldeneye",
    "Bay_breasted_Warbler",
    "Bell's_Vireo",
    "Belted_Kingfisher",
    "Bewick's_Wren",
    "Bewick_Wren",
    "Black_Guillemot",
    "Black_Oystercatcher",
    "Black_Phoebe",
    "Black_Rosy_Finch",
    "Black_Scoter",
    "Black_Skimmer",
    "Black_Tern",
    "Black_Turnstone",
    "Black_Vulture",
    "Black_and_white_Warbler",
    "Black_bellied_Plover",
    "Black_bellied_Whistling_Duck",
    "Black_billed_Cuckoo",
    "Black_billed_Magpie",
    "Black_capped_Chickadee",
    "Black_capped_Vireo",
    "Black_chinned_Hummingbird",
    "Black_crested_Titmouse",
    "Black_crowned_Night_Heron",
    "Black_footed_Albatross",
    "Black_headed_Grosbeak",
    "Black_legged_Kittiwake",
    "Black_necked_Stilt",
    "Black_tailed_Gnatcatcher",
    "Black_throated_Blue_Warbler",
    "Black_throated_Gray_Warbler",
    "Black_throated_Green_Warbler",
    "Black_throated_Sparrow",
    "Blackburnian_Warbler",
    "Blackpoll_Warbler",
    "Blue_Grosbeak",
    "Blue_Jay",
    "Blue_gray_Gnatcatcher",
    "Blue_headed_Vireo",
    "Blue_winged_Teal",
    "Blue_winged_Warbler",
    "Boat_tailed_Grackle",
    "Bobolink",
    "Bohemian_Waxwing",
    "Bonaparte's_Gull",
    "Boreal_Chickadee",
    "Brandt's_Cormorant",
    "Brandt_Cormorant",
    "Brant",
    "Brewer's_Blackbird",
    "Brewer's_Sparrow",
    "Brewer_Blackbird",
    "Brewer_Sparrow",
    "Bridled_Titmouse",
    "Broad_billed_Hummingbird",
    "Broad_tailed_Hummingbird",
    "Broad_winged_Hawk",
    "Bronzed_Cowbird",
    "Brown_Creeper",
    "Brown_Pelican",
    "Brown_Thrasher",
    "Brown_capped_Rosy_Finch",
    "Brown_headed_Cowbird",
    "Brown_headed_Nuthatch",
    "Bufflehead",
    "Bullock's_Oriole",
    "Burrowing_Owl",
    "Bushtit",
    "Cackling_Goose",
    "Cactus_Wren",
    "California_Gull",
    "California_Quail",
    "California_Thrasher",
    "California_Towhee",
    "Calliope_Hummingbird",
    "Canada_Goose",
    "Canada_Warbler",
    "Canvasback",
    "Canyon_Towhee",
    "Canyon_Wren",
    "Cape_Glossy_Starling",
    "Cape_May_Warbler",
    "Cardinal",
    "Carolina_Chickadee",
    "Carolina_Wren",
    "Caspian_Tern",
    "Cassin's_Finch",
    "Cassin's_Kingbird",
    "Cassin's_Vireo",
    "Cattle_Egret",
    "Cave_Swallow",
    "Cedar_Waxwing",
    "Cerulean_Warbler",
    "Chestnut_backed_Chickadee",
    "Chestnut_sided_Warbler",
    "Chihuahuan_Raven",
    "Chimney_Swift",
    "Chipping_Sparrow",
    "Chuck_will_Widow",
    "Cinnamon_Teal",
    "Clark's_Grebe",
    "Clark's_Nutcracker",
    "Clark_Nutcracker",
    "Clay_colored_Sparrow",
    "Cliff_Swallow",
    "Common_Eider",
    "Common_Gallinule",
    "Common_Goldeneye",
    "Common_Grackle",
    "Common_Ground_Dove",
    "Common_Loon",
    "Common_Merganser",
    "Common_Nighthawk",
    "Common_Raven",
    "Common_Redpoll",
    "Common_Tern",
    "Common_Yellowthroat",
    "Cooper's_Hawk",
    "Cordilleran_Flycatcher",
    "Costa's_Hummingbird",
    "Crested_Auklet",
    "Crested_Caracara",
    "Curve_billed_Thrasher",
    "Dark_eyed_Junco",
    "Dickcissel",
    "Double_crested_Cormorant",
    "Downy_Woodpecker",
    "Dunlin",
    "Eared_Grebe",
    "Eastern_Bluebird",
    "Eastern_Kingbird",
    "Eastern_Meadowlark",
    "Eastern_Phoebe",
    "Eastern_Screech_Owl",
    "Eastern_Towhee",
    "Eastern_Wood_Pewee",
    "Elegant_Tern",
    "Eurasian_Collared_Dove",
    "European_Goldfinch",
    "European_Starling",
    "Evening_Grosbeak",
    "Field_Sparrow",
    "Fish_Crow",
    "Florida_Jay",
    "Florida_Scrub_Jay",
    "Forster's_Tern",
    "Forsters_Tern",
    "Fox_Sparrow",
    "Frigatebird",
    "Gadwall",
    "Gambel's_Quail",
    "Geococcyx",
    "Gila_Woodpecker",
    "Glaucous_winged_Gull",
    "Glossy_Ibis",
    "Golden_Eagle",
    "Golden_crowned_Kinglet",
    "Golden_crowned_Sparrow",
    "Golden_fronted_Woodpecker",
    "Golden_winged_Warbler",
    "Grasshopper_Sparrow",
    "Gray_Catbird",
    "Gray_Jay",
    "Gray_Kingbird",
    "Gray_crowned_Rosy_Finch",
    "Great_Black_backed_Gull",
    "Great_Blue_Heron",
    "Great_Cormorant",
    "Great_Crested_Flycatcher",
    "Great_Egret",
    "Great_Grey_Shrike",
    "Great_Horned_Owl",
    "Great_tailed_Grackle",
    "Greater_Roadrunner",
    "Greater_Scaup",
    "Greater_White_fronted_Goose",
    "Greater_Yellowlegs",
    "Green_Heron",
    "Green_Jay",
    "Green_Kingfisher",
    "Green_Violetear",
    "Green_tailed_Towhee",
    "Green_winged_Teal",
    "Groove_billed_Ani",
    "Hairy_Woodpecker",
    "Harlequin_Duck",
    "Harris's_Hawk",
    "Harris's_Sparrow",
    "Harris_Sparrow",
    "Heermann's_Gull",
    "Heermann_Gull",
    "Henslow_Sparrow",
    "Hermit_Thrush",
    "Hermit_Warbler",
    "Herring_Gull",
    "Hoary_Redpoll",
    "Hooded_Merganser",
    "Hooded_Oriole",
    "Hooded_Warbler",
    "Horned_Grebe",
    "Horned_Lark",
    "Horned_Puffin",
    "House_Finch",
    "House_Sparrow",
    "House_Wren",
    "Hutton's_Vireo",
    "Inca_Dove",
    "Indigo_Bunting",
    "Ivory_Gull",
    "Juniper_Titmouse",
    "Kentucky_Warbler",
    "Killdeer",
    "Ladder_backed_Woodpecker",
    "Lark_Bunting",
    "Lark_Sparrow",
    "Laughing_Gull",
    "Laysan_Albatross",
    "Lazuli_Bunting",
    "Le_Conte_Sparrow",
    "Least_Auklet",
    "Least_Flycatcher",
    "Least_Sandpiper",
    "Least_Tern",
    "Lesser_Goldfinch",
    "Lesser_Scaup",
    "Lesser_Yellowlegs",
    "Lincoln's_Sparrow",
    "Lincoln_Sparrow",
    "Little_Blue_Heron",
    "Loggerhead_Shrike",
    "Long_billed_Curlew",
    "Long_tailed_Duck",
    "Long_tailed_Jaeger",
    "Louisiana_Waterthrush",
    "MacGillivray's_Warbler",
    "Magnolia_Warbler",
    "Mallard",
    "Mangrove_Cuckoo",
    "Marbled_Godwit",
    "Marsh_Wren",
    "Merlin",
    "Mew_Gull",
    "Mexican_Jay",
    "Mississippi_Kite",
    "Mockingbird",
    "Monk_Parakeet",
    "Mottled_Duck",
    "Mountain_Bluebird",
    "Mountain_Chickadee",
    "Mourning_Dove",
    "Mourning_Warbler",
    "Mute_Swan",
    "Myrtle_Warbler",
    "Nashville_Warbler",
    "Nelson_Sharp_tailed_Sparrow",
    "Neotropic_Cormorant",
    "Nighthawk",
    "Northern_Bobwhite",
    "Northern_Cardinal",
    "Northern_Flicker",
    "Northern_Fulmar",
    "Northern_Gannet",
    "Northern_Harrier",
    "Northern_Mockingbird",
    "Northern_Parula",
    "Northern_Pintail",
    "Northern_Pygmy_Owl",
    "Northern_Rough_winged_Swallow",
    "Northern_Saw_whet_Owl",
    "Northern_Shoveler",
    "Northern_Shrike",
    "Northern_Waterthrush",
    "Northwestern_Crow",
    "Nuttall's_Woodpecker",
    "Oak_Titmouse",
    "Olive_sided_Flycatcher",
    "Orange_crowned_Warbler",
    "Orchard_Oriole",
    "Osprey",
    "Ovenbird",
    "Pacific_Loon",
    "Pacific_Wren",
    "Pacific_slope_Flycatcher",
    "Painted_Bunting",
    "Palm_Warbler",
    "Parakeet_Auklet",
    "Pelagic_Cormorant",
    "Peregrine_Falcon",
    "Phainopepla",
    "Philadelphia_Vireo",
    "Pied_Kingfisher",
    "Pied_billed_Grebe",
    "Pigeon_Guillemot",
    "Pileated_Woodpecker",
    "Pine_Grosbeak",
    "Pine_Siskin",
    "Pine_Warbler",
    "Plumbeous_Vireo",
    "Pomarine_Jaeger",
    "Prairie_Falcon",
    "Prairie_Warbler",
    "Prothonotary_Warbler",
    "Purple_Finch",
    "Purple_Gallinule",
    "Purple_Martin",
    "Pygmy_Nuthatch",
    "Pyrrhuloxia",
    "Red_Crossbill",
    "Red_bellied_Woodpecker",
    "Red_breasted_Merganser",
    "Red_breasted_Nuthatch",
    "Red_breasted_Sapsucker",
    "Red_cockaded_Woodpecker",
    "Red_eyed_Vireo",
    "Red_faced_Cormorant",
    "Red_headed_Woodpecker",
    "Red_legged_Kittiwake",
    "Red_naped_Sapsucker",
    "Red_necked_Grebe",
    "Red_shouldered_Hawk",
    "Red_tailed_Hawk",
    "Red_throated_Loon",
    "Red_winged_Blackbird",
    "Reddish_Egret",
    "Redhead",
    "Rhinoceros_Auklet",
    "Ring_billed_Gull",
    "Ring_necked_Duck",
    "Ring_necked_Pheasant",
    "Ringed_Kingfisher",
    "Rock_Pigeon",
    "Rock_Wren",
    "Rose_breasted_Grosbeak",
    "Roseate_Spoonbill",
    "Ross's_Goose",
    "Rough_legged_Hawk",
    "Royal_Tern",
    "Ruby_crowned_Kinglet",
    "Ruby_throated_Hummingbird",
    "Ruddy_Duck",
    "Ruddy_Turnstone",
    "Ruffed_Grouse",
    "Rufous_Hummingbird",
    "Rufous_crowned_Sparrow",
    "Rusty_Blackbird",
    "Sage_Thrasher",
    "Sanderling",
    "Sandhill_Crane",
    "Savannah_Sparrow",
    "Say's_Phoebe",
    "Sayornis",
    "Scaled_Quail",
    "Scarlet_Tanager",
    "Scissor_tailed_Flycatcher",
    "Scott_Oriole",
    "Seaside_Sparrow",
    "Semipalmated_Plover",
    "Semipalmated_Sandpiper",
    "Sharp_shinned_Hawk",
    "Shiny_Cowbird",
    "Short_billed_Dowitcher",
    "Slaty_backed_Gull",
    "Snow_Bunting",
    "Snow_Goose",
    "Snowy_Egret",
    "Snowy_Owl",
    "Solitary_Sandpiper",
    "Song_Sparrow",
    "Sooty_Albatross",
    "Spotted_Catbird",
    "Spotted_Sandpiper",
    "Spotted_Towhee",
    "Steller's_Jay",
    "Summer_Tanager",
    "Surf_Scoter",
    "Surfbird",
    "Swainson's_Hawk",
    "Swainson's_Thrush",
    "Swainson_Warbler",
    "Swallow_tailed_Kite",
    "Swamp_Sparrow",
    "Tennessee_Warbler",
    "Townsend's_Solitaire",
    "Townsend's_Warbler",
    "Tree_Sparrow",
    "Tree_Swallow",
    "Tricolored_Heron",
    "Tropical_Kingbird",
    "Trumpeter_Swan",
    "Tufted_Titmouse",
    "Tundra_Swan",
    "Turkey_Vulture",
    "Varied_Thrush",
    "Vaux's_Swift",
    "Veery",
    "Verdin",
    "Vermilion_Flycatcher",
    "Vesper_Sparrow",
    "Violet_green_Swallow",
    "Warbling_Vireo",
    "Western_Bluebird",
    "Western_Grebe",
    "Western_Gull",
    "Western_Kingbird",
    "Western_Meadowlark",
    "Western_Sandpiper",
    "Western_Screech_Owl",
    "Western_Scrub_Jay",
    "Western_Tanager",
    "Western_Wood_Pewee",
    "Whimbrel",
    "Whip_poor_Will",
    "White_Ibis",
    "White_Pelican",
    "White_breasted_Kingfisher",
    "White_breasted_Nuthatch",
    "White_crowned_Sparrow",
    "White_eyed_Vireo",
    "White_faced_Ibis",
    "White_necked_Raven",
    "White_tailed_Kite",
    "White_throated_Sparrow",
    "White_throated_Swift",
    "White_winged_Crossbill",
    "White_winged_Dove",
    "White_winged_Scoter",
    "Wild_Turkey",
    "Willet",
    "Wilson's_Phalarope",
    "Wilson's_Snipe",
    "Wilson's_Warbler",
    "Wilson_Warbler",
    "Winter_Wren",
    "Wood_Duck",
    "Wood_Stork",
    "Wood_Thrush",
    "Worm_eating_Warbler",
    "Wrentit",
    "Yellow_Warbler",
    "Yellow_bellied_Flycatcher",
    "Yellow_bellied_Sapsucker",
    "Yellow_billed_Cuckoo",
    "Yellow_billed_Magpie",
    "Yellow_breasted_Chat",
    "Yellow_crowned_Night_Heron",
    "Yellow_headed_Blackbird",
    "Yellow_rumped_Warbler",
    "Yellow_throated_Vireo",
    "Yellow_throated_Warbler"
]
NUM_CLASSIFIER_CLASSES = len(CLASSIFIER_CLASSES)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# --- Tải Model YOLO (giữ nguyên) ---
yolo_model = None
try:
    yolo_model = YOLO(YOLO_MODEL_PATH)
    print(f"YOLO Model '{YOLO_MODEL_PATH}' loaded successfully.")
except Exception as e:
    print(f"Error loading YOLO model '{YOLO_MODEL_PATH}': {e}")
    yolo_model = None

# --- Tải Model Classifier (giữ nguyên) ---
classifier_model = None
try:
    classifier_model = efficientnet_b3(weights=None)
    print("Created base EfficientNet_B3 structure.")
    num_ftrs = classifier_model.classifier[-1].in_features
    print(f"Detected {num_ftrs} input features for the final layer.")
    num_classes = NUM_CLASSIFIER_CLASSES
    new_classifier_layer = nn.Linear(num_ftrs, num_classes)
    print(f"Created a new Linear layer with {num_classes} output features.")
    classifier_model.classifier[-1] = new_classifier_layer
    print("Replaced the original final layer with the new classifier layer.")

    print(f"Attempting to load state_dict from '{CLASSIFIER_MODEL_PATH}'...")
    state_dict = torch.load(CLASSIFIER_MODEL_PATH, map_location=device)
    classifier_model.load_state_dict(state_dict, strict=True)
    print("State_dict loaded successfully.")
    classifier_model.to(device)
    classifier_model.eval()
    print(f"Classifier Model '{CLASSIFIER_MODEL_PATH}' loaded and configured successfully.")

except FileNotFoundError:
    print(f"Error: Classifier model file not found at {CLASSIFIER_MODEL_PATH}")
    print("Please ensure the .pth file is in the correct location.")
    classifier_model = None
except RuntimeError as e:
    print(f"Error loading Classifier model state_dict (structure mismatch likely): {e}")
    print("Please ensure the model structure defined in app.py (especially the final linear layer) matches the structure used during training.")
    print(f"Expected number of output classes: {NUM_CLASSIFIER_CLASSES}")
    classifier_model = None
except Exception as e:
    print(f"An unexpected error occurred loading Classifier model: {e}")
    if app.debug:
         import traceback
         traceback.print_exc()
    classifier_model = None

# --- Classifier Transform---
classifier_transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize(340), # Resize ảnh về kích thước lớn hơn kích thước crop
    transforms.CenterCrop(CLASSIFIER_IMG_SIZE), # Cắt ảnh vào giữa với kích thước mong muốn
    transforms.ToTensor(),
    transforms.Normalize(mean=CLASSIFIER_NORM_MEAN, std=CLASSIFIER_NORM_STD)
])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    # Truyền None cho result_image và detection_results khi render lần đầu
    return render_template('index.html', result_image=None, detection_results=None, error_message=None)

@app.route('/predict', methods=['POST'])
def predict():
    if yolo_model is None:
        return render_template('index.html', error_message="Error: YOLO model could not be loaded.")
    if classifier_model is None:
        return render_template('index.html', error_message="Error: Classifier model could not be loaded.")
    # Kiểm tra API clients
    if cse_service is None or gemini_model is None:
         return render_template('index.html', error_message="Error: Google API clients could not be initialized. Check API keys and CSE ID.")


    if 'image' not in request.files:
        return redirect(request.url)

    file = request.files['image']

    if file.filename == '':
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = int(time.time())
        upload_filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{timestamp}_{filename}")
        file.save(upload_filepath)

        detection_results_list = []

        try:
            img = cv2.imread(upload_filepath)
            if img is None:
                 return render_template('index.html', error_message="Error: Could not read the uploaded image.")

            results = yolo_model(upload_filepath)
            yolo_detections = results[0]

            annotated_img = img.copy()

            # --- Xử lý từng bounding box ---
            for i, box in enumerate(yolo_detections.boxes):
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                yolo_conf = float(box.conf[0])
                cls_id = int(box.cls[0])
                yolo_class_name = yolo_model.names[cls_id]

                species_name = "N/A"
                species_conf = None
                species_info = "Không thể lấy thông tin chi tiết." 
                image_urls = []
                audio_urls = []

                # --- Phân loại loài chim ---
                try:
                    y1_crop = max(0, y1)
                    x1_crop = max(0, x1)
                    y2_crop = min(img.shape[0], y2)
                    x2_crop = min(img.shape[1], img.shape[1]) # Sửa lỗi chính tả ở đây
                    x2_crop = min(img.shape[1], x2) # Sửa lỗi chính tả ở đây

                    cropped_img = img[y1_crop:y2_crop, x1_crop:x2_crop]

                    if cropped_img.shape[0] > 0 and cropped_img.shape[1] > 0:
                        img_rgb = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2RGB)
                        input_tensor = classifier_transform(img_rgb).unsqueeze(0)
                        input_tensor = input_tensor.to(device)

                        with torch.no_grad():
                            classifier_outputs = classifier_model(input_tensor)

                        probabilities = torch.softmax(classifier_outputs, dim=1)[0]
                        species_conf_tensor, predicted_class_index = torch.max(probabilities, 0)
                        species_name = CLASSIFIER_CLASSES[predicted_class_index.item()]
                        species_conf = species_conf_tensor.item()
                    else:
                         species_name = "Invalid crop"
                         species_conf = None
                         print(f"Skipping classification for invalid crop region: ({x1},{y1}) to ({x2},{y2})")


                except Exception as classifier_error:
                    print(f"Error during classification for box ({x1},{y1})-({x2},{y2}): {classifier_error}")
                    species_name = f"Classification Error"
                    species_conf = None
                    if app.debug:
                         print(f"Classifier Error Details: {classifier_error}")


                # --- Gọi Gemini API để lấy thông tin ---
                if species_name and species_name != "N/A" and not species_name.startswith("Error") and not species_name.startswith("Invalid"):
                    try:
                        clean_species_name = species_name.replace('_', ' ')
                        gemini_response = gemini_model.generate_content(prompt + clean_species_name)
                        if gemini_response and gemini_response.text:
                             species_info = gemini_response.text
                             print(f"Đã nhận thông tin từ Gemini cho {species_name}.")
                        else:
                             species_info = f"Không thể lấy thông tin chi tiết từ Gemini cho loài chim {clean_species_name}."
                             print(f"Không thể lấy thông tin từ Gemini cho {species_name}.")

                    except Exception as e:
                        print(f"Lỗi khi gọi Gemini API cho {species_name}: {e}")
                        species_info = f"Lỗi khi lấy thông tin từ Gemini." # Rút gọn thông báo lỗi trên giao diện
                        if app.debug:
                             print(f"Gemini API Error Details: {e}")


                # --- Gọi Google Custom Search API để lấy hình ảnh ---
                if species_name and species_name != "N/A" and not species_name.startswith("Error") and not species_name.startswith("Invalid"):
                    try:
                        # Sử dụng tên loài chim đã làm sạch cho truy vấn hình ảnh
                        image_results = cse_service.cse().list(
                            q=clean_species_name + " bird", # Thêm " bird" để kết quả chính xác hơn
                            cx=GOOGLE_CSE_ID,
                            searchType='image',
                            num=5 # Lấy 5 hình ảnh
                        ).execute()

                        if 'items' in image_results:
                            image_urls = [item['link'] for item in image_results['items']]
                            print(f"Tìm thấy {len(image_urls)} hình ảnh cho {species_name}.")
                        else:
                             print(f"Không tìm thấy hình ảnh nào cho {species_name}.")
                             image_urls = [] # Đảm bảo là danh sách rỗng

                    except Exception as e:
                        print(f"Lỗi khi gọi Google Custom Search API cho {species_name}: {e}")
                        # Không cần cập nhật species_info ở đây, chỉ để image_urls là rỗng
                        if app.debug:
                             print(f"Custom Search API Error Details: {e}")
                             
                             # Gọi API Xeno-canto
                if species_name and species_name != "N/A" and not species_name.startswith("Error") and not species_name.startswith("Invalid"):
                    audio_urls = get_bird_songs(species_name)

                # --- Thêm kết quả vào danh sách ---
                detection_results_list.append({
                    'id': i + 1,
                    'yolo_class': yolo_class_name,
                    'yolo_conf': yolo_conf,
                    'species_name': species_name,
                    'species_conf': species_conf,
                    'bbox': (x1, y1, x2, y2),
                    'species_info': species_info, 
                    'image_urls': image_urls,
                    'audio_urls': audio_urls
                })

                # --- Vẽ bounding box và label lên ảnh (giữ nguyên) ---
                if species_conf is not None and species_conf > 0.5:
                     color = (0, 255, 0) # Xanh lá nếu phân loại tự tin
                elif species_name.startswith("Error") or species_name.startswith("Invalid"):
                     color = (0, 0, 255) # Đỏ nếu có lỗi phân loại
                else:
                     color = (255, 0, 0) # Xanh dương nếu phân loại không tự tin hoặc N/A

                cv2.rectangle(annotated_img, (x1, y1), (x2, y2), color, 2)

                # Label hiển thị tên loài chim được phân loại (nếu có) và độ tin cậy
                if species_conf is not None:
                     label = f"{species_name} ({species_conf:.2f})" # Chỉ hiển thị tên loài chim phân loại
                else:
                     label = f"{species_name}" # Hiển thị N/A hoặc lỗi

                # Điều chỉnh vị trí label để không bị tràn
                (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
                text_y_pos = y1 - 10
                if text_y_pos < h + 5:
                     text_y_pos = y1 + h + 10
                     if text_y_pos > annotated_img.shape[0] - 5:
                          text_y_pos = annotated_img.shape[0] - 5 # Đảm bảo không tràn xuống dưới
                text_x_pos = x1

                if text_x_pos < 0:
                     text_x_pos = 0
                if text_x_pos + w > annotated_img.shape[1]:
                     text_x_pos = annotated_img.shape[1] - w

                # Vẽ background cho label
                cv2.rectangle(annotated_img, (text_x_pos, text_y_pos - h - 5), (text_x_pos + w, text_y_pos), color, -1)

                # Vẽ text label
                text_color = (255, 255, 255) if color == (0, 0, 255) else (0, 0, 0) # Text trắng trên nền đỏ, text đen trên nền khác
                cv2.putText(annotated_img, label, (text_x_pos, text_y_pos - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 1, cv2.LINE_AA)


            # --- Lưu ảnh kết quả (giữ nguyên) ---
            result_filename = f"result_{timestamp}_{filename}"
            result_filepath = os.path.join(app.config['RESULT_FOLDER'], result_filename)
            cv2.imwrite(result_filepath, annotated_img)

            # --- Render template với tất cả kết quả ---
            return render_template('index.html',
                                   result_image=url_for('static', filename=f'results/{result_filename}'),
                                   detection_results=detection_results_list, # Truyền danh sách kết quả chi tiết
                                   error_message=None)

        except Exception as e:
            print(f"An unexpected error occurred during processing: {e}")
            if app.debug:
                 import traceback
                 traceback.print_exc()
            # Trả về trang với thông báo lỗi
            return render_template('index.html', error_message=f"An unexpected error occurred: {e}", result_image=None, detection_results=None)

    # Trả về trang với thông báo lỗi nếu file không hợp lệ
    return render_template('index.html', error_message="Invalid file type.", result_image=None, detection_results=None)

if __name__ == '__main__':
    app.run(debug=True, port=5000)