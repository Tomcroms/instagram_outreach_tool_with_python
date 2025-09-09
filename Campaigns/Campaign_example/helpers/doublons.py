

def count_duplicates(input_list):
    frequency = {}
    for item in input_list:
        frequency[item] = frequency.get(item, 0) + 1

    nb = 0
    for item, count in frequency.items():
        if count > 1:
            nb+=1
            print(f"{item} appears {count} times")
    print(nb)

with open("", "r") as fichier:
    selected_targets = [target.strip() for target in fichier.read().split("\n")]
count_duplicates(selected_targets)


unique_item = set(selected_targets)
print(len(unique_item))

with open("", "w") as fichier:
    for target in unique_item:
        fichier.write(f"{target}\n")