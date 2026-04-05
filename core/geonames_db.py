import os


class GeoNamesDB:

    def __init__(self):

        self.cities = set()

        path = os.path.join(
            os.path.dirname(__file__),
            "../data/cities500.txt"
        )

        with open(path, encoding="utf-8") as f:

            for line in f:

                parts = line.strip().split("\t")

                country = parts[8]

                # Collect ALL possible names
                names = set()

                names.add(parts[1].lower().strip())  # name
                names.add(parts[2].lower().strip())  # ascii name

                # alternate names
                if parts[3]:

                    for alt in parts[3].split(","):

                        names.add(
                            alt.lower().strip()
                        )

                # Store all variants
                for name in names:

                    self.cities.add(
                        (name, country)
                    )


    def is_real_city(self, name, country):

        return (
            name.lower().strip(),
            country
        ) in self.cities