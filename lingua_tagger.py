import os
import subprocess
import sys

# ==========================================
# 🧬 DR. LINGUA CONFIGURATION (PRIORITY EDITION)
# ==========================================

HURGHADA_LAT = "27.2579"
HURGHADA_LON = "33.8116"
AUTHOR = "Dr. Lingua | LinguaPharm"
COPYRIGHT = "© 2025 LinguaPharm.com - All Rights Reserved"
WEBSITE = "https://lingua-pharm.com"

# PRIORITY TAGS: These will ALWAYS appear first in the keyword list.
BASE_KEYWORDS = [
    "Hurghada Pharmacy",
    "Pharmacy near me",
    "Dr. Lingua",
    "Red Sea Medical Delivery",
    "Original Medication",
    "Makadi Bay Pharmacy",
    "Soma Bay Pharmacy",
    "Sahl Hasheesh Pharmacy",
    "Antibiotics",
    "Amoxicillin",
]

# NOISE FILTER: Words to strip from the Keyword Tags
STOP_WORDS = {
    "ar", "en", "box", "side", "view", "front", "back", "strip",
    "bottle", "mark", "packaging", "tablets", "capsules", "pills",
    "of", "and", "or", "for", "the", "in", "with", "tract", "tissue", "soft", "coated",
    "mg", "g", "1g", "ml", "16", "14", "20", "10", "12", "30", "312.5mg", "457mg", "70ml", "80ml", "625mg", "642.9mg", "75ml", "15", "500mg", "e", "mox", "n", "60ml", "50ml"
}

# Suffix Mapping for Human-Readable Titles
SUFFIX_MAP = {
    "-ar": "Arabic Box Side",
    "-en": "English Box Side",
    "-strip": "Blister Strip View",
    "-strip-front": "Blister Strip Front View",
    "-strip-back": "Blister Strip Back View",
    "-mark": "Bottle Reconstitution Level Mark",
    "-bottle": "Syrup Bottle View",
}

# ==========================================
# ⚙️ THE LOGIC LAYER
# ==========================================


def get_images(directory):
    """Scans for valid image formats."""
    return [f for f in os.listdir(directory) if f.lower().endswith(('.webp', '.png', '.jpg', '.jpeg'))]


def clean_product_title(filename):
    """
    Creates the 'Human Title'.
    Ex: 'Hibiotic 625Mg - Arabic Packaging'
    """
    name_no_ext = filename.rsplit('.', 1)[0]
    detected_suffix_text = ""
    clean_base_name = name_no_ext

    for suffix, text in sorted(SUFFIX_MAP.items(), key=lambda x: -len(x[0])):
        if name_no_ext.endswith(suffix):
            detected_suffix_text = text
            clean_base_name = name_no_ext[:-len(suffix)]
            break

    final_base = clean_base_name.replace("-", " ").replace("_", " ").title()

    if detected_suffix_text:
        return f"{final_base} - {detected_suffix_text}"
    else:
        return final_base


def generate_priority_keywords(filename_base, category, ailment):
    """
    Generates an ORDERED list of keywords.
    1. Base Keywords (First)
    2. Category
    3. Ailment
    4. Filename Specifics
    """
    final_keywords_list = []
    seen_words = set()  # To track duplicates without losing order

    def add_keyword(word):
        # clean the word
        clean = word.strip().title()
        lower_clean = clean.lower()

        # Check if valid
        if lower_clean not in STOP_WORDS and len(lower_clean) > 1:
            # Check for duplicates
            if lower_clean not in seen_words:
                final_keywords_list.append(clean)
                seen_words.add(lower_clean)

    # 1. Add BASE_KEYWORDS (They get absolute priority)
    for kw in BASE_KEYWORDS:
        # We assume Base Keywords are phrases, add them directly
        # But we still check duplication just in case
        if kw.lower() not in seen_words:
            final_keywords_list.append(kw)
            seen_words.add(kw.lower())

    # 2. Add Category words
    for word in category.split():
        add_keyword(word)

    # 3. Add Ailment Keywords
    # Split by comma or space
    raw_ailment_words = ailment.replace(",", " ").split()
    for word in raw_ailment_words:
        add_keyword(word)

    # 4. Add Filename Keywords
    raw_filename_words = filename_base.replace("-", " ").lower().split()
    for word in raw_filename_words:
        if not word.isdigit():  # Skip numbers
            add_keyword(word)

    return final_keywords_list


def generate_quantum_description(product_title, ailment):
    """
    Generates the Natural Language Description.
    """
    base_name = product_title.split(" - ")[0]

    return (
        f"{base_name}. Verified authentic medication recommended by Dr. Lingua for {ailment.lower()}. "
        f"Essential for tourist health in the Red Sea. "
        f"Available for express hotel delivery in Hurghada (Mamsha/Sheraton/Dahar/Kawther/and more), "
        f"Sahl Hasheesh, Makadi Bay, Soma Bay. Nationwide Shipping to Cairo, Alexandria, Luxor, "
        f"and all Egyptian Governorates (via Aramex, Bosta and Mylerz) via Lingua-Pharm.com."
    )


def tag_image(filename, category, ailment):

    # 1. Generate Data
    product_title = clean_product_title(filename)
    description = generate_quantum_description(product_title, ailment)

    # Generate ORDERED keywords
    keywords_list = generate_priority_keywords(
        filename.rsplit('.', 1)[0], category, ailment)

    # Join keywords with commas, maintaining order
    keyword_string = ", ".join(keywords_list)

    cmd = [
        'exiftool',
        '-overwrite_original',

        # A. Location
        f'-GPSLatitude={HURGHADA_LAT}',
        f'-GPSLongitude={HURGHADA_LON}',
        '-GPSLatitudeRef=N',
        '-GPSLongitudeRef=E',

        # B. Titles & Description
        f'-XMP:Title={product_title}',
        f'-XMP:Description={description}',
        f'-ImageDescription={description}',

        # C. Taxonomy (Keywords - Ordered)
        f'-XMP:Subject={keyword_string}',
        f'-IPTC:Keywords={keyword_string}',

        # D. Authority
        f'-XMP:Creator={AUTHOR}',
        f'-Artist={AUTHOR}',
        f'-Copyright={COPYRIGHT}',
        f'-XMP:Rights={COPYRIGHT}',
        f'-XMP:WebStatement={WEBSITE}',

        filename
    ]

    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL,
                       stderr=subprocess.PIPE)
        print(f"✅ [TAGGED] {filename}")
        print(f"   └── Tags (First 3): {keywords_list[:3]}...")  # Verification
    except subprocess.CalledProcessError as e:
        print(f"❌ [ERROR] Failed to tag {filename}")


def main():
    print("==================================================")
    print("🧬 DR. LINGUA QUANTUM TAGGER (v5.1 PRIORITY)")
    print("==================================================")

    images = get_images(os.getcwd())

    if not images:
        print("⚠️  No images found. Please run this inside your 'images' folder.")
        return

    print(f"🔍 Found {len(images)} images to process.")
    print("--- BATCH CONFIGURATION ---")

    # User Inputs
    category_input = input(
        "👉 Enter Main Category (e.g., Antibiotics): ").strip()
    ailment_input = input(
        "👉 Enter Main Ailment/Use (e.g., Bacterial Infection, Dental): ").strip()

    print("\n🚀 Injecting Priority Metadata...\n")

    for img in images:
        tag_image(img, category_input, ailment_input)

    print("\n==================================================")
    print("🎉 MISSION COMPLETE. Base Keywords set to Priority #1.")
    print("==================================================")


if __name__ == "__main__":
    main()
