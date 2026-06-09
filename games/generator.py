import random

# write your views here
def generate_even_puzzle():

    even_numbers = random.sample(range(2, 50, 2),5)

    odd_number = random.choice(range(1, 50, 2))

    numbers = even_numbers + [odd_number]
    random.shuffle(numbers)
    return {

        "numbers": numbers,
        "answer": odd_number,
        "category": "Odd"
    }


def generate_odd_puzzle():

    odd_numbers = random.sample(
        range(1, 50, 2),
        5
    )
    even_number = random.choice(
        range(2, 50, 2)
    )
    numbers = odd_numbers + [even_number]
    random.shuffle(numbers)
    return {
        "numbers": numbers,
        "answer": even_number,
        "category": "Even"
    }

def generate_prime_puzzle():
    prime_numbers = random.sample(
        [2,3,5,7,11,13,17,19,23,29],
        5
    )
    non_prime = random.choice(
        [4,6,8,9,10,12,14,15,16]
    )
    numbers = prime_numbers + [non_prime]
    random.shuffle(numbers)
    return {
        "numbers": numbers,
        "answer": non_prime,
        "category": "Non Prime"
    }

def master_puzzle():
    generators = [
        # Know this is not a dictionary 
        generate_even_puzzle,
        generate_odd_puzzle,
        generate_prime_puzzle
    ]
    chosen = random.choice(generators)
    # And this do execute the list of the functions
    return chosen()