import re


def correct_prenom_nom(root):
    # on pourra utiliser ce module pour checker les adfresses douteuses
    items = root.findall(".//MotsAnonymises/MotAnonymise")
    pseudonymisations = {"Noms": {}, "Prenoms": {}, "Adresse": {}}
    for e in items:
        if e.find("Type").text == "Nom":
            if e.find("Mots").text.lower() in pseudonymisations["Noms"]:
                pseudonymisations["Noms"][e.find("Mots").text.lower()] += 1
            else:
                pseudonymisations["Noms"][e.find("Mots").text.lower()] = 1

    for e in items:
        if e.find("Type").text == "Prenom":
            if e.find("Mots").text.lower() in pseudonymisations["Prenoms"]:
                pass
            else:
                for nom in pseudonymisations["Noms"]:
                    if e.find("Mots").text.lower() in nom:
                        pseudonymisations["Prenoms"][e.find("Mots").text.lower()] = pseudonymisations["Noms"][nom]


def match_pseudonymes(root, text, path=""):
    items = root.findall(".//FichierResultat/Type[.='0']/../MotsAnonymises/MotAnonymise")
    annon_names_count = {}
    annon_first_names_count = {}
    annon_address_count = {}
    file_in_error = False

    annon_clean = {}

    for e in items:
        if e.find("Type").text == "Adresse":
            try:  # pour gérer les balises vides
                if e.find("Mots").text.lower() in annon_address_count:
                    annon_address_count[e.find("Mots").text.lower()] += 1
                else:
                    annon_address_count[e.find("Mots").text.lower()] = 1

            except:
                pass  # a refaire

        elif e.find("Type").text == "Prenom":
            try:  # pour gérer les balises vides
                name = e.find("Mots").text.lower()
                if name in annon_first_names_count:
                    annon_first_names_count[name] += 1
                else:
                    annon_first_names_count[name] = 1
            except:
                pass  # a refaire

        elif e.find("Type").text == "Nom":
            try:  # pour gérer les balises vides
                name = e.find("Mots").text.lower()
                if name in annon_names_count:
                    annon_names_count[name] += 1
                else:
                    annon_names_count[name] = 1
            except:
                pass  # a refaire

    for key in annon_names_count:

        if key not in annon_first_names_count:
            expected = annon_names_count[key]
        else:
            expected = annon_names_count[key] + annon_first_names_count[key]

        counted = len(re.findall("\\b{}\\b".format(key.replace("(", "\(").replace(")", "\)")), text, re.IGNORECASE))

        if counted > expected:

            # print("over reach {}".format(key))

            file_in_error = True


        elif counted < expected:
            understood = suggest_correction_names(expected, key, text, path)
            if not understood:
                # print("################ New file {}".format(path))
                # print("Expected to find {} {} time(s) and found it {} time(s)".format(key, expected, counted))
                file_in_error = True
            else:
                annon_clean[key] = [(pos[0], pos[1], "PER_NOM") for pos in understood]
        else:
            annon_clean[key] = [(m.start(0), m.end(0), "PER_NOM") for m in
                                re.finditer("\\b{}\\b".format(key.replace("(", "\(").replace(")", "\)")), text,
                                            re.IGNORECASE)]

    for key in annon_first_names_count:

        if key not in annon_names_count:
            expected = annon_first_names_count[key]
        else:
            continue

        counted = len(re.findall("\\b{}\\b".format(key.replace("(", "\(").replace(")", "\)")), text, re.IGNORECASE))

        if counted > expected:

            #print("Expected to find {} {} time(s) and found it {} time(s) in file {}".format(key, expected, counted,
            #                                                                                 path))
            file_in_error = True


        elif counted < expected:
            understood = suggest_correction_names(expected, key, text, path)
            if not understood:
                # print("################ New file {}".format(path))
                # print("Expected to find {} {} time(s) and found it {} time(s)".format(key, expected, counted))
                file_in_error = True
            else:
                annon_clean[key] = [(pos[0], pos[1], "PER_PRENOM") for pos in understood]
        else:
            annon_clean[key] = [(m.start(0), m.end(0), "PER_PRENOM") for m in
                                re.finditer("\\b{}\\b".format(key.replace("(", "\(").replace(")", "\)")), text,
                                            re.IGNORECASE)]

    for key in annon_address_count:
        expected = annon_address_count[key]
        counted = len(re.findall(key.replace("(", "\(").replace(")", "\)"), text, re.IGNORECASE))
        if counted > expected:

            file_in_error = True
            # print("over reach adress")


        elif counted < expected:

            understood = suggest_correction_adresses(expected, key, text)
            if not understood:
                # print("################ New file {}".format(path))
                # print("Expected to find adress {} {} time(s) and found it {} time(s)".format(key, expected, counted))
                file_in_error = True
            else:
                annon_clean[key] = [(pos[0], pos[1], "LOC") for pos in understood]

        else:
            annon_clean[key] = [(m.start(0), m.end(0), "LOC") for m in
                                re.finditer(key.replace("(", "\(").replace(")", "\)"), text, re.IGNORECASE)]

    if file_in_error:
        return False
    else:
        return annon_clean


def suggest_correction_names(expected, key, text, path):
    if expected == len(re.findall("\\b{}\\b".format(key.replace("(", "\(").replace(")", "\)")), re.sub(' +', ' ', text),
                                  re.IGNORECASE)):
        # Doubles espaces corrigible en matchant première partie
        # done
        corrected_positions = []
        key_elements = key.split()

        occurences = re.finditer("\\b{}\\b".format(key_elements[0].replace("(", "\(").replace(")", "\)")), text,
                                 re.IGNORECASE)

        for occurence in occurences:
            text_truncated = text[occurence.start(0):]
            splitted_text_truncated = text_truncated.split()
            valid = True

            for i in range(len(key_elements)):
                # print(key_elements[i],re.sub('[^A-Za-z0-9]+', ' ', splitted_text_truncated[i]).lower())
                if not key_elements[i] == re.sub('[^A-Za-z0-9]+', '', splitted_text_truncated[i]).lower():
                    valid = False
            if valid:
                end = re.search(re.sub('[^A-Za-z0-9]+', '', key_elements[-1]), text_truncated, re.IGNORECASE).end(0)

                # print(text_truncated[0:end])
                # print(text[occurence.start(0):occurence.start(0)+end])
                corrected_positions.append((occurence.start(0), occurence.start(0) + end))
        if len(corrected_positions) == expected:

            return corrected_positions
        else:
            #print("name 1")
            return False



    elif expected == len(
            re.findall("\\b{}\\b".format(key.replace("(", "\(").replace(")", "\)")), text.replace("\n", " "),
                       re.IGNORECASE)):
        # retours lignes à la place d'un espace
        # done

        corrected_positions = re.finditer("\\b{}\\b".format(key.replace("(", "\(").replace(")", "\)")),
                                          text.replace("\n", " "), re.IGNORECASE)
        corrected_positions = [(m.start(0), m.end(0)) for m in corrected_positions]
        if len(corrected_positions) == expected:
            # print("victory")
            return corrected_positions
        else:
            #print("name 2")
            return False


    elif expected == len(re.findall("\\b{}\\b".format(key.replace("(", "\(").replace(")", "\)")),
                                    re.sub(' +', ' ', text.replace("\n", "")), re.IGNORECASE)):
        # Doubles espaces et retours lignes à la place d'un espace
        # done

        corrected_positions = []
        key_elements = re.split('(-)', key)
        occurences = re.finditer("\\b{}\\b".format(key_elements[0].replace("(", "\(").replace(")", "\)")), text,
                                 re.IGNORECASE)

        for occurence in occurences:

            text_truncated = text[occurence.start(0):]

            splitted_text_truncated = re.split('(-| )\s*', text_truncated.replace("\n", " "))
            valid = True
            for i in range(len(key_elements)):
                # print(key_elements[i],re.sub('[^A-Za-z0-9-]+', '', splitted_text_truncated[i]).lower())
                if not key_elements[i] == re.sub('[^A-Za-z0-9-]+', '', splitted_text_truncated[i]).lower():
                    valid = False
            if valid:
                end = re.search(re.sub('[^A-Za-z0-9-]+', '', key_elements[-1]), text_truncated, re.IGNORECASE).end(0)

                # print(text_truncated[0:end])
                # print(text[occurence.start(0):occurence.start(0)+end])
                corrected_positions.append((occurence.start(0), occurence.start(0) + end))
        if len(corrected_positions) == expected:
            # print("victory")
            return corrected_positions
        else:
            #print("name 3")
            return False


    elif expected == len(re.findall("\\b{}\\b".format(key.replace("(", "\(").replace(")", "\)")),
                                    re.sub(' +', '', text.replace("\n", "")), re.IGNORECASE)):
        # Retours à la ligne et tabulations en début de ligne
        # print("type 1")
        #print("name 4")
        return False
    elif expected == len(re.findall("\\b{}\\b".format(key.replace("(", "\(").replace(")", "\)")),
                                    re.sub(' +', ' ', text.replace("\n", " ").replace("|", " ")), re.IGNORECASE)):
        # Retours à la ligne et tabulations en début de ligne
        # print(key, expected)
        # print(path)
        # print("type 2")
        corrected_positions = []
        key_elements = key.split()

        occurences = re.finditer("\\b{}\\b".format(key_elements[0].replace("(", "\(").replace(")", "\)")), text,
                                 re.IGNORECASE)

        for occurence in occurences:
            text_truncated = text[occurence.start(0):]
            splitted_text_truncated = text_truncated.split()
            valid = True

            for i in range(len(key_elements)):
                # print(key_elements[i],re.sub('[^A-Za-z0-9]+', ' ', splitted_text_truncated[i]).lower())
                if not key_elements[i] == re.sub('[^A-Za-z0-9]+', '', splitted_text_truncated[i]).lower():
                    valid = False
            if valid:
                end = re.search(re.sub('[^A-Za-z0-9]+', '', key_elements[-1]), text_truncated, re.IGNORECASE).end(0)

                # print(text_truncated[0:end])
                # print(text[occurence.start(0):occurence.start(0)+end])
                corrected_positions.append((occurence.start(0), occurence.start(0) + end))
        if len(corrected_positions) == expected:

            return corrected_positions
        else:
            #print("name 5")
            return False


    elif expected == len(re.findall("\\b{}\\b".format(key.replace("(", "\(").replace(")", "\)")),
                                    re.sub(' +', ' ', text.replace("\n-", "-").replace("-\n", "-").replace("\n", " ")),
                                    re.IGNORECASE)):
        # Retours à la ligne et tabulations en début de ligne
        # compliqué
        # print(key, expected)
        # print(path)
        # print("type 3")

        corrected_positions = []

        key_elements = re.split('(-)', key)
        occurences = re.finditer("\\b{}\\b".format(key_elements[0]), text, re.IGNORECASE)

        for occurence in occurences:

            text_truncated = text[occurence.start(0):]

            splitted_text_truncated = re.split('(-|-\n|\n-|\s)', text_truncated)

            # print(splitted_text_truncated[0:5])
            valid = True
            for i in range(len(key_elements)):
                # print(key_elements[i],re.sub('[^A-Za-z0-9-]+', '', splitted_text_truncated[i]).lower())
                if not key_elements[i] == re.sub('[^A-Za-z0-9-]+', '', splitted_text_truncated[i]).lower():
                    valid = False
            if valid:
                end = re.search(re.sub('[^A-Za-z0-9-]+', '', key_elements[-1]), text_truncated, re.IGNORECASE).end(0)

                # print(text_truncated[0:end])
                # print(text[occurence.start(0):occurence.start(0)+end])
                corrected_positions.append((occurence.start(0), occurence.start(0) + end))
        if len(corrected_positions) == expected:
            # print("victory")
            return corrected_positions
        else:
            #print("name 6")
            return False


    else:
        #print("unknown")
        return False


def suggest_correction_adresses(expected, key, text):
    if expected <= len(
            re.findall("{}".format(key.replace("(", "\(").replace(")", "\)")), re.sub(' +', ' ', text), re.IGNORECASE)):
        # Doubles espaces corrigible en matchant première partie

        # Doubles espaces corrigible en matchant première partie

        # print(key, expected)
        corrected_positions = []
        key_elements = key.split()

        occurences = re.finditer("{}".format(key_elements[0].replace("(", "\(").replace(")", "\)")), text,
                                 re.IGNORECASE)

        for occurence in occurences:
            text_truncated = text[occurence.start(0):]
            splitted_text_truncated = text_truncated.split()
            valid = True

            for i in range(len(key_elements)):
                # print(key_elements[i], splitted_text_truncated[i].lower())
                if not key_elements[i] == splitted_text_truncated[i].lower():
                    valid = False
            if valid:
                end = re.search(re.sub('[^A-Za-z0-9]+', '', key_elements[-1]), text_truncated, re.IGNORECASE).end(0)

                # print(text_truncated[0:end])
                # print(text[occurence.start(0):occurence.start(0)+end])
                corrected_positions.append((occurence.start(0), occurence.start(0) + end))

        if len(corrected_positions) == expected:

            return corrected_positions
        else:
            #print("adress 1")
            return False


    elif expected <= len(re.findall("{}".format(key.replace("(", "\(").replace(")", "\)")),
                                    re.sub(' +', ' ', text.replace("\n", " ")), re.IGNORECASE)):
        # retours lignes à la place d'un espace
        # done

        # print(key, expected)

        corrected_positions = []
        key_elements = key.split()

        occurences = re.finditer("{}".format(key_elements[0].replace("(", "\(").replace(")", "\)")), text,
                                 re.IGNORECASE)

        for occurence in occurences:
            text_truncated = text[occurence.start(0):].replace("\n", " ")
            splitted_text_truncated = text_truncated.split()
            valid = True

            for i in range(len(key_elements)):
                # print(key_elements[i], splitted_text_truncated[i].lower())
                if not key_elements[i] == splitted_text_truncated[i].lower():
                    valid = False
            if valid:
                # des erruers se produisent ici

                end = re.search(re.sub('[^A-Za-z0-9]+', '', key_elements[-1]), text_truncated, re.IGNORECASE).end(0)

                # print(text_truncated[0:end])
                # print(text[occurence.start(0):occurence.start(0)+end])
                corrected_positions.append((occurence.start(0), occurence.start(0) + end))

        if len(corrected_positions) == expected:
            return corrected_positions

        else:
            #print("adress 2")
            return False


    elif expected <= len(re.findall("{}".format(key.replace("(", "\(").replace(")", "\)")),
                                    re.sub(' +', ' ', text.replace("\n", "")), re.IGNORECASE)):
        # Doubles espaces et retours lignes à la place d'un espace
        #print("adress 3")
        return False
    elif expected <= len(
            re.findall("{}".format(key.replace("(", "\(").replace(")", "\)")), re.sub(' +', '', text.replace("\n", "")),
                       re.IGNORECASE)):
        # Retours à la ligne et tabulations en début de ligne
        #print("adress 4")
        return False
    elif expected <= len(re.findall("{}".format(key.replace("(", "\(").replace(")", "\)")),
                                    re.sub(' +', ' ', text.replace("\n", " ").replace("|", " ")), re.IGNORECASE)):
        # Retours à la ligne et tabulations en début de ligne
        #print("adress 5")
        return False
    elif expected <= len(re.findall("{}".format(key.replace("(", "\(").replace(")", "\)")),
                                    re.sub(' +', ' ', text.replace("\n-", "-").replace("-\n", "-").replace("\n", " ")),
                                    re.IGNORECASE)):
        # Retours à la ligne et tabulations en début de ligne
        #print("adress 6")
        return False
    else:
        #print("adress unknown")
        return False
