import json
import random
import string
from collections import defaultdict

# List of common English words
common_words = [
    "the", "quick", "brown", "fox", "jumps", "over", "lazy", "dog", "hello", "world",
    "python", "hadoop", "mapreduce", "data", "science", "machine", "learning", "artificial", "intelligence",
    "big", "small", "large", "tiny", "huge", "run", "walk", "fly", "jump", "swim", "strike", "nike", "adidas", "white"
]

def generate_random_sentence(word_count, word_stats):
    words = random.choices(common_words, k=word_count)
    for word in words:
        word_stats[word] += 1
    return ' '.join(words)

def generate_json_file(file_name, word_count, max_words_per_sentence):
    data = []
    word_stats = defaultdict(int)
    total_words = 0

    while total_words < word_count:
        words_in_sentence = min(random.randint(1, max_words_per_sentence), word_count - total_words)
        sentence = generate_random_sentence(words_in_sentence, word_stats)
        data.append({"text": sentence})
        total_words += words_in_sentence

    with open(file_name, 'w') as f:
        json.dump(data, f, indent=4)  # Dump the entire list to the JSON file

    return word_stats

def save_word_stats(stats_file_name, word_stats):
    with open(stats_file_name, 'w') as f:
        json.dump(word_stats, f, indent=4)

if __name__ == "__main__":
    json_file_name = "large_input.json"
    stats_file_name = "word_stats.json"
    total_word_count = 100  # Total number of words to generate
    max_words_per_sentence = 15  # Maximum words per sentence

    word_stats = generate_json_file(json_file_name, total_word_count, max_words_per_sentence)
    save_word_stats(stats_file_name, word_stats)

    print(f"{json_file_name} generated with a total of {total_word_count} words.")
    print(f"{stats_file_name} generated with word counts.")