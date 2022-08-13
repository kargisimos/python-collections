#this script takes a readable file as input
#and converts it's content using the rot13
#cipher. Saves output in <filename>_rot13.
#Note: Since the rot13 cipher is reversible,
#you can use this script for both encryption
#and decryption.  

import sys

alphabet = 'abcdefghijklmnopqrstuvwxyz'

def check_args():
    if len(sys.argv) != 2:
        print(f'Usage: python3 {sys.argv[0]} <filename>')
        sys.exit(1)

def rot13(message):
    with open(f"{sys.argv[1]}_rot13",'at') as f:
        ciphertext = ''.join([alphabet[(alphabet.find(letter) + 13) % 26] if letter.isalpha() else letter for letter in message.lower()])
        f.write(''.join([ciphertext[index] if message[index].islower() else ciphertext[index].upper() if message[index].isupper() else ciphertext[index] for index in range(len(message))]) + '\n')


check_args()
try:
    with open(sys.argv[1],'rt') as f:
        message = f.readlines()
    for m in message:
        rot13(m.strip())
except Exception as e:
    print(f"An error occured...{e}")
    sys.exit(1)
