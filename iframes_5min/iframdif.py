def extract_iframes(text):
    """Extract iframes from the given text."""
    iframes = []
    # Assuming iframes are enclosed within <iframe> tags
    start = text.find("<iframe")
    while start != -1:
        end = text.find("</iframe>", start)
        if end != -1:
            iframes.append(text[start:end + 9])  # Include the closing tag
            start = text.find("<iframe", end)
        else:
            break
    return iframes

def compare_iframes(file1_text, file2_text):
    """Compare iframes between two texts."""
    iframes_file1 = extract_iframes(file1_text)
    iframes_file2 = extract_iframes(file2_text)

    missing_in_file1 = [iframe for iframe in iframes_file2 if iframe not in iframes_file1]
    missing_in_file2 = [iframe for iframe in iframes_file1 if iframe not in iframes_file2]

    return missing_in_file1, missing_in_file2

# Read contents of the two files
with open("filea.txt", "r") as file1:
    file1_text = file1.read()

with open("fileb.txt", "r") as file2:
    file2_text = file2.read()
iframes_file1 = extract_iframes(file1_text)
iframes_file2 = extract_iframes(file2_text)
print("my lengths for 1")
print(len(iframes_file1))
print("my lengths for 2")
print(len(iframes_file2))
missing_in_file1, missing_in_file2 = compare_iframes(file1_text, file2_text)

print("Iframes missing in file1 but present in file2:")
print(len(missing_in_file1))
for iframe in missing_in_file1:
    print(iframe)

print("\nIframes missing in file2 but present in file1:")
print(len(missing_in_file2))
for iframe in missing_in_file2:
    print(iframe)
