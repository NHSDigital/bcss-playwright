import random
import datetime
from typing import Dict
import logging
from classes.organisation_complex import Organisation
from classes.gender_type import GenderType
from classes.address import Address
from classes.person import Person
from classes.region_type import RegionType
from classes.pi_subject import PISubject


class DataCreation:
    rand = random.Random()

    org_list_england = [
        Organisation(20289, "BRACE STREET HEALTH CENTRE", "M91014"),
        Organisation(20289, "BRACE STREET HEALTH CENTRE", "M91014"),
        Organisation(20147, "RANGEWAYS ROAD SURGERY", "M87041"),
        Organisation(20297, "HARDEN SURGERY", "M91022"),
        Organisation(20157, "BRIERLEY HILL HEALTH CTR A", "M87613"),
        Organisation(20157, "BRIERLEY HILL HEALTH CTR A", "M87613"),
        Organisation(14483, "ST STEPHEN'S GATE M/PRACT", "D82008"),
        Organisation(22414, "HMP BIRMINGHAM", "Y00613"),
        Organisation(13478, "THE MOIR MEDICAL CENTRE", "C81010"),
        Organisation(13494, "ADAM HOUSE MEDICAL CENTRE", "C81026"),
        Organisation(25243, "PERTH MEDICAL CENTRE", "J89999"),
        Organisation(13470, "MOSS VALLEY MEDICAL PRACTICE", "C81002"),
        Organisation(13469, "SPRINGS HEALTH CENTRE", "C81001"),
        Organisation(26099, "HMP EXETER", "Y02926"),
        Organisation(25224, "SYDNEY MEDICAL CENTRE", "J77777"),
        Organisation(19496, "MOSS LANE SURGERY", "M83015"),
    ]
    org_list_isle_of_man = [
        Organisation(10, "CASTLETOWN MEDICAL CENTRE", "Y00001"),
        Organisation(11, "PEEL GROUP PRACTICE", "Y00002"),
        Organisation(12, "RAMSEY GROUP PRACTICE", "Y00003"),
        Organisation(13, "SOUTHERN GROUP PRACTICE", "Y00004"),
        Organisation(14, "KENSINGTON GROUP PRACTICE", "Y00005"),
        Organisation(15, "PROMENADE MEDICAL CENTRE", "Y00006"),
        Organisation(16, "PALATINE GROUP PRACTICE", "Y00007"),
        Organisation(17, "HAILWOOD MEDICAL CENTRE", "Y00008"),
        Organisation(18, "BALLASALLA MEDICAL CENTRE", "Y00009"),
        Organisation(19, "LAXEY HEALTH CENTRE", "Y00010"),
        Organisation(20, "SNAEFELL SURGERY", "Y00011"),
        Organisation(21, "DRUG & ALCOHOL SERVICE (DA)", "Y00012"),
        Organisation(22, "ISLE OF MAN PRISON", "Y00013"),
    ]
    registration_code_list = [
        "G3341506",
        "G9008533",
        "G3021280",
        "G3232222",
        "G3358823",
        "G3389966",
        "G3238101",
        "G8306584",
        "G3400043",
        "G3210707",
        "G3375673",
        "G8210290",
        "G8605331",
        "G3337426",
        "G3059715",
    ]
    female_common_title_list = ["MRS", "MS", "MISS", "DR"]
    female_rare_title_list = [
        "PROF",
        "DAME",
        "LADY",
        "REV",
        "ADM",
        "COL",
        "CAPT",
        "MAJ",
        "DEAN",
        "WCOM",
        "GEN",
    ]
    male_common_title_list = ["MR", "MR", "MR", "DR"]
    male_rare_title_list = [
        "PROF",
        "REV",
        "SIR",
        "HON",
        "LORD",
        "EARL",
        "BRO",
        "FR",
        "ADM",
        "COL",
        "CAPT",
        "MAJ",
        "GEN",
    ]

    def generate_random_subject(
        self, random_words_list: Dict[str, str], pi_reference: str, region: RegionType
    ) -> PISubject:
        """
        Generates a random PI Subject with the provided random words, PI reference, and region.
        Args:
            random_words_list (Dict[str, str]): A dictionary of random words for names and addresses.
            pi_reference (str): The PI reference for the subject.
            region (RegionType): The region type (e.g., England)
        Returns:
            PISubject: A randomly generated PI Subject.
        """
        logging.info(
            f"generateRandomSubject: {random_words_list}, {pi_reference}, {region}"
        )
        pi_subject = PISubject()
        pi_subject.set_nhs_number(self.generate_random_nhs_number())
        person = self.generate_random_person(random_words_list, GenderType.NOT_KNOWN)
        pi_subject.set_family_name(person.get_surname())
        pi_subject.set_first_given_names(person.get_forename())
        pi_subject.set_other_given_names(person.get_other_forenames())
        pi_subject.set_previous_family_name(person.get_previous_surname())
        pi_subject.set_name_prefix(person.get_title())
        pi_subject.set_birth_date(
            datetime.date.today() - datetime.timedelta(days=60 * 365)
        )
        pi_subject.set_death_date(None)
        gender = person.get_gender()
        if gender is not None:
            pi_subject.set_gender_code(gender.redefined_value)
        else:
            pi_subject.set_gender_code(GenderType.NOT_KNOWN.redefined_value)
        address = self.generate_random_address(random_words_list)
        pi_subject.set_address_line1(address.get_address_line1())
        pi_subject.set_address_line2(address.get_address_line2())
        pi_subject.set_address_line3(address.get_address_line3())
        pi_subject.set_address_line4(address.get_address_line4())
        pi_subject.set_address_line5(address.get_address_line5())
        pi_subject.set_post_code(address.get_post_code())
        pi_subject.set_registration_code(self.generate_random_registration_code())
        gp_surgery = self.generate_random_gp_surgery(region)
        if gp_surgery is not None:
            pi_subject.set_gp_practice_code(gp_surgery.get_code())
        pi_subject.set_nhais_deduction_reason(None)
        pi_subject.set_nhais_deduction_date(None)
        pi_subject.set_exeter_system("ATO")
        pi_subject.set_removed_to(None)
        pi_subject.set_pi_reference(pi_reference)
        pi_subject.set_superseded_by_nhs_number(None)
        pi_subject.set_replaced_by_nhs_number(None)
        logging.info("generateRandomSubject: end")
        return pi_subject

    def generate_random_nhs_number(self) -> str:
        """
        Generates a random NHS number
        Returns:
            str: The generated NHS number
        """
        logging.info("generateRandomNHSNumber: start")
        nhs_number_base = 900000000
        nhs_number_range = 100000000
        while True:
            nhs_number = str(
                nhs_number_base + self.rand.randint(0, nhs_number_range - 1)
            )
            if self.is_valid_nhs_number(nhs_number):
                break
        nhs_number += str(self.calculate_nhs_number_checksum(nhs_number))
        logging.info("generateRandomNHSNumber: end")
        return nhs_number

    def is_valid_nhs_number(self, nhs_number: str) -> bool:
        """
        Checks if the NHS number is valid
        Retuns:
            bool: True if it is valid, False if it is not
        """
        return len(nhs_number) == 9 and nhs_number.isdigit()

    def calculate_nhs_number_checksum(self, nhs_number: str) -> int:
        """
        Calculates the NHS number checksum
        Returns:
            int: the checksum of the NHS number
        """
        digits = [int(d) for d in nhs_number]
        total = sum((10 - i) * digits[i] for i in range(9))
        remainder = total % 11
        checksum = 11 - remainder
        if checksum == 11:
            checksum = 0
        return checksum

    def generate_random_registration_code(self) -> str:
        """
        Generates a random registraction code
        Returns:
            str: The generated registration code
        """
        logging.info("generateRandomRegistrationCode: start")
        code = random.choice(self.registration_code_list)
        logging.info("generateRandomRegistrationCode: end")
        return code

    def generate_random_gp_surgery(self, region: RegionType) -> Organisation | None:
        """
        Generates a random gp surgery
        Args:
            region (RegionType): The region type (e.g., England)
        Returns:
            Organisation: The generated gp surgery
        """
        logging.info(f"generateRandomGPSurgery: {region}")
        if region == RegionType.ENGLAND:
            return random.choice(self.org_list_england)
        elif region == RegionType.ISLE_OF_MAN:
            return random.choice(self.org_list_isle_of_man)
        else:
            return None

    def generate_random_address(self, random_words_list: Dict[str, str]) -> Address:
        """
        Generates a random address
        Args:
            random_words_list (Dict[str, str]): A dictionary of random words for names and addresses.
        Returns:
            Address: The generated address
        """
        logging.info(f"generateRandomAddress: {random_words_list}")
        address = Address()
        house_number = self.rand.randint(0, 100)
        road_prefix = random_words_list.get("roadPrefix", "")
        road_suffix = random_words_list.get("roadSuffix", "")
        address.set_address_line(1, f"{house_number} {road_prefix} {road_suffix}")

        line_number = 2
        if self.rand.randint(0, 100) < 10:
            address.set_address_line(line_number, random_words_list.get("locality", ""))
            line_number += 1

        if self.rand.randint(0, 100) < 50:
            address.set_address_line(line_number, random_words_list.get("city", ""))
        else:
            address.set_address_line(line_number, random_words_list.get("town", ""))
            line_number += 1
            address.set_address_line(line_number, random_words_list.get("county", ""))

        address.set_post_code(self.generate_random_postcode())
        logging.info("generateRandomAddress: end")
        return address

    def generate_random_person(
        self, random_words_list: Dict[str, str], gender: GenderType
    ) -> Person:
        """
        Generates a random person
        Args:
            random_words_list (Dict[str, str]): A dictionary of random words for names and addresses.
            gender (GenderType): The gender of the person
        Returns:
            Person: The generated person
        """
        logging.info("generateRandomPerson: start")
        if gender not in [GenderType.MALE, GenderType.FEMALE]:
            gender = (
                GenderType.MALE if self.rand.randint(0, 100) < 50 else GenderType.FEMALE
            )

        person = Person()
        person.set_title(self.generate_random_title(gender))
        person.set_forename(random_words_list.get("forename", ""))
        person.set_surname(random_words_list.get("surname", ""))
        person.set_gender(gender)

        if self.rand.randint(0, 100) < 5:
            person.set_other_forenames(random_words_list.get("forename2", ""))
        if self.rand.randint(0, 100) < 5:
            person.set_previous_surname(random_words_list.get("surname2", ""))

        logging.info("generateRandomPerson: end")
        return person

    def generate_random_postcode(self) -> str:
        """
        Generates a random postcode
        Returns:
            str: The generated postcode
        """
        logging.info("generateRandomPostcode: start")
        unused_first_characters = ["V", "Q", "X"]
        inward_letters = [
            "A",
            "B",
            "D",
            "E",
            "F",
            "G",
            "H",
            "J",
            "L",
            "N",
            "P",
            "Q",
            "R",
            "S",
            "T",
            "U",
            "W",
            "X",
            "Y",
            "Z",
        ]
        random_outward_letters = random.choice(unused_first_characters) + random.choice(
            inward_letters
        )
        random_outward_digits = str(self.rand.randint(0, 99)).zfill(2)
        random_inward_digit = str(self.rand.randint(0, 9))
        random_inward_letter1 = random.choice(inward_letters)
        random_inward_letter2 = random.choice(inward_letters)
        postcode = f"{random_outward_letters}{random_outward_digits} {random_inward_digit}{random_inward_letter1}{random_inward_letter2}"
        logging.info("generateRandomPostcode: end")
        return postcode

    def generate_random_title(self, gender: GenderType) -> str:
        """
        Generates a random title for the person
        Args:
            gender (GenderType): The gender of the person
        Returns:
            str: The generated title
        """
        logging.info("generateRandomTitle: start")
        weighting = self.rand.randint(0, 9)
        if gender == GenderType.FEMALE:
            if weighting > 7:
                return random.choice(self.female_rare_title_list)
            else:
                return random.choice(self.female_common_title_list)
        else:
            if weighting > 7:
                return random.choice(self.male_rare_title_list)
            else:
                return random.choice(self.male_common_title_list)
