import json
import random
from collections import defaultdict
from minio import Minio
import traceback
from io import BytesIO

# List of common English words
common_words = [
    "the", "quick", "brown", "fox", "jumps", "over", "lazy", "dog", "hello", "world",
    "python", "hadoop", "mapreduce", "data", "science", "machine", "learning", "artificial", "intelligence",
    "big", "small", "large", "tiny", "huge", "run", "walk", "fly", "jump", "swim", "strike", "nike", "adidas", "white",
    "green", "angry",
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

# Function to generate JSON data with specified total word count and maximum words per sentence
def generate_json_data(word_count, max_words_per_sentence, word_stats):
    data = []
    total_words = 0

    while total_words < word_count:
        words_in_sentence = min(random.randint(1, max_words_per_sentence), word_count - total_words)
        sentence = generate_random_sentence(words_in_sentence, word_stats)
        data.append({"text": sentence})
        total_words += words_in_sentence

    return json.dumps(data, indent=4), word_stats

# Function to save word statistics to a JSON string and return it
def generate_word_stats_json(word_stats):
    stats_json = json.dumps(word_stats, indent=4)
    print(stats_json)  # Print the JSON string
    return stats_json

# Function to upload data to MinIO bucket without saving locally
def upload_data_to_minio(bucket_name, object_name, data):
    try:
        # Check if bucket exists, create if not
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)

        # Upload data to MinIO
        data_stream = BytesIO(data.encode('utf-8'))
        minio_client.put_object(bucket_name, object_name, data_stream, len(data.encode('utf-8')))

        print(f"File '{object_name}' uploaded successfully to bucket '{bucket_name}'.")

    except Exception as e:
        print(f"An error occurred while uploading file '{object_name}' to bucket '{bucket_name}':")
        print(traceback.format_exc())  # Print full traceback for debugging
        print(f"Error details: {e}")

if __name__ == "__main__":
    json_file_name = "large_input2.json"
    stats_file_name = "word_stats2.json"
    total_word_count = 1000000  # Total number of words to generate
    max_words_per_sentence = 30  # Maximum words per sentence
    bucket_name = 'map-reduce-input-files'

    word_stats = defaultdict(int)
    json_data, word_stats = generate_json_data(total_word_count, max_words_per_sentence, word_stats)
    stats_data = generate_word_stats_json(word_stats)

    # Upload JSON data to MinIO bucket
    upload_data_to_minio(bucket_name, json_file_name, json_data)
    upload_data_to_minio(bucket_name, stats_file_name, stats_data)

    print(f"{json_file_name} generated with a total of {total_word_count} words and uploaded to MinIO.")
    print(f"{stats_file_name} generated with word counts and uploaded to MinIO bucket.")
