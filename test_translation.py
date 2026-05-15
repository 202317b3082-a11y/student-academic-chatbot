#!/usr/bin/env python
"""
Test script to verify translation flow works end-to-end
"""
from translate import translate_to_english, translate_from_english

print("=" * 60)
print("TESTING TRANSLATION FLOW")
print("=" * 60)

# Test 1: Hindi to English
print("\n[TEST 1] Hindi → English")
print("-" * 60)
hindi_text = "सीजीपीए कैसे चेक करें?"
print(f"Input (Hindi): {hindi_text}")

result1 = translate_to_english(hindi_text, "Hindi")
print(f"Success: {result1['success']}")
print(f"Output (English): {result1['translated_text']}")

if not result1['success']:
    print(f"Error: {result1.get('error')}")

# Test 2: English to Hindi
print("\n[TEST 2] English → Hindi")
print("-" * 60)
english_text = "How can I check my CGPA?"
print(f"Input (English): {english_text}")

result2 = translate_from_english(english_text, "Hindi")
print(f"Success: {result2['success']}")
print(f"Output (Hindi): {result2['translated_text']}")

if not result2['success']:
    print(f"Error: {result2.get('error')}")

# Test 3: Round-trip (Hindi → English → Hindi)
print("\n[TEST 3] Round-trip: Hindi → English → Hindi")
print("-" * 60)
original_hindi = "मुझे प्रोजेक्ट वीवा के बारे में जानना है"
print(f"Original (Hindi): {original_hindi}")

# Step 1: Hindi to English
step1 = translate_to_english(original_hindi, "Hindi")
english = step1['translated_text']
print(f"Step 1 (English): {english}")

# Step 2: English to Hindi
step2 = translate_from_english(english, "Hindi")
back_to_hindi = step2['translated_text']
print(f"Step 2 (Hindi): {back_to_hindi}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
