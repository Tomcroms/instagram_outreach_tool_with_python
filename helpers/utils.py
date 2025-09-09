import os
import datetime
import time
import random
import bcrypt

class DataCapacities:
    def garder_seulement_les_targets_pas_encore_contactees(base_directory_path):

        chemin_fichier1 = os.path.join(base_directory_path, "all_targets.txt")
        chemin_fichier2 = os.path.join(base_directory_path, "contacted_targets.txt")
        chemin_fichier3 = os.path.join(base_directory_path, "remaining_targets.txt")

        # Lire les lignes de chaque fichier
        with open(chemin_fichier1, "r", encoding="utf-8") as fichier1:
            lignes_fichier1 = set(fichier1.read().splitlines())

        with open(chemin_fichier2, "r", encoding="utf-8") as fichier2:
            lignes_fichier2 = set(fichier2.read().splitlines())

        # Trouver la différence entre les ensembles
        comptes_a_garder = lignes_fichier1 - lignes_fichier2

        # Écrire dans le troisième fichier
        with open(chemin_fichier3, "w", encoding="utf-8") as fichier3:
            for compte in comptes_a_garder:
                fichier3.write(compte + "\n")

    def add_new_contacted_target(base_directory_path, target):
        contacted_targets_path = os.path.join(base_directory_path, "contacted_targets.txt")

        with open(contacted_targets_path, "a", encoding="utf-8") as fichier:
            fichier.write(target + "\n")  # ajouter un saut de ligne après chaque nom d'utilisateur

    def getTargets(base_directory_path):
        remaining_targets_path = os.path.join(base_directory_path, "remaining_targets.txt")

        with open(remaining_targets_path, "r") as file:
            targets = [target.strip() for target in file.read().split("\n")]

        return targets

    def delete_duplicates(file_path):
        unique_lines = set()
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                unique_lines.add(line)

        # Écrire les lignes uniques dans un nouveau fichier
        with open(file_path, 'w', encoding='utf-8') as file:
            for line in unique_lines:
                file.write(line)

    def write_old_and_new_usernames(old_username, new_username):
        file_path = os.path.join("C:/Users/thoma/OneDrive/Documents/Socialify/BOT/BASES/accounts/", "old_new_usernames.txt")

        with open(file_path, "a", encoding="utf-8") as fichier:
            fichier.write(old_username + " - " + new_username + "\n")  # ajouter un saut de ligne après chaque nom d'utilisateur

    ##SCRAPPING SIMILAR ACCOUNTS
    def remove_used_for_similar_scrapping(base_directory_path):
        chemin_fichier1 = os.path.join(base_directory_path, "all_possible_targets_username.txt")
        chemin_fichier2 = os.path.join(base_directory_path, "accounts_used_for_scrapping_similar_accounts.txt")
        chemin_fichier3 = os.path.join(base_directory_path, "remaining_targets_for_scrap.txt")
        # Lire les lignes de chaque fichier
        with open(chemin_fichier1, "r", encoding="utf-8") as fichier1:
            lignes_fichier1 = set(fichier1.read().splitlines())

        with open(chemin_fichier2, "r", encoding="utf-8") as fichier2:
            lignes_fichier2 = set(fichier2.read().splitlines())

        # Trouver la différence entre les ensembles (éléments du fichier1 qui ne sont pas dans le fichier2)
        comptes_a_garder = lignes_fichier1 - lignes_fichier2

        # Écrire cet ensemble dans un troisième fichier
        with open(chemin_fichier3, "w", encoding="utf-8") as fichier3:
            for compte in comptes_a_garder:
                fichier3.write(compte + "\n")

    def add_to_all_possible_targets(possible_target_username, base_directory_path):
        chemin_fichier1 = os.path.join(base_directory_path, "all_possible_targets_username.txt")
        with open(chemin_fichier1, "a") as file:
            file.write(possible_target_username + "\n")

    def add_to_accounts_used_for_similar(account, base_directory_path):
        chemin_fichier1 = os.path.join(base_directory_path, "accounts_used_for_scrapping_similar_accounts.txt")
        with open(chemin_fichier1, "a") as file:
            file.write(account + "\n")

    def reload_possible_targets(self, lock):
        global possible_targets
        dossier_base = os.path.dirname(__file__)
        chemin_fichier1 = os.path.join(dossier_base, "all_possible_targets_username.txt")
        chemin_fichier2 = os.path.join(dossier_base, "remaining_targets_for_scrap.txt")
        self.delete_duplicates(chemin_fichier1)
        self.remove_used_for_similar_scrapping()
        with lock:
            with open(chemin_fichier2, "r") as file:
                new_targets = [target.strip() for target in file.read().split("\n")]
            possible_targets.clear()
            possible_targets.extend(new_targets)
            print(len(possible_targets))


    ##SCRAPPING
    def remove_already_scrapped_targets(base_directory_path):

        chemin_fichier1 = os.path.join(base_directory_path, "all_targets_scrapping.txt")
        chemin_fichier2 = os.path.join(base_directory_path, "scrapped_targets.txt")
        chemin_fichier3 = os.path.join(base_directory_path, "remaining_targets_for_scrap.txt")

        # Lire les lignes de chaque fichier
        with open(chemin_fichier1, "r", encoding="utf-8") as fichier1:
            lignes_fichier1 = set(fichier1.read().splitlines())

        with open(chemin_fichier2, "r", encoding="utf-8") as fichier2:
            lignes_fichier2 = set(fichier2.read().splitlines())

        # Trouver la différence entre les ensembles
        comptes_a_garder = lignes_fichier1 - lignes_fichier2

        # Écrire dans le troisième fichier
        with open(chemin_fichier3, "w", encoding="utf-8") as fichier3:
            for compte in comptes_a_garder:
                fichier3.write(compte + "\n")            

    def add_to_selected_targets(account, base_directory_path):
        chemin_fichier1 = os.path.join(base_directory_path, "selected_targets.txt")
        with open(chemin_fichier1, "a") as file:
            file.write(account + "\n")

    def add_scrapped_target(target, base_directory_path):
        chemin_fichier = os.path.join(base_directory_path, "scrapped_targets.txt")
        with open(chemin_fichier, "a", encoding="utf-8") as fichier:
            fichier.write(target + "\n")  # ajouter un saut de ligne après chaque nom d'utilisateur
    
    def getTargetsForScrap(base_directory_path):
        remaining_targets_path = os.path.join(base_directory_path, "remaining_targets_for_scrap.txt")
        with open(remaining_targets_path, "r") as file:
            targets = [target.strip() for target in file.read().split("\n")]

        return targets


    ##COMPUTING
    def generate_random_array_fixed_time(length, min_sum, max_sum, min_value, max_value):
        """
        Generate a random array of a given length where each element is between min_value and max_value,
        and the sum of the array is between min_sum and max_sum. This approach avoids the infinite loop
        by generating a valid array in a more deterministic manner.

        Parameters:
        length (int): Length of the array.
        min_sum (int): Minimum sum of the array elements.
        max_sum (int): Maximum sum of the array elements.
        min_value (int): Minimum value of each element in the array.
        max_value (int): Maximum value of each element in the array.

        Returns:
        list: A list of integers satisfying the given conditions.
        """
        # Initialize the array with minimum values
        array = [min_value] * length

        # Remaining sum to distribute
        remaining_sum = random.randint(min_sum, max_sum) - length * min_value

        for i in range(length):
            # Distribute the remaining sum randomly among the elements
            add = min(remaining_sum, max_value - min_value)
            array[i] += add
            remaining_sum -= add

            # If the remaining sum is zero, break the loop
            if remaining_sum == 0:
                break

        # Shuffle the array to ensure randomness
        random.shuffle(array)
        return array

    def generate_hash_password(self, password):
        # Générer un sel
        salt = bcrypt.gensalt()
        # Hacher le mot de passe avec le sel
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_password


class TextProcessor:
    def convert_to_int(text):
        text = text.lower()

        # Supprime les mots comme 'followers' et 'publications' et nettoie les espaces
        text = text.replace('followers', '').replace('publications', '').replace('suivi(e)s', '').replace("suivi(e)", "").replace("publication", "")

        # Remplace les espaces par rien pour gérer les nombres comme '1 048'
        number_str = text.replace(' ', '')
        
        # Remplace la virgule par un point pour une conversion en nombre décimal
        number_str = number_str.replace(',', '.')

        # Détecte l'unité (k ou m) sans tenir compte de la casse et multiplie par le nombre approprié
        if 'm' in number_str:
            # Retire l'unité et multiplie par un million
            number = float(number_str.replace('m', '')) * 1_000_000
        elif 'k' in number_str:
            # Retire l'unité et multiplie par mille
            number = float(number_str.replace('k', '')) * 1_000
        else:
            # Pour un nombre sans unité, convertit simplement en float
            number = float(number_str)
        
        # Convertit le résultat en un nombre entier si c'est possible sans perte d'information
        return int(number)

    def filter_profile_lines(input_file_path, output_file_path):
        with open(input_file_path, 'r', encoding='utf-8') as infile:
            lines = infile.readlines()

        filtered_lines = []

        for i, line in enumerate(lines):
            if line.startswith("Photo de profil"):
                if i + 1 < len(lines):
                    filtered_lines.append(lines[i + 1].strip())

        with open(output_file_path, 'w', encoding='utf-8') as outfile:
            outfile.write("\n".join(filtered_lines))


class TimeProcessor:
    def sleepToAround9am():
        now = datetime.datetime.now()

        nine_am_today = now.replace(hour=9, minute=0, second=0, microsecond=0)

        if now > nine_am_today:
            nine_am_today += datetime.timedelta(days=1)

        random_additional_time = datetime.timedelta(seconds=random.uniform(0, 624))
        target_time = nine_am_today + random_additional_time

        sleep_duration = (target_time - now).total_seconds()

        time.sleep(sleep_duration)







