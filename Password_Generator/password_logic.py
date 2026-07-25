"""
password_logic.py - Pure logic for the Password Generator (Advanced Tier)
------------------------------------------------------------------------------
Kept separate from the GUI so the generation and strength-scoring logic
can be tested on its own, without opening a window.

Uses the `secrets` module (not `random`) because `secrets` is Python's
cryptographically secure random number generator - the right choice
any time randomness is used for something security-related, like
passwords or tokens.
"""

import secrets
import string

AMBIGUOUS_CHARACTERS = "0O1lI"


def build_pools(use_upper, use_lower, use_digits, use_symbols, exclude_ambiguous):
    """
    Return a dict of {type_name: character_pool_string} for every
    character type the user selected, with ambiguous characters
    removed if requested.
    """
    pools = {}
    if use_upper:
        pools["upper"] = string.ascii_uppercase
    if use_lower:
        pools["lower"] = string.ascii_lowercase
    if use_digits:
        pools["digits"] = string.digits
    if use_symbols:
        pools["symbols"] = "!@#$%^&*()-_=+"

    if exclude_ambiguous:
        for key, pool in pools.items():
            pools[key] = "".join(c for c in pool if c not in AMBIGUOUS_CHARACTERS)

    return pools


def secure_shuffle(characters):
    """
    Shuffle a list of characters using the `secrets` module instead of
    `random.shuffle`, via the Fisher-Yates algorithm, so the character
    order in the final password is also cryptographically unpredictable.
    """
    characters = list(characters)
    for i in range(len(characters) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        characters[i], characters[j] = characters[j], characters[i]
    return characters


def generate_password(length, use_upper, use_lower, use_digits, use_symbols,
                       exclude_ambiguous=False):
    """
    Generate a password of the given length that is GUARANTEED to
    contain at least one character from every selected type.

    Raises ValueError if no character types are selected, or if the
    length is too short to fit one of each selected type.
    """
    pools = build_pools(use_upper, use_lower, use_digits, use_symbols, exclude_ambiguous)

    if not pools:
        raise ValueError("Select at least one character type.")
    if length < len(pools):
        raise ValueError(
            f"Length must be at least {len(pools)} to include one of each selected type."
        )

    # Step 1: guarantee one character from each selected pool
    password_chars = [secrets.choice(pool) for pool in pools.values()]

    # Step 2: fill the rest of the length from the combined pool
    combined_pool = "".join(pools.values())
    remaining = length - len(password_chars)
    password_chars += [secrets.choice(combined_pool) for _ in range(remaining)]

    # Step 3: shuffle so the guaranteed characters aren't always at the front
    password_chars = secure_shuffle(password_chars)

    return "".join(password_chars)


def password_strength(length, num_types_selected):
    """
    Score a password's strength as 'Weak', 'Medium', or 'Strong' based
    on its length and how many character types it draws from.
    """
    score = 0
    if length >= 8:
        score += 1
    if length >= 12:
        score += 1
    if length >= 16:
        score += 1
    score += max(0, num_types_selected - 1)  # 0 to 3 extra points

    if score <= 2:
        return "Weak"
    elif score <= 4:
        return "Medium"
    else:
        return "Strong"
