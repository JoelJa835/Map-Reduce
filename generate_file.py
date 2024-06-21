import json
import random
import string
from collections import defaultdict
from minio import Minio
import traceback

# List of common English words
common_words = [
    "the", "quick", "brown", "fox", "jumps", "over", "lazy", "dog", "hello", "world",
    "python", "hadoop", "mapreduce", "data", "science", "machine", "learning", "artificial", "intelligence",
    "big", "small", "large", "tiny", "huge", "run", "walk", "fly", "jump", "swim", "strike", "nike", "adidas", "white"
]

# MinIO server details (replace with your actual MinIO server endpoint and credentials)
MINIO_ENDPOINT = "83.212.78.127:30000"
ACCESS_KEY = "dena"
SECRET_KEY = "dena1234"
secure = False  # Change to True if MinIO is configured with TLS

# Initialize MinIO client
minio_client = Minio(MINIO_ENDPOINT, access_key=ACCESS_KEY, secret_key=SECRET_KEY, secure=secure)

# Function to generate a random sentence with specified word count and update word statistics
def generate_random_sentence(word_count, word_stats):
    words = random.choices(common_words, k=word_count)
    for word in words:
        word_stats[word] += 1
    return ' '.join(words)

# Function to generate JSON file with specified total word count and maximum words per sentence
def generate_json_file(file_name, word_count, max_words_per_sentence, word_stats):
    data = []
    total_words = 0

    while total_words < word_count:
        words_in_sentence = min(random.randint(1, max_words_per_sentence), word_count - total_words)
        sentence = generate_random_sentence(words_in_sentence, word_stats)
        data.append({"text": sentence})
        total_words += words_in_sentence

    with open(file_name, 'w') as f:
        json.dump(data, f, indent=4)  # Dump the entire list to the JSON file

    return word_stats

# Function to save word statistics to a JSON file
def save_word_stats(stats_file_name, word_stats):
    with open(stats_file_name, 'w') as f:
        json.dump(word_stats, f, indent=4)

# Function to upload file to MinIO bucket
def upload_file_to_minio(bucket_name, object_name, file_path):
    try:
        # Check if bucket exists, create if not
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)

        # Upload file to MinIO
        minio_client.fput_object(bucket_name, object_name, file_path)

        print(f"File '{object_name}' uploaded successfully to bucket '{bucket_name}'.")

    except Exception as e:
        print(f"An error occurred while uploading file '{object_name}' to bucket '{bucket_name}':")
        print(traceback.format_exc())  # Print full traceback for debugging
        print(f"Error details: {e}")

if __name__ == "__main__":
    json_file_name = "large_input.json"
    stats_file_name = "word_stats.json"
    total_word_count = 10000000  # Total number of words to generate
    max_words_per_sentence = 15  # Maximum words per sentence
    bucket_name = 'map-reduce-input-files'

    word_stats = defaultdict(int)
    word_stats = generate_json_file(json_file_name, total_word_count, max_words_per_sentence, word_stats)
    save_word_stats(stats_file_name, word_stats)

    # Upload files to MinIO bucket
    upload_file_to_minio(bucket_name, json_file_name, json_file_name)
    upload_file_to_minio(bucket_name, stats_file_name, stats_file_name)

    print(f"{json_file_name} generated with a total of {total_word_count} words.")
    print(f"{stats_file_name} generated with word counts and uploaded to MinIO bucket.")

