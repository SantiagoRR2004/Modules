import numpy as np
import requests

class Address:
    def __init__(self, street: str, houseNumber: str, city: str, region: str, country: str, postalCode: str) -> None:
        """
        Initialize the Address object.

        Args:
            - street (str): The street name.
            - houseNumber (str): The house number.
            - city (str): The city name.
            - region (str): The region name.
            - country (str): The country name.
            - postalCode (str): The postal code.

        Returns:
            - None
        """
        self.street = street
        self.houseNumber = houseNumber
        self.city = city
        self.region = region
        self.country = country
        self.postalCode = postalCode
        self.setCoordinates()

    def queryNominatim(self) -> tuple[float, float] | tuple[None, None]:
        """
        Query Nominatim for the address and return latitude and longitude.

        Docs:
            - https://nominatim.org/release-docs/latest/api/Search/#structured-query

        Args:
            - None

        Returns:
            - tuple: (latitude, longitude)
        """
        url = "https://nominatim.openstreetmap.org/search"

        params = {
            "street": f"{self.houseNumber} {self.street}",
            "city": self.city,
            "region": self.region,
            "country": self.country,
            "postalcode": self.postalCode,
            "format": "json",
            "limit": 1
        }
        
        headers = {
            "User-Agent": "my-geocoder/1.0"
        }

        # Photon is so slow that we can't hit the Nominatim rate limit
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()

        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
        else:
            return None, None


    def queryPhoton(self) -> tuple[float, float] | tuple[None, None]:
        """
        Query Photon for the address and return latitude and longitude.

        Args:
            - None

        Returns:
            - tuple: (latitude, longitude)
        """
        base = "https://photon.komoot.io/api"


        parts = [
            self.houseNumber,
            self.street,
            self.postalCode,
            self.city,
            self.region,
            self.country
        ]


        # Build free-form query
        q = ", ".join(parts).strip()

        params = {
            "q": q,
            "limit": 1,    
        }

        try:
            resp = requests.get(base, params=params)
            resp.raise_for_status()
            data = resp.json()
            features = data.get("features", [])

            if features:
                coords = features[0]["geometry"]["coordinates"]  # [lon, lat]
                lon, lat = coords[0], coords[1]
                return float(lat), float(lon)
            
        except (requests.RequestException, ValueError, KeyError):
            pass

        return None, None

    def setCoordinates(self) -> None:
        """
        Set the coordinates of the address.

        Args:
            - None

        Returns:
            - None
        """
        self.lats = []
        self.lons = []

        functions = [self.queryNominatim, self.queryPhoton]

        for func in functions:
            lat, lon = func()
            if lat is not None and lon is not None:
                self.lats.append(lat)
                self.lons.append(lon)

    def getCoordinates(self) -> tuple[float, float]:
        """
        Get the coordinates of the address by
        returning the average of the latitude and longitude.

        Args:
            - None

        Returns:
            - tuple: (latitude, longitude)
        """
        return np.mean(self.lats), np.mean(self.lons)
